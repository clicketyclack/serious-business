#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 Erik Mossberg

This file is part of SeriousBusiness.

SeriousBusiness is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SeriousBusiness is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import base64
import pathlib

import argparse
import cherrypy
from cherrypy.lib import static as lib_static

from media_clip import MediaClip
from media_library import MediaLibrary

def media_abs_location(args):
    media_location = args.media_location
    if media_location is not None:
        media_location = os.path.abspath(media_location)
    else:
        media_location = os.path.abspath('media')
    return media_location

class SeriousServer(object):

    def __init__(self, args):
        """
        SeriousServer : A Super Basic Streaming Network Server
        """
        self._tilecon_render_cache = {}
        self._media_location = media_abs_location(args)
        self._media_library = MediaLibrary(self._media_location)

    def _header(self):
        """
        Index page header.
        """
        toreturn = """
<!doctype html><html lang=en>
<head><meta charset=utf-8>
<link rel="stylesheet" href="./static/v/video-js.css">
<link rel="stylesheet" href="./static/sbsns.css">
<title>Super Basic Streaming Network Server</title>
</head>
"""


        return toreturn


    def _footer(self):
        """
        Index page footer.
        """
        return """</html>"""


    @cherrypy.expose
    def index(self):
        segments = [self._header()]
        segments.append('<body>')
        segments.append('<h3>Super Basic Streaming Network Server</h3>')
        fnames = self._media_library.get_clip_filenames()

        for clip in self._media_library.get_clips():
            segments += self._render_tilecon(clip)

        segments.append('</body>')
        return "\n".join(segments)

    def _render_tilecon(self, clip):
        """
        Render a tile/icon to html.
        """

        if clip.get_uid() in self._tilecon_render_cache:
            return self._tilecon_render_cache[clip.get_uid()]

        fname = clip.get_filename()
        toreturn = ["<div class='tilecon'>"]
        b64key = base64.b64encode(fname.encode('ascii')).decode('ascii')

        toreturn.append("<a href='./serve_content?fkey=%s'>" % b64key)
        toreturn.append("<img class='tilecon_thumb' src='./%s' /></a>" % clip.get_thumbnail_page())
        toreturn.append("<br /><a href='./fronter?clip_uid=%s' class='tilecon_title'>" % clip.get_uid())
        toreturn.append("%s</a></div>" % (clip.get_title()))

        self._tilecon_render_cache[clip.get_uid()] = toreturn
        return toreturn


    @cherrypy.expose
    def serve_content(self, fkey):
        """
        Serves raw files. Allows b64-encoded filenames.
        """
        clearkey = None
        try:
            clearkey = base64.b64decode(fkey.encode('ascii')).decode('ascii')
            print("Clearkey is now '%s'" % clearkey)
        except Exception as ex:
            print("Key %s not b64-decodable." % fkey)


        #return serve_file(media[fkey], "application/x-download", "attachment")


        # File name MUST! be checked against a
        # whilelist, only containing content in
        # the media directory. Basic protection
        # against directory traversal.
        fname_whitelist = os.listdir(self._media_location)

        if fkey in fname_whitelist:
            fname = os.path.join(self._media_location, fkey)
            fname = os.path.abspath(fname)
            print("Statically serving '%s" % fname)
            return lib_static.serve_file(fname)

        elif clearkey is not None and clearkey in fname_whitelist:
            fname = os.path.join(self._media_location, clearkey)
            fname = os.path.abspath(fname)
            print("Statically serving '%s" % fname)
            return lib_static.serve_file(fname)

        else:
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            cherrypy.response.status=404
            return "No such fkey"

    @cherrypy.expose
    def fronter(self, clip_uid):
        """
        Return full page for a given fkey.
        """
        segments = [self._header()]
        segments.append('<body>')
        segments.append('<h3>Super Basic Streaming Network Server</h3><div class="fronted_clip"><p>')

        template = """<video id='my-video' class='video-js' controls preload='auto' width='640' height='264'
            poster='THUMBNAIL_IMAGE' data-setup='{}'>
            <source src='./serve_content?fkey=MP4_B64KEY' type='video/mp4'>
            <!-- <source src='void.webm' type='video/webm'> -->
            <p class='vjs-no-js'>
            To view this video please enable JavaScript, and consider upgrading to a web browser that supports HTML5 video.
            </p>
            </video>"""

        segments.append('</p></div>')
        segments.append("<script src='./static/v/video.js'></script>")
        segments.append('</body>')

        thumbnail_image = clip_uid
        mp4_filename = clip_uid
        mp4_b64key = clip_uid

        clips = self._media_library.get_clips()
        for clip in clips:
            if clip.get_uid() == clip_uid:
                thumbnail_image = clip.get_thumbnail_page()
                mp4_filename = clip.get_filename()
                mp4_b64key = base64.b64encode(mp4_filename.encode('ascii')).decode('ascii')

        render = template.replace('THUMBNAIL_IMAGE', thumbnail_image).replace('MP4_B64KEY', mp4_b64key)
        segments += [render]
        segments += [self._footer()]
        return "\n".join(segments)


PATH = os.path.abspath('./static')

class Static:

    @cherrypy.expose
    def index(self):
        return """Index."""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serious Business simple media server.')
    parser.add_argument('-m', '--media-location',
                        help='Path to media content.')
    parser.add_argument('-a', '--assets-location',
                        help='Path to static assets.')
    args = parser.parse_args()

    conf_static = {
        '/': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': PATH,
            },
    }

    conf_global = {'server.socket_port': 8080,
                   'server.socket_host': '0.0.0.0' }
    cherrypy.config.update(conf_global)

    cherrypy.tree.mount(SeriousServer(args), '/') #, blog_conf)
    cherrypy.tree.mount(Static(), '/static', conf_static)

    cherrypy.engine.start()
    cherrypy.engine.block()

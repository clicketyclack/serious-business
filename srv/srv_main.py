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

import cherrypy
from cherrypy.lib import static as lib_static

class SeriousServer(object):

    def _header(self):
        """
        Index page header.
        """
        toreturn = """
<!doctype html><html lang=en>
<head><meta charset=utf-8>
<link rel="stylesheet" href="./static?sbsns.css">
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
        fnames = os.listdir('media')

        for fname in fnames:
            segments += self._render_tilecon(fname)

        segments.append('</body>')
        return "\n".join(segments)

    def _render_tilecon(self, media_id):
        """
        Render a tile/icon to html.
        """
        fname = media_id
        toreturn = ["<div class='tilecon'>"]
        b64key = base64.b64encode(fname.encode('ascii')).decode('ascii')

        toreturn.append("<a href='./serve_content?fkey=%s'>" % b64key)
        toreturn.append("<img class='tilecon_thumb' src='./static?missing_media.jpg' /></a>")
        toreturn.append("<br /><a href='./serve_content?fkey=%s' class='tilecon_title'>" % b64key)
        toreturn.append("%s</a></div>" % (fname))

        return toreturn

    @cherrypy.expose
    def static(self, **argv):
        """
        Serve a directory from the static directory.
        """

        directory_name = "static"
        fname_whitelist = [str(p) for p in pathlib.Path(directory_name).rglob("*")]
        fname_whitelist = [s[len(directory_name):].strip(os.sep) for s in fname_whitelist]



        fname = None
        try:
            fname = list(argv)[0]
            if fname in fname_whitelist:
                fname = os.path.join(directory_name, fname)
                fname = os.path.abspath(fname)

                if os.path.isfile(fname):
                    print("Statically serving '%s" % fname)
                    return lib_static.serve_file(fname)
            else:
                raise Exception("No file resolvable for argv '%s'" % (argv))

        except Exception as ex:
            print("Static request for '%s' failed with exception '%s'." % (fname, str(ex)))
            return lib_static.serve_file(os.path.abspath('static/missing_media.jpg'))

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
        fname_whitelist = os.listdir('media')

        if fkey in fname_whitelist:
            fname = os.path.join('media', fkey)
            fname = os.path.abspath(fname)
            print("Statically serving '%s" % fname)
            return lib_static.serve_file(fname)

        elif clearkey is not None and clearkey in fname_whitelist:
            fname = os.path.join('media', clearkey)
            fname = os.path.abspath(fname)
            print("Statically serving '%s" % fname)
            return lib_static.serve_file(fname)

        else:
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            cherrypy.response.status=404
            return "No such fkey"


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(SeriousServer())

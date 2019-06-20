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

import cherrypy

class SeriousServer(object):
    @cherrypy.expose
    def index(self):
        toreturn = "A serious serving of cherrypy!<br>"

        fnames = os.listdir('media')

        for fname in fnames:
            b64key = base64.b64encode(fname.encode('ascii')).decode('ascii')
            toreturn += "<a href='./serve_content?fkey=%s'>%s</a><br>" % (b64key, fname)
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

        from cherrypy.lib.static import serve_file
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
            return serve_file(fname)

        elif clearkey is not None and clearkey in fname_whitelist:
            fname = os.path.join('media', clearkey)
            fname = os.path.abspath(fname)
            print("Statically serving '%s" % fname)
            return serve_file(fname)

        else:
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            cherrypy.response.status=404
            return "No such fkey"


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(SeriousServer())

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

        files = os.listdir('media')
        for fname in files:
            b64key = base64.b64encode(fname.encode('ascii')).decode('ascii')
            toreturn += "%s %s<br>" % (fname, b64key)
        return toreturn

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(SeriousServer())

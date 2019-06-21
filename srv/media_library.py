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

import unittest
import pathlib
import os
import json

from media_clip import MediaClip


class MediaLibrary(object):
    def __init__(self, directory_name):
        """
        Represents a library based on a filesystem directory.
        """
        self._directory_name = directory_name
        self._clips = None
        self.discover()

    def discover(self):
        """
        Traverse directory and re-populate any media clips.
        """

        fname_whitelist = [str(p) for p in pathlib.Path(self._directory_name).rglob("*")]
        fname_whitelist = [s[len(self._directory_name):].strip(os.sep) for s in fname_whitelist]
        self._fname_whitelist = fname_whitelist
        clips = []
        for fname in self._fname_whitelist:
            if fname.endswith('.mp4'):
                clip = MediaClip(fname, fname, fname, 'missing_media.jpg')
                clips.append(clip)

        self._clips = clips


    def get_clip_filenames(self):
        """
        Get filenames of media library.
        """
        toreturn = []
        for clip in self._clips:
            filename = clip.get_filename()
            if filename is not None:
                toreturn.append(filename)

        return toreturn


    def get_clips(self):
        return self._clips


class TestMediaLibrary(unittest.TestCase):


    def test_discover(self):
        ml = MediaLibrary('../media')
        clips = ml.get_clips()
        self.assertTrue(len(clips) > 0)


if __name__ == '__main__':
    unittest.main()

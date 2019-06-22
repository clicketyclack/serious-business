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

class MediaClip():
    def __init__(self, uid, filename, title, thumbnail_filename):
        """
        Simple media item.
        """
        self._filename = self._sanitize_string_chs(filename)
        self._uid = self._sanitize_string_chs(uid)
        self._title = self._sanitize_string_chs(title)
        self._thumbnail_filename = self._sanitize_string_chs(thumbnail_filename)


    def infer_thumbnail(self, thumbs_directory=None):
        """
        Make an attempt at inferring a thumbnail.

        Useful for the following cases:
         - We don't have a metadata json, but the thumbnail has the same
           name as the media file, with a different extension.
         - Clip is audio only, but there is only one jpg in the
           directory (i.e. podcasts, albums).
        """
        if True: #thumbs_directory:
            whitelist = []
            whitelist += [str(p) for p in pathlib.Path(thumbs_directory).rglob("*jpg")]
            whitelist += [str(p) for p in pathlib.Path(thumbs_directory).rglob("*jpeg")]
            whitelist += [str(p) for p in pathlib.Path(thumbs_directory).rglob("*png")]
            whitelist += [str(p) for p in pathlib.Path(thumbs_directory).rglob("*gif")]

            whitelist = [os.path.basename(p) for p in whitelist]

            if len(whitelist) == 1:
                return whitelist[0]

            base, _ = os.path.splitext(self._filename)

            candidates = ['%s.jpg' % base, '%s.jpeg' % base, '%s.png' % base, '%s.gif' % base]
            for candidate in candidates:
                if candidate in whitelist:
                    print("Inferred thumbnail %s for base %s" % (candidate, base))
                    self._thumbnail_filename = candidate
                    return

            print("Could not infer thumbnail for media filename %s, whitelist is '%s' " % (self._filename, whitelist))

    def _sanitize_string_chs(self, string):
        """
        Sanitize chars from any filename string.

        Returns string if the string is ok. Ok means:
         - All characters are in the basic ascii printable subset.
         - No character is a directory delimiter.
         - No character is a <, > or & for html reasons.
         - Length greater than 0.

        Returns None if the passed argument is None.

        Otherwise throws an exception.
        """
        if string is None:
            return None

        if len(string) == 0:
            raise TypeError("Validation failed, got empty string.")

        valid_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -_.}[]{()#|"
        for ch in string:
            if ch not in valid_chars:
                raise TypeError("Validation failed, got invalid char '%s' for string '%s'" % (ch, string))

        return string

    def get_uid(self):
        """
        Media UID.
        """
        return self._uid

    def get_thumbnail_page(self):
        """
        Return a thumbnail picture filename. Fallback to missing media image, useful for raw clips without metadata.
        """
        if self._thumbnail_filename is None:
            return 'static?missing_media.jpg'
        return "serve_content?fkey=%s" % self._thumbnail_filename

    def get_thumbnail_filename(self):
        """
        Return a thumbnail picture filename. Fallback to missing media image, useful for raw clips without metadata.
        """
        if self._thumbnail_filename is None:
            return 'missing_media.jpg'
        return self._thumbnail_filename

    def get_title(self):
        """
        Return a printable title. Fallback to filename, useful for raw clips without metadata.
        """
        if self._title is None:
            return self.get_filename()
        return self._title

    def get_filename(self):
        """
        Filename of clip.
        """
        if self._filename is None:
            return 'MISSING FILE'

        return self._filename


class TestMediaClip(unittest.TestCase):


    def test_get_thumbnail(self):
        try:
            _ = MediaClip('foo', 'foo', 'foo', 'foo/x.jpg')
            self.fail("Media clip failed to reject thumbnail filename with path separator.")
        except TypeError:
            pass

        clip_exists = MediaClip('foo', 'foo', 'foo', 'foo.jpg')
        clip_missing = MediaClip('foo', 'foo', 'foo', None)
        self.assertEqual(clip_exists.get_thumbnail_filename(), 'foo.jpg')
        self.assertEqual(clip_missing.get_thumbnail_filename(), 'missing_media.jpg')
        self.assertEqual(clip_exists.get_thumbnail_page(), 'serve_content?fkey=foo.jpg')
        self.assertEqual(clip_missing.get_thumbnail_page(), 'static?missing_media.jpg')


    def test_sanitization(self):
        """
        Catch attempts at putting html in title.
        """
        _ = MediaClip('foo', 'foo', 'foo', 'foo.jpg')

        try:
            _ = MediaClip('foo', 'foo', 'fo<o', 'foo.jpg')
            self.fail("Media clip failed to reject thumbnail filename with html-ish content.")
        except TypeError:
            pass

        try:
            _ = MediaClip('foo', 'foo', 'fo&o', 'foo.jpg')
            self.fail("Media clip failed to reject thumbnail filename with html-ish content.")
        except TypeError:
            pass

    def test_infer_thumb(self):
        """
        landscape_thumb.mp4 -> landscape_thumb.png
        """

        fname = 'landscape_thumb.mp4'
        clip = MediaClip(fname, fname, fname, None)
        self.assertEqual(clip.get_thumbnail_page(), 'static?missing_media.jpg')
        clip.infer_thumbnail('../srv')
        self.assertEqual(clip.get_thumbnail_page(), 'static?missing_media.jpg')
        clip.infer_thumbnail('../media')
        self.assertEqual(clip.get_thumbnail_page(), 'serve_content?fkey=landscape_thumb.png')

if __name__ == '__main__':
    unittest.main()

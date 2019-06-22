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

    def _discover_jsons(self):
        """
        Helper function that discoveres media via json metafiles.
        """
        clips = []

        jsons = [str(p) for p in pathlib.Path(self._directory_name).rglob("*.json")]
        jsons = [s[len(self._directory_name):].strip(os.sep) for s in jsons]

        print(jsons)
        for json_fname in jsons:
            json_fname_abspath = os.path.abspath(os.path.join(self._directory_name, json_fname))
            clip = None
            with open(json_fname_abspath) as json_file:
                json_str = json_file.read()
                try:
                    clip = self._clip_from_json(json_str)
                except json.decoder.JSONDecodeError:
                    print("Failed to read json from file '%s'" % json_fname_abspath)

            if clip is not None:
                clips.append(clip)

        return clips

    def _clip_from_json(self, json_str):
        """
        Given a string of json, return a media clip.

        Return None is loading / parsing json fails.
        """

        json_obj = json.loads(json_str)
        keys = list(json_obj)
        print("Got %d keys worth of json." % len(keys))

        uid = None
        filename = None
        title = None
        thumbnail_filename = None

        for key in json_obj:
            val = json_obj[key]

            if key.startswith('_'):
                key = key.lstrip('_')

            if key == 'id' or key == 'uid':
                if type(val) == str:
                    uid = val

            if key == 'filename':
                if type(val) == str:
                    filename = val

            if key == 'title':
                if type(val) == str:
                    try:
                        title = MediaClip.sanitize_string_chs(val)
                    except TypeError:
                        # title contains invalid chars.
                        alternate = MediaClip.censor_string_chs(val)
                        if len(alternate) > 5:
                            print("Title '%s has alternate '%s'" % (val, alternate) )
                            title = alternate


            # Thumbnail must have image-ish file extension.
            if key in ['thumbnail_filename', 'thumbnail']:
                if type(val) == str and '.' in val:
                    _, ext = os.path.splitext(val)
                    if ext in ['.jpg', '.jpeg', '.png', 'gif']:
                        try:
                            # Check if thumbnail filename is in any way
                            # 'dangerous'. Admittedly there is low
                            # risk that someone would inject
                            # directory traversal or html escapes
                            # via metadata. But still...
                            MediaClip.sanitize_string_chs(val)
                            thumbnail_filename = val
                        except TypeError:
                            # Thumbnail contains invalid chars.
                            pass

        if filename is None:
            print("Failed to extract filename from json keys %s" % keys)
            return
            
        clip = None
        try:
            clip = MediaClip(uid, filename, title, thumbnail_filename)
            if thumbnail_filename is None:
                clip.infer_thumbnail(self._directory_name)
        except TypeError as err:
            # If filename is valid, _discover_raws will catch this clip.
            print("Failed to create clip for filename '%s'" % str(filename))

        return clip


    def _discover_raws(self, already_claimed=[]):
        """
        Helper function that discoveres media via raw metafiles.
        """

        fname_whitelist = [str(p) for p in pathlib.Path(self._directory_name).rglob("*")]
        fname_whitelist = [s[len(self._directory_name):].strip(os.sep) for s in fname_whitelist]
        self._fname_whitelist = fname_whitelist
        clips = []
        for fname in self._fname_whitelist:
            if fname in already_claimed:
                continue

            if fname.endswith('.mp4'):
                clip = MediaClip(fname, fname, fname, None)
                clips.append(clip)
                clip.infer_thumbnail(self._directory_name)

        return clips

    def discover(self):
        """
        Traverse directory and re-populate any media clips.
        """
        clips = []
        clips += self._discover_jsons()

        already_claimed = []
        for clip in clips:
            already_claimed.append(clip.get_filename())

        clips += self._discover_raws(already_claimed)

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


    def test_discover_thumbnails(self):
        ml = MediaLibrary('../media')
        clips = ml.get_clips()
        landscape_clips = [c for c in clips if 'andsca' in c.get_title()]
        self.assertEqual(len(landscape_clips), 1)

        thumb = landscape_clips[0].get_thumbnail_page()
        self.assertTrue(thumb.endswith('thumb.png'))

if __name__ == '__main__':
    unittest.main()

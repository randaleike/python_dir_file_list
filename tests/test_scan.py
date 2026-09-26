#!/usr/bin/python
"""@package dirscan_grocsoftware
@brief Directory/file scanning utilities
"""
#==========================================================================
#Copyright (c) 2020 Randal Eike
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#==========================================================================

import os
import tempfile
import unittest
import io

from contextlib import redirect_stdout

from src.dirscan_grocsoftware import scan


class DirectoryListTests(unittest.TestCase):
    '''
    @brief Unit tests for DirectoryList
    '''
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = self.tempdir.name
        self.nested = os.path.join(self.root, "nested")
        os.makedirs(self.nested)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_recurse_includes_root_and_nested_directories(self):
        '''
        @brief Test that the recursive directory list includes both the root and nested directories
        '''
        directories = scan.DirectoryList(self.root).get_list(recurse=True)

        self.assertCountEqual(directories, [self.root, self.nested])
        self.assertEqual(len(directories), 2)

    def test_non_recursive_list_contains_only_base_directory(self):
        '''
        @brief Test that the non-recursive directory list contains only the base directory
        '''
        directories = scan.DirectoryList(self.root).get_list(recurse=False)

        self.assertEqual(directories, [self.root])

    def test_non_recursive_list_cwd__directory(self):
        '''
        @brief Test that the non-recursive directory list contains only the
               cwd base directory
        '''
        directories = scan.DirectoryList().get_list(recurse=False)

        self.assertEqual(directories, [os.path.abspath(os.getcwd())])

    def test_string_representation(self):
        '''
        @brief Test the string representation of the DirectoryList object
        '''
        dirlist = scan.DirectoryList()
        dirlist.get_list(recurse=False)
        expected = os.path.abspath(os.getcwd())
        #print(str(dirlist))
        self.assertIn(str(expected),str(dirlist))


class FileListTests(unittest.TestCase):
    '''
    @brief Unit tests for FileList
    '''
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = self.tempdir.name
        self.nested = os.path.join(self.root, "nested")
        os.makedirs(self.nested)

        self.root_txt = os.path.join(self.root, "root.txt")
        self.child_txt = os.path.join(self.nested, "child.txt")
        self.child_md = os.path.join(self.nested, "child.md")

        with open(self.root_txt, "w", encoding="utf-8") as file_obj:
            file_obj.write("root")
        with open(self.child_txt, "w", encoding="utf-8") as file_obj:
            file_obj.write("child")
        with open(self.child_md, "w", encoding="utf-8") as file_obj:
            file_obj.write("ignore")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_collects_matching_files_from_nested_directories(self):
        '''
        @brief Test that the FileList collects matching files from nested directories
        '''
        files = scan.FileList(ext_filter="txt").get_list([self.root])
        normalized = {os.path.normcase(path) for path in files}

        self.assertSetEqual(
            normalized,
            {
                os.path.normcase(self.root_txt),
                os.path.normcase(self.child_txt),
            },
        )

    def test_deduplicates_overlapping_directories(self):
        '''
        @brief Test that the FileList deduplicates files when directories overlap
        '''
        files = scan.FileList(ext_filter="txt").get_list(
            [self.root, self.root, self.nested]
        )
        normalized = {os.path.normcase(path) for path in files}

        self.assertEqual(len(files), 2)
        self.assertSetEqual(
            normalized,
            {
                os.path.normcase(self.root_txt),
                os.path.normcase(self.child_txt),
            },
        )

    def test_filters_by_base_name_and_extension(self):
        '''
        @brief Test that the FileList filters files by both base name and extension
        '''
        files = scan.FileList(base_name_filter="^child", ext_filter="txt").get_list(
            [self.root]
        )

        self.assertEqual(files, [self.child_txt])

    def test_filters_by_base_name_only(self):
        '''
        @brief Test that the FileList filters files by base name only
        '''
        files = scan.FileList(base_name_filter="^child").get_list(
            [self.root]
        )

        self.assertEqual(len(files), 2)
        self.assertIn(self.child_txt, files)
        self.assertIn(self.child_md, files)

    def test_string_representation_contains_matching_paths(self):
        '''
        @brief Test that the string representation of the FileList contains the matching file paths
        '''
        file_list = scan.FileList(ext_filter="txt")
        file_list.get_list([self.root])

        self.assertIn(self.root_txt, str(file_list))
        self.assertIn(self.child_txt, str(file_list))
        self.assertNotIn(self.child_md, str(file_list))


class ScanfileTests(unittest.TestCase):
    '''
    @brief Unit tests for the directory and file scanning utilities
    '''
    def setUp(self):
        '''
        @brief Set up the temporary directory structure for testing
        '''
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = self.tempdir.name
        self.nested = os.path.join(self.root, "nested")
        os.makedirs(self.nested)

        self.root_txt = os.path.join(self.root, "root.txt")
        self.child_txt = os.path.join(self.nested, "child.txt")
        self.child_md = os.path.join(self.nested, "child.md")

        with open(self.root_txt, "w", encoding="utf-8") as file_obj:
            file_obj.write("root")
        with open(self.child_txt, "w", encoding="utf-8") as file_obj:
            file_obj.write("child")
        with open(self.child_md, "w", encoding="utf-8") as file_obj:
            file_obj.write("ignore")

    def tearDown(self):
        '''
        @brief Clean up the temporary directory structure after testing
        '''
        self.tempdir.cleanup()

    def test_scanfiles_get_file_list_returns_expected_results(self):
        '''
        @brief Test that Scanfiles.get_file_list returns the expected results for txt files
        '''
        scanner = scan.Scanfiles(start_directory=self.root, ext_filter="txt")
        files = scanner.get_file_list(recurse=True)

        self.assertEqual(len(files), 2)
        self.assertSetEqual(
            {os.path.normcase(path) for path in files},
            {
                os.path.normcase(self.root_txt),
                os.path.normcase(self.child_txt),
            },
        )
        self.assertNotIn(self.child_md, files)

    def test_scanfiles_logs_directory_list(self):
        '''
        @brief Test that Scanfiles logs the directory list correctly
        '''
        scanner = scan.Scanfiles(start_directory=self.root, ext_filter="txt")
        scanner.get_file_list(recurse=True)

        with io.StringIO() as buf, redirect_stdout(buf):
            scanner.log_dir_list()
            output = buf.getvalue()
        self.assertIn(self.root, output)
        self.assertIn(self.nested, output)


    def test_scanfiles_logs_file_list(self):
        '''
        @brief Test that Scanfiles logs the file list correctly
        '''
        scanner = scan.Scanfiles(start_directory=self.root, ext_filter="txt")
        scanner.get_file_list(recurse=True)

        with io.StringIO() as buf, redirect_stdout(buf):
            scanner.log_file_list()
            output = buf.getvalue()
        self.assertIn(self.root_txt, output)
        self.assertIn(self.child_txt, output)
        self.assertNotIn(self.child_md, output)

if __name__ == "__main__":
    unittest.main()

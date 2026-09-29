#!/usr/bin/python
"""@package dirscan_grocsoftware
@brief Directory/file scanning utilities
"""
#==========================================================================
# Copyright (c) 2020 Randal Eike
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

import re
import os
from pathlib import Path

class DirectoryList(object):
    '''
    @brief Create a list of sub-directories from a base directory

    This class with scan the file system and create a list of sub-directories
    from a base directory
    '''

    def __init__(self, base_directory=None):
        '''
        @brief Initialize the DirectoryList object
        @param base_directory The base directory to start scanning from
        '''
        if base_directory is None:
            self._base_dir = os.path.abspath(os.getcwd())
        else:
            self._base_dir = os.path.abspath(base_directory)

        self._subdir_list = []

    def _get_subdirectory_list(self, start_directory: str, recurse: bool):
        '''
        @brief Recursively get the list of subdirectories starting from start_directory
        @param start_directory:string The directory to start scanning from
        @param recurse:boolean Whether to recurse into subdirectories
        '''
        #print ("start: "+start_directory)
        self._subdir_list.append(start_directory)
        dirs = os.listdir(start_directory)
        for entry in dirs:
            if not os.path.isdir(os.path.join(start_directory, entry)):
                continue
            else:
                full_sub_dir = os.path.abspath(os.path.join(start_directory, entry))
                self._subdir_list.append(full_sub_dir)
                if recurse:
                    self._get_subdirectory_list(full_sub_dir, recurse)

    def __str__(self):
        '''
        @brief Return the list of subdirectories as a string
        @return string: A string representation of the list of subdirectories
        '''
        retstr=""
        prepend = "["
        for subdir in self._subdir_list:
            retstr += prepend + subdir
            prepend = ",\n"
        retstr += "]"
        return retstr

    def _scan_subdirectory_list(self, recurse: bool = True):
        '''
        @brief Scan the subdirectory list starting from the base directory
        @param recurse:boolean Whether to recurse into subdirectories
        '''
        del self._subdir_list[:]
        self._get_subdirectory_list(self._base_dir, recurse)
        self._subdir_list = list(dict.fromkeys(self._subdir_list))

    def get_list(self, recurse: bool = True):
        '''
        @brief Get the list of subdirectories starting from the base directory
        @param recurse:boolean Whether to recurse into subdirectories
        @return list: A list of subdirectories
        '''
        self._scan_subdirectory_list(recurse)
        return self._subdir_list

class FileList(object):
    '''
    @brief Create a list of files in a list of directories

    This class with scan the file system and create a list of files
    contained within a list of directories
    '''

    def __init__(self, base_name_filter = None, ext_filter = None):
        '''
        @brief Initialize the file_list object with optional base name and extension filters
        @param base_name_filter:string A regular expression to filter the base names of files
        @param ext_filter:string A regular expression to filter the file extensions
        '''
        self._file_list = []
        if base_name_filter is not None:
            self._base_name_filter = base_name_filter
        else:
            self._base_name_filter = r'^[\w,\s-]+'

        if ext_filter is not None:
            self._ext_filter = ext_filter
        else:
            self._ext_filter = r'[A-Za-z0-9]{0,3}'
        self._name_match = self._base_name_filter + r'\.' + self._ext_filter


    def _is_match(self, test_file_name:str):
        '''
        @brief Check if the given file name matches the base name and extension filters
        @param test_file_name:string The name of the file to check
        @return bool: True if the file name matches the filters, False otherwise
        '''
        base_name = os.path.basename(test_file_name)
        if re.match(self._name_match,base_name) is None:
            return False
        else:
            return True

    def _get_file_list(self, file_dir: str):
        '''
        @brief Get the list of files in the specified directory that match the filters
        @param file_dir:string The directory to scan for files
        '''
        for root, _, files in os.walk(file_dir):
            for filename in files:
                if self._is_match(filename):
                    self._file_list.append(os.path.join(root, filename))

    def __str__(self):
        '''
        @brief Get a string representation of the file list
        @return string: The string representation of the file list
        '''
        retstr=""
        prepend = "["
        for filename in self._file_list:
            retstr += prepend + filename
            prepend = ",\n"
        retstr += "]"
        return retstr


    def get_list(self, dir_list):
        '''
        @brief Get the list of files from the specified directories that match the filters
        @param dir_list:list A list of directories to scan for files
        @return list: The list of matching files
        '''
        del self._file_list[:]
        seen_dirs = set()
        for current_dir in dir_list:
            normalized_dir = os.path.normcase(os.path.abspath(current_dir))
            if normalized_dir in seen_dirs:
                continue
            seen_dirs.add(normalized_dir)
            self._get_file_list(current_dir)
        self._file_list = list(dict.fromkeys(self._file_list))
        return self._file_list

class Scanfiles(object):
    '''
    @brief Scan the folder and sub-folders for matching files

    This class will scan the folder and sub-folders for files that match
    the input filter.
    '''

    def __init__(self, start_directory=None, base_name_filter=None, ext_filter=None):
        '''
        @brief Initialize the Scanfiles object with the starting directory and filters
        @param start_directory:string The starting directory for the scan
        @param base_name_filter:string A regular expression to filter the base names of files
        @param ext_filter:string The extension filter for files
        '''
        self._dir_list = DirectoryList(start_directory)
        self._file_list = FileList(base_name_filter, ext_filter)

    def log_dir_list(self):
        '''
        @brief Log the contents of the directory list with a header
        '''
        print("Directory List:")
        print(str(self._dir_list))

    def log_file_list(self):
        '''
        @brief Log the contents of the file list with a header
        '''
        print("File List:")
        print(str(self._file_list))

    def get_file_list(self, recurse: bool = False):
        '''
        @brief Get the list of files from the starting directory and sub-directories that match the filters
        @param recurse:bool Whether to recursively scan sub-directories
        @return list: The list of matching files
        '''
        dir_list = self._dir_list.get_list(recurse)
        ret_file_list = self._file_list.get_list(dir_list)
        return ret_file_list

class DuplicateDirectoryTree(DirectoryList):
    '''
    @brief Class to duplicate a directory tree from an old root to a new root
    '''

    def __init__(self, new_root: str, old_root: str = None):
        '''
        @brief Initialize the DuplicateDirectoryTree object with the starting directory
        @param new_root:string New root directory for the duplicate directory tree
        @param old_root:string The old root directory for comparison
        '''
        super().__init__(old_root)
        if not os.path.isdir(new_root):
            raise ValueError(f"New root directory does not exist: {new_root}")
        self._new_root = Path(new_root).resolve()

    def _make_new_dir(self, new_dir: str) -> bool:
        '''
        @brief Create the new directory if it does not exist
        @param new_dir:string The path of the new directory to create
        '''
        new_path = Path(new_dir)
        if not new_path.exists():
            new_path.mkdir(parents=True, exist_ok=True)
        return new_path.is_dir()

    def duplicate_tree(self, recurse: bool = False):
        '''
        @brief Get the list of directories from the old root and duplicate them in the new root
        @param recurse:bool Whether to recursively scan sub-directories
        @return list: The list of duplicate directories
        '''
        all_dirs = self.get_list(recurse)
        for old_dir in all_dirs:
            relative_path = os.path.relpath(old_dir, self._base_dir)
            new_directory = os.path.join(self._new_root, relative_path)

            if not self._make_new_dir(str(new_directory)):
                raise RuntimeError(f"Failed to create directory: {relative_path}")

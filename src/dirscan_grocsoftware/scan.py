#!/usr/bin/python
'''
@package MP4_Convert
'''
''' 
Copyright (c) 2020 Randal Eike
 
 Permission is hereby granted, free of charge, to any person obtaining a 
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY  
 CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
 TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

# Import 
import re, sys, os

class DirectoryList(object):
    '''
    @brief Create a list of sub-directories from a base directory

    This class with scan the file system and create a list of sub-directories
    from a base directory
    '''

    def __init__(self, baseDir=None):
        if (baseDir is not None):
            self.__baseDir = os.path.abspath(baseDir)
        else:
            self.__baseDir = os.path.getcwd()

        self.__subdirs = []

    def __getSubdirList(self, startingDir, recurse):
        #print ("start: "+startingDir)
        self.__subdirs.append(startingDir)
        for root, dirs, files in os.walk(startingDir):
            if (len(dirs) > 0):
                for subdir in dirs:
                    fullSubdir = os.path.abspath(os.path.join(startingDir, subdir))
                    self.__getSubdirList(fullSubdir, True)

    def __str__(self):
        return str(self.__subdirs)

    def __scanSubDirsList(self, recurse = True):
        del self.__subdirs[:]
        if (recurse):
            print ("Recursing")
            self.__getSubdirList(self.__baseDir, True)
        else:
            self.__subdirs.append(self.__baseDir)
        self.__subdirs = list(dict.fromkeys(self.__subdirs))

    
    def getList(self, recurse = True):
        self.__scanSubDirsList(recurse)
        return self.__subdirs

class FileList(object):
    '''
    @brief Create a list of files in a list of directories

    This class with scan the file system and create a list of files
    contained within a list of directories
    '''
    
    def __init__(self, baseNameFilter=None, extFilter = None):
        self.__fileList = []
        if (baseNameFilter is not None):
            self.__baseNameFilter = baseNameFilter
        else:
            self.__baseNameFilter = r'^[\w,\s-]+'

        if (extFilter is not None):
            self.__extFilter = extFilter
        else:
            self.__extFilter = r'[A-Za-z0-9]{0,3}'
        self.__nameMatch = self.__baseNameFilter + r'\.' + self.__extFilter


    def __isMatch(self, fileName):
        baseName = os.path.basename(fileName)
        if (re.match(self.__nameMatch,baseName) is None): 
            return False
        else:
            return True

    def __getFileList(self, dir):
        for root, dirs, files in os.walk(dir):
            for filename in files:
                if (self.__isMatch(filename)):
                    self.__fileList.append(os.path.join(root, filename))

    def __str__(self):
        return str(self.__fileList)

        
    def getList(self, dirList):
        del self.__fileList[:]
        seenDirs = set()
        for dir in dirList:
            normalizedDir = os.path.normcase(os.path.abspath(dir))
            if normalizedDir in seenDirs:
                continue
            seenDirs.add(normalizedDir)
            self.__getFileList(dir)
        self.__fileList = list(dict.fromkeys(self.__fileList))
        return self.__fileList

class Scanfiles(object):
    '''
    @brief Scan the folder and sub-folders for matching files

    This class will scan the folder and sub-folders for files that match 
    the input filter.
    '''

    def __init__(self, startingDir=None, baseNameFilter=None, extFilter=None):
        self.__dirList = DirectoryList(startingDir)
        self.__fileList = FileList(baseNameFilter, extFilter)
        self.debug = True

    def __logList(self, header, list):
        if (self.debug):
            print (header)
            if (len(list) > 0):
                for entry in list:
                    print (entry)
            else:
                print("Empty")

    def getFileList(self, recurse = False):
        dirList = self.__dirList.getList(recurse)
        self.__logList("Directory List:", dirList)
        fileList = self.__fileList.getList(dirList)
        self.__logList("File List:", fileList)
        return fileList


def main():
    scanner = Scanfiles(startingDir="/mnt/raid5/MakeMKV", extFilter='mkv')
    filelist = scanner.getFileList(True)
    print (filelist)

if __name__ == '__main__':
    main()

    

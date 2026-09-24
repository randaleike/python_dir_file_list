import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from dirscan_grocsoftware import scan


class ScanfileTests(unittest.TestCase):
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

    def test_directory_list_recurse_includes_root_and_nested_dirs(self):
        directories = scan.DirectoryList(self.root).getList(recurse=True)

        self.assertIn(self.root, directories)
        self.assertIn(self.nested, directories)

    def test_file_list_collects_matching_files_from_nested_directories(self):
        files = scan.FileList(extFilter="txt").getList([self.root])
        normalized = {os.path.normcase(path) for path in files}

        self.assertSetEqual(
            normalized,
            {
                os.path.normcase(self.root_txt),
                os.path.normcase(self.child_txt),
            },
        )

    def test_scanfiles_get_file_list_returns_expected_results(self):
        scanner = scan.Scanfiles(startingDir=self.root, extFilter="txt")
        files = scanner.getFileList(recurse=True)

        self.assertEqual(len(files), 2)
        self.assertSetEqual(
            {os.path.normcase(path) for path in files},
            {
                os.path.normcase(self.root_txt),
                os.path.normcase(self.child_txt),
            },
        )
        self.assertNotIn(self.child_md, files)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for DriveMounter backend.
"""

import unittest
from drivemounter.backend.parser import parse_share_input, ShareParseError
from drivemounter.config import WINDOWS_DRIVE_LETTERS

class TestParser(unittest.TestCase):
    def test_windows_unc_smb(self):
        res = parse_share_input(r"\\192.168.1.100\dane")
        self.assertEqual(res["protocol"], "smb")
        self.assertEqual(res["host"], "192.168.1.100")
        self.assertEqual(res["share"], "dane")
        self.assertEqual(res["canonical_uri"], "smb://192.168.1.100/dane")

    def test_windows_unc_nested(self):
        res = parse_share_input(r"\\nas\storage\subfolder")
        self.assertEqual(res["protocol"], "smb")
        self.assertEqual(res["host"], "nas")
        self.assertEqual(res["share"], "storage/subfolder")

    def test_nfs_colon_format(self):
        res = parse_share_input("192.168.1.50:/volume1/nfs_export")
        self.assertEqual(res["protocol"], "nfs")
        self.assertEqual(res["host"], "192.168.1.50")
        self.assertEqual(res["share"], "/volume1/nfs_export")

    def test_nfs_uri(self):
        res = parse_share_input("nfs://nas-server/export")
        self.assertEqual(res["protocol"], "nfs")
        self.assertEqual(res["host"], "nas-server")
        self.assertEqual(res["share"], "/export")

    def test_webdav_https(self):
        res = parse_share_input("https://nextcloud.example.com/remote.php/dav/files/admin/")
        self.assertEqual(res["protocol"], "webdav")
        self.assertEqual(res["host"], "nextcloud.example.com")
        self.assertTrue(res["is_ssl"])
        self.assertTrue(res["canonical_uri"].startswith("davs://"))

    def test_drive_letters_order(self):
        self.assertEqual(WINDOWS_DRIVE_LETTERS[0], "Z:")
        self.assertEqual(WINDOWS_DRIVE_LETTERS[1], "Y:")
        self.assertEqual(WINDOWS_DRIVE_LETTERS[-1], "D:")

if __name__ == "__main__":
    unittest.main()

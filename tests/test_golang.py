#!/usr/bin/env python

"""
Tests in-toto golang implementation against other implementations.
"""

import os
import subprocess
import unittest
from shutil import move, rmtree

from .common import CliTestCase, TmpDirMixin


class TestGolang(CliTestCase, TmpDirMixin):
    """
    Test in-toto golang implementation.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.set_up_test_dir()

        cls.keys_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "keys"
        )
        cls.scripts_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "scripts"
        )

        cls.owner_key = os.path.join(cls.keys_dir, "alice")
        cls.owner_pub = os.path.join(cls.keys_dir, "alice.pub")
        cls.bob_key = os.path.join(cls.keys_dir, "bob")
        cls.bob_pub = os.path.join(cls.keys_dir, "bob.pub")
        cls.carl_key = os.path.join(cls.keys_dir, "carl")
        cls.carl_pub = os.path.join(cls.keys_dir, "carl.pub")

        cls.create_layout = os.path.join(cls.scripts_dir, "create_layout.py")

    def setUp(self) -> None:
        pass

    def test_using_demo(self):
        """
        Test running in-toto demo against in-toto implementations.
        """

        # Create Layout.
        os.chdir(self.scripts_dir)
        create_layout_cmd = ["python3", self.create_layout]
        self.assert_cli_sys_exit(create_layout_cmd, 0)

        # Move generated layout to test dir.
        move("root.layout", self.test_dir)
        os.chdir(self.test_dir)

        # Step 1: Clone source code (Bob) using in-toto run.
        clone_cmd = [
            "in-toto-golang",
            "run",
            "-n",
            "clone",
            "-p",
            "demo-project/foo.py",
            "-k",
            self.bob_key,
            "--",
            "git",
            "clone",
            "https://github.com/in-toto/demo-project.git",
        ]
        self.assert_cli_sys_exit(clone_cmd, 0)

        # Step 2: Update version number (Bob) using in-toto record.
        update_version_start_cmd = [
            "in-toto-golang",
            "record",
            "start",
            "-n",
            "update-version",
            "-k",
            self.bob_key,
            "-m",
            "demo-project/foo.py",
        ]

        self.assert_cli_sys_exit(update_version_start_cmd, 0)

        update_version = (
            'echo \'VERSION = "foo-v1"\n\n'
            'print("Hello in-toto")\n\' > demo-project/foo.py'
        )
        subprocess.call(update_version, shell=True)

        update_version_stop_cmd = [
            "in-toto-golang",
            "record",
            "stop",
            "-n",
            "update-version",
            "-k",
            self.bob_key,
            "-p",
            "demo-project/foo.py",
        ]
        self.assert_cli_sys_exit(update_version_stop_cmd, 0)

        # NOTE: in-toto-golang doesn't removes unfinished link on record stop.
        # TODO: Report this issue.
        os.remove(".update-version.776a00e2.link-unfinished")

        # Step 3: Package (Carl) using in-toto run.
        package_cmd = [
            "in-toto-golang",
            "run",
            "-n",
            "package",
            "-m",
            "demo-project/foo.py",
            "-p",
            "demo-project.tar.gz",
            "-k",
            self.carl_key,
            "--",
            "tar",
            "--exclude",
            "'.git'",
            "-zcvf",
            "demo-project.tar.gz",
            "demo-project",
        ]
        self.assert_cli_sys_exit(package_cmd, 0)

        # Removing demo-project directory before verifying.
        rmtree("demo-project")

        # Verify using in-toto-golang verify.
        verify_cmd_go = [
            "in-toto-golang",
            "verify",
            "--layout",
            "root.layout",
            "--layout-keys",
            self.owner_pub,
        ]
        self.assert_cli_sys_exit(verify_cmd_go, 0)
        rmtree("demo-project")

        # Verify using in-toto-python verify.
        verify_cmd = [
            "in-toto-verify",
            "--layout",
            "root.layout",
            "--layout-key",
            self.owner_pub,
        ]
        self.assert_cli_sys_exit(verify_cmd, 0)

    def tearDown(self) -> None:
        self.tear_down_test_dir()


if __name__ == "__main__":
    unittest.main()

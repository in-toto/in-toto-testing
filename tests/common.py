#!/usr/bin/env python

"""
Common code for in-toto unittests, import like so: `import tests.common`
"""

import os
import shutil
import subprocess
import tempfile
import unittest

from .util import remove_with_write


class TmpDirMixin:
    """Mixin with classmethods to create and change into a temporary directory,
    and to change back to the original CWD and remove the temporary directory.

    Note: Ported from in-toto-python tests/common.py.
    """

    @classmethod
    def set_up_test_dir(cls):
        """Back up CWD, and create and change into temporary directory."""
        cls.original_cwd = os.getcwd()
        cls.test_dir = os.path.realpath(tempfile.mkdtemp())
        os.chdir(cls.test_dir)

    @classmethod
    def tear_down_test_dir(cls):
        """Change back to original CWD and remove temporary directory."""
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.test_dir, onerror=remove_with_write)


class CliTestCase(unittest.TestCase):
    """TestCase subclass providing a test helper that calls a subprocess or cli
    and asserts the return code equal to the passed status argument.

    Note: Ported from in-toto-python common.
    """

    def assert_cli_sys_exit(self, cmd, status):
        """Test helper to makes command line call and assert return value."""

        exc = subprocess.run(cmd, capture_output=True, check=False, text=True)
        self.assertEqual(exc.returncode, status, exc.stderr)

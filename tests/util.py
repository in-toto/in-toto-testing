"""
Utilities for tests.
"""

import os
import stat


def remove_with_write(func, path, _):
    """
    Remove a file or directory with write permission.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

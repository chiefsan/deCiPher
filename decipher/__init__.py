"""
___init__.py for decipher
"""

import os
import tempfile

if os.name == "posix":
    TMPDIR = "/tmp/"
else:
    TMPDIR = tempfile.gettempdir()

"""
eyesight

Enable/disable the built-in camera on macOS.
"""
import os

PROGRAM_NAME = 'eyesight'
MIN_MACOS_VERSION = 10.10
UID = os.geteuid()
IS_ROOT = UID == 0

__version__ = '1.2.1'

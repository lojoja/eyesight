#!/usr/bin/env python
"""
eyesight

Enable/disable the built-in camera on macOS.
"""
import os
import platform

import click
from pathlib2 import Path
import subprocess32

PROGRAM_NAME = 'eyesight'
MIN_MACOS_VERSION = 10.10
CAMERA_FILES = [
    Path('/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServices.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/AVC.plugin/Contents/MacOS/AVC'),
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),
    Path('/System/Library/QuickTime/QuickTimeUSBVDCDigitizer.component/Contents/MacOS/QuickTimeUSBVDCDigitizer'),
    Path('/Library/CoreMediaIO/Plug-Ins/DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera'),
    Path('/Library/CoreMediaIO/Plug-Ins/FCP-DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera')
]
DISABLE_FILE_MODE = 0o000
ENABLE_FILE_MODE = 0o755


def get_mac_version():
    """Get system macOS version (e.g., 10.10)"""
    version = platform.mac_ver()[0]
    return float('.'.join(version.split('.')[:2]))


def get_sip_status():
    """
    Get System Integrity Protection status

    Possible return values are:
        - None: SIP status could not be determined
        - 'ENABLED': SIP is enabled
        - 'DISABLED': SIP is disabled
    """
    try:
        status = subprocess32.check_output(['csrutil', 'status'])
    except subprocess32.CalledProcessError:
        status = None

    if status:
        # status string: 'System Integrity Protection status: disabled.\n'
        status = status.split(': ')[1].strip('.\n').upper()
    return status


@click.command()
@click.option('--enable/--disable', default=None)
@click.version_option()
def cli(enable):
    """Command line entry point"""
    if not os.geteuid() == 0:
        raise click.ClickException('{} must be run as root'.format(PROGRAM_NAME))

    if get_mac_version() < MIN_MACOS_VERSION:
        raise click.ClickException('{} requires macOS {} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION))

    sip = get_sip_status()
    if sip is None:
        raise click.ClickException('Could not determine SIP status')
    elif sip == 'ENABLED':
        raise click.ClickException('Camera state cannot be altered while SIP is enabled')

    if enable is None:
        raise click.UsageError('Missing option (--enable/--disable)')

    mode = ENABLE_FILE_MODE if enable else DISABLE_FILE_MODE
    files = [f for f in CAMERA_FILES if f.is_file()]

    for f in files:
        f.chmod(mode)

    action = 'enabled' if enable else 'disabled'
    click.echo('Camera {}'.format(action))

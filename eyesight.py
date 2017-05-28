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
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServices.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),  # noqa
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/AVC.plugin/Contents/MacOS/AVC'),  # noqa
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),  # noqa
    Path('/System/Library/QuickTime/QuickTimeUSBVDCDigitizer.component/Contents/MacOS/QuickTimeUSBVDCDigitizer'),
    Path('/Library/CoreMediaIO/Plug-Ins/DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera'),
    Path('/Library/CoreMediaIO/Plug-Ins/FCP-DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera')
]

def check_mac_version():
    """
    Verify system macOS version is supported.

    :raises click.ClickException: When the system version is not supported.
    """

    version = platform.mac_ver()[0]
    version = float('.'.join(version.split('.')[:2]))  # format as e.g., '10.10'

    if version < MIN_MACOS_VERSION:
        msg = '{0} requires macOS {1} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION)
        raise click.ClickException(msg)


def check_sip_status():
    """
    Verify System Integrity Protection (SIP) is disabled.

    :raises click.ClickException: When SIP status is unknown or SIP is enabled.
    """
    try:
        status = subprocess32.check_output(['csrutil', 'status'])
    except subprocess32.CalledProcessError:
        msg = 'Could not determine SIP status'
        raise click.ClickException(msg)

    # status string format example: 'System Integrity Protection status: disabled.\n'
    status = status.split(': ')[1].strip('.\n').upper()

    if status == 'ENABLED':
        msg = 'SIP is enabled'
        raise click.ClickException(msg)


def check_user_permissions():
    """
    Check that program was started by root user.

    :raises click.ClickException: When script is run by an unprivileged user.
    """

    if not os.geteuid() == 0:
        msg = '{0} must be run as root'.format(PROGRAM_NAME)
        raise click.ClickException(msg)


def get_camera_files():
    """
    Get a list of `CAMERA_FILES` that exist on the system.

    :raises click.ClickException: When no `CAMERA_FILES` exist.
    """

    files = [f for f in CAMERA_FILES if f.is_file()]

    if not files:
        msg = 'There are no camera files to modify'
        raise click.ClickException(msg)

    return files


@click.command()
@click.option('--enable/--disable', default=None)
@click.version_option()
def cli(enable):
    """
    Command line entry point.

    Validates options, verifies the system is in a correct state,
    and applies the specified action to the built-in camera.

    :param enable: Camera state flag. Enables if `True`, disables if `False`. Default is `None` (no-op).
    """

    if enable is None:
        msg = 'Missing option (--enable/--disable)'
        raise click.UsageError(msg)

    check_user_permissions()
    check_mac_version()
    check_sip_status()

    # Everything checks out so change the files
    files = get_camera_files()
    mode = 0o755 if enable else 0o000

    for f in files:
        f.chmod(mode)

    msg = 'Camera {0}d'.format('enable' if enable else 'disable')
    click.echo(msg)

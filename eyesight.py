#!/usr/bin/env python
"""
eyesight

Enable/disable the built-in camera on macOS.
"""
import logging
import logging.config
import logging.handlers
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
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(name)s [%(levelname)s]: %(message)s',
            'datefmt': '%b %d %Y %H:%M:%S'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '{0}{1}.log'.format('/var/log/', PROGRAM_NAME),
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['default'],
            'propogate': 'no'
        }
    }
}

logger = logging.getLogger(PROGRAM_NAME)
logging.config.dictConfig(LOG_CONFIG)


def check_mac_version():
    """
    Verify system macOS version is supported.

    :raises click.ClickException: When the system version is not supported.
    """
    logger.info('Checking macOS version')

    version = platform.mac_ver()[0]
    version = float('.'.join(version.split('.')[:2]))  # format as e.g., '10.10'

    if version < MIN_MACOS_VERSION:
        msg = '{0} requires macOS {1} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION)
        logger.error(msg)
        raise click.ClickException(msg)


def check_sip_status():
    """
    Verify System Integrity Protection (SIP) is disabled.

    :raises click.ClickException: When SIP status is unknown or SIP is enabled.
    """
    logger.info('Checking SIP status')

    try:
        status = subprocess32.check_output(['csrutil', 'status'])
    except subprocess32.CalledProcessError:
        msg = 'Could not determine SIP status'
        logger.error(msg)
        raise click.ClickException(msg)

    # status string format example: 'System Integrity Protection status: disabled.\n'
    status = status.split(': ')[1].strip('.\n').upper()

    if status == 'ENABLED':
        msg = 'SIP is enabled'
        logger.error(msg)
        raise click.ClickException(msg)


def check_user_permissions():
    """
    Check that program was started by root user.

    :raises click.ClickException: When script is run by an unprivileged user.
    """
    logger.info('Checking user privileges')

    if not os.geteuid() == 0:
        msg = '{0} must be run as root'.format(PROGRAM_NAME)
        logger.error(msg)
        raise click.ClickException(msg)


def get_camera_files():
    """
    Get a list of `CAMERA_FILES` that exist on the system.

    :raises click.ClickException: When no `CAMERA_FILES` exist.
    """
    logger.info('Collecting camera files')

    files = [f for f in CAMERA_FILES if f.is_file()]

    if not files:
        msg = 'There are no camera files to modify'
        logger.error(msg)
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
    logger.info('{0} started'.format(PROGRAM_NAME))

    if enable is None:
        msg = 'Missing option (--enable/--disable)'
        logger.error(msg)
        raise click.UsageError(msg)

    logger.info('Verifying system state')
    check_user_permissions()
    check_mac_version()
    check_sip_status()
    logger.info('System state OK')

    # Everything checks out so change the files
    files = get_camera_files()
    mode = 0o755 if enable else 0o000

    for f in files:
        logger.info('Processing {0}'.format(f))
        f.chmod(mode)

    msg = 'Camera {0}d'.format('enable' if enable else 'disable')
    logger.info(msg)
    click.echo(msg)

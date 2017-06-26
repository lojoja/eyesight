import logging
import platform

import click
from pathlib2 import Path
import subprocess32

from eyesight import IS_ROOT, MIN_MACOS_VERSION, PROGRAM_NAME, UID, __version__
import eyesight.log as log

CAMERA_FILES = [
    Path('/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServices.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),  # noqa
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/AVC.plugin/Contents/MacOS/AVC'),  # noqa
    Path('/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC'),  # noqa
    Path('/System/Library/QuickTime/QuickTimeUSBVDCDigitizer.component/Contents/MacOS/QuickTimeUSBVDCDigitizer'),
    Path('/Library/CoreMediaIO/Plug-Ins/DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera'),
    Path('/Library/CoreMediaIO/Plug-Ins/FCP-DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera')
]

logger = logging.getLogger(PROGRAM_NAME)
logger.setLevel(logging.DEBUG)


def check_mac_version():
    """
    Verify system macOS version is supported.

    :raises click.ClickException: When the system version is not supported.
    """
    logger.debug('Checking macOS version')

    version = platform.mac_ver()[0]
    version = float('.'.join(version.split('.')[:2]))  # format as e.g., '10.10'
    logger.debug('macOS version is "{}"'.format(version))

    if version < MIN_MACOS_VERSION:
        raise click.ClickException('{0} requires macOS {1} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION))


def check_sip_status():
    """
    Verify System Integrity Protection (SIP) is disabled.

    :raises click.ClickException: When SIP status is unknown or SIP is enabled.
    """
    logger.debug('Checking SIP status')

    try:
        status = subprocess32.check_output(['csrutil', 'status'])
    except subprocess32.CalledProcessError:
        raise click.ClickException('Could not determine SIP status')

    # status string format example: 'System Integrity Protection status: disabled.\n'
    status = status.split(': ')[1].strip('.\n').upper()
    logger.debug('SIP status is "{}"'.format(status))

    if status == 'ENABLED':
        raise click.ClickException('SIP is enabled')


def check_user_permissions():
    """
    Check that program was started by root user.

    :raises click.ClickException: When script is run by an unprivileged user.
    """
    logger.debug('Checking user permissions')
    logger.debug('System user ID is "{}"'.format(UID))

    if not IS_ROOT:
        raise click.ClickException('{} must be run as root'.format(PROGRAM_NAME))


def get_camera_files():
    """
    Get a list of `CAMERA_FILES` that exist on the system.

    :raises click.ClickException: When no `CAMERA_FILES` exist.
    """
    logger.debug('Collecting camera files')

    files = []

    for f in CAMERA_FILES:
        if f.is_file():
            logger.debug('File found: "{}"'.format(f))
            files.append(f)
        else:
            logger.debug('File missing: "{}"'.format(f))

    if len(files) == 0:
        raise click.ClickException('There are no camera files to modify')

    return files


@click.command()
@click.option('--enable/--disable', '-e/-d', default=None, help='Set the camera state. No-op if missing.')
@click.option('--verbose/--quiet', '-v/-q', is_flag=True, default=None, help='Specify verbosity level.')
@click.version_option()
def cli(enable, verbose):
    log.init(logger, verbose)
    logger.debug('{0} {1} started'.format(PROGRAM_NAME, __version__))

    logger.debug('Checking command line options')
    if enable is None:
        raise click.UsageError('Missing option (--enable/--disable)')
    logger.debug('Command line options are OK')

    logger.info('Performing system checks')
    check_mac_version()
    check_sip_status()
    check_user_permissions()
    logger.info('System is OK')

    logger.info('Configuring camera')
    files = get_camera_files()
    mode = 0o755 if enable else 0o000

    for f in files:
        logger.debug('Setting permissions to "{0}" for file "{1}"'.format(mode, f))
        f.chmod(mode)

    logger.info('Camera {0}d'.format('enable' if enable else 'disable'))


def show_exception(self, file=None):
    logger.error(self.message)


click.ClickException.show = show_exception
click.UsageError.show = show_exception

import logging
import os
import platform

import click

from eyesight import __version__  # noqa

__all__ = ['cli']


PROGRAM_NAME = 'eyesight'
MIN_MACOS_VERSION = 10.10
LOG_VERBOSITY_MAP = {True: logging.DEBUG, False: logging.WARNING}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClickFormatter(logging.Formatter):
    colors = {
        'critical': 'red',
        'debug': 'blue',
        'error': 'red',
        'exception': 'red',
        'warning': 'yellow',
    }

    def format(self, record):
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg
            if level in self.colors:
                prefix = click.style(
                    '{0}: '.format(level.title()), fg=self.colors[level]
                )
                if not isinstance(msg, (str, bytes)):
                    msg = str(msg)
                msg = '\n'.join(prefix + l for l in msg.splitlines())
            return msg
        return logging.Formatter.format(self, record)


class ClickHandler(logging.Handler):
    error_levels = ['critical', 'error', 'exception', 'warning']

    def emit(self, record):
        try:
            msg = self.format(record)
            err = record.levelname.lower() in self.error_levels
            click.echo(msg, err=err)
        except Exception:
            self.handleError(record)


click_handler = ClickHandler()
click_formatter = ClickFormatter()
click_handler.setFormatter(click_formatter)
logger.addHandler(click_handler)


class Camera(object):
    """ Container for camera files and routines. """

    paths = [
        '/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC',
        '/System/Library/PrivateFrameworks/CoreMediaIOServices.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC',  # noqa
        '/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/AVC.plugin/Contents/MacOS/AVC',  # noqa
        '/System/Library/PrivateFrameworks/CoreMediaIOServicesPrivate.framework/Versions/A/Resources/VDC.plugin/Contents/MacOS/VDC',  # noqa
        '/System/Library/QuickTime/QuickTimeUSBVDCDigitizer.component/Contents/MacOS/QuickTimeUSBVDCDigitizer',
        '/Library/CoreMediaIO/Plug-Ins/DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera',
        '/Library/CoreMediaIO/Plug-Ins/FCP-DAL/AppleCamera.plugin/Contents/MacOS/AppleCamera',
    ]

    def __init__(self, enable=True):
        self.enable = enable
        self.files = self.get_files()

    @property
    def mode(self):
        return 0o755 if self.enable else 0o000

    def change_state(self):
        logger.info('{0} camera'.format('Enabling' if self.enable else 'Disabling'))

        for f in self.files:
            logger.debug('Processing: "{0}"'.format(f))
            os.chmod(f, self.mode)

    def get_files(self):
        logger.debug('Collecting camera files')
        files = []

        for p in self.paths:
            if os.path.isfile(p):
                logger.debug('Camera file found "{0}"'.format(p))
                files.append(p)
            else:
                logger.debug('Skipping missing camera file "{0}"'.format(p))

        if not files:
            raise click.ClickException('Could not locate camera files')
        return files


class Context(object):
    def __init__(self, enable, verbose):
        logger.debug('Gathering system and environment details')

        self.enable = enable
        self.verbose = verbose
        self.macos_version = self._get_mac_version()
        self.sip_enabled = self._get_sip_status()
        self.sudo = os.geteuid() == 0

    def _get_mac_version(self):
        version = platform.mac_ver()[0]
        version = float('.'.join(version.split('.')[:2]))  # format as e.g., '10.10'
        return version

    def _get_sip_status(self):
        try:
            status = subprocess32.check_output(['csrutil', 'status'])
        except subprocess32.CalledProcessError:
            return None

        # status string format example: 'System Integrity Protection status: disabled.\n'
        status = status.split(': ')[1].strip('.\n').upper()
        return status == 'ENABLED'


@click.command()
@click.option(
    '--enable/--disable',
    '-e/-d',
    default=None,
    help='Set the camera state. No-op if missing.',
)
@click.option(
    '--verbose/--quiet',
    '-v/-q',
    is_flag=True,
    default=None,
    help='Specify verbosity level.',
)
@click.version_option()
@click.pass_context
def cli(ctx, enable, verbose):
    logger.setLevel(LOG_VERBOSITY_MAP.get(verbose, logging.INFO))
    logger.debug('{0} started'.format(PROGRAM_NAME))

    logger.debug('Checking "enable" command line option')
    if enable is None:
        raise click.UsageError('Missing option (--enable/--disable)')

    ctx.obj = Context(enable, verbose)

    logger.debug('Checking macOS version')
    if ctx.obj.macos_version < MIN_MACOS_VERSION:
        raise click.ClickException(
            '{0} requires macOS {1} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION)
        )

    logger.debug('Checking SIP status')
    if ctx.obj.sip_enabled is None:
        raise click.ClickException('Could not determine SIP status')
    elif ctx.obj.sip_enabled:
        raise click.ClickException('SIP is enabled')

    logger.debug('Checking user permissions')
    if not ctx.obj.sudo:
        raise click.ClickException('{0} must be run as root'.format(PROGRAM_NAME))

    camera = Camera(enable=ctx.obj.enable)
    camera.change_state()

    logger.info('Camera {0}'.format('enabled' if ctx.obj.enable else 'disabled'))


def show_exception(self, file=None):
    logger.error(self.message)


click.ClickException.show = show_exception
click.UsageError.show = show_exception

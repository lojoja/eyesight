from codecs import open
import re
from setuptools import setup


def get_long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


def get_version():
    pattern = r'^__version__ = \'([^\']*)\''
    with open('eyesight/__init__.py', encoding='utf-8') as f:
        text = f.read()
    match = re.search(pattern, text, re.M)

    if match:
        return match.group(1)
    raise RuntimeError('Unable to determine version')


setup(
    name='eyesight',
    version=get_version(),
    description='Simple utility to enable/disable the built-in iSight camera in macOS.',
    long_description=get_long_description(),
    url='https://github.com/lojoja/eyesight',
    author='lojoja',
    author_email='github@lojoja.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='macOS iSight camera privacy',
    packages=['eyesight'],
    install_requires=[
        'click>=6.0',
        'subprocess32>=3.2.7'
    ],
    entry_points={
        'console_scripts': [
            'eyesight=eyesight.core:cli',
        ]
    }
)

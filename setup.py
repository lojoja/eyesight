"""eyesight setuptools module"""
from codecs import open
from os import path
from setuptools import setup

from eyesight import __version__ as version

project_path = path.abspath(path.dirname(__file__))

with open(path.join(project_path, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eyesight',
    version=version,
    description='Simple script to enable/disable the built-in iSight camera in macOS.',
    long_description=long_description,
    url='https://github.com/lojoja/eyesight',
    author='lojoja',
    author_email='github@lojoja.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='macOS iSight camera privacy',
    py_modules=['eyesight'],
    install_requires=[
        'click>=6.7',
        'pathlib2>=2.2.1',
        'subprocess32>=3.2.7'
    ],
    entry_points={
        'console_scripts': [
            'eyesight=eyesight:cli',
        ]
    }
)

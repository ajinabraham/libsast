"""Setup for libsast."""
from setuptools import find_packages, setup

from pathlib import Path


def get_requires():
    requires = [
        'requests>=2.22.0',
        'pyyaml>=5.3',
        'semgrep==0.38.0;platform_system!="Windows"',
    ]
    return requires


def read(rel_path):
    init = Path(__file__).resolve().parent / rel_path
    return init.read_text('utf-8', 'ignore')


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            return line.split('\'')[1]
    raise RuntimeError('Unable to find version string.')


description = ('A generic SAST core built on top of '
               'semgrep and regex')
setup(
    name='libsast',
    version=get_version('libsast/__init__.py'),
    description=description,
    author='Ajin Abraham',
    author_email='ajin25@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v2 (LGPLv2)'),
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(include=[
        'libsast', 'libsast.*',
        'libsast.core_matcher', 'libsast.core_matcher',
        'libsast.core_sgrep', 'libsast.core_sgrep',
    ]),
    entry_points={
        'console_scripts': [
            'libsast = libsast.__main__:main',
        ],
    },
    include_package_data=True,
    url='https://github.com/ajinabraham/libsast',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=get_requires(),
)

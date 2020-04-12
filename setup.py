"""Setup for libsast."""
from setuptools import (
    find_packages,
    setup,
)

description = ('A generic SAST core built on top of sgrep and regex')
setup(
    name='libsast',
    version='1.0.0',
    description=description,
    author='Ajin Abraham',
    author_email='ajin25@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: '
         'GNU Lesser General Public License v2 (LGPLv2)'),
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(include=[
        'libsast', 'libsast.*',
        'libsast.core_matcher', 'libsast.core_matcher',
    ]),
    entry_points={
        'console_scripts': [
            'libsast = libsast.__main__:main',
        ],
    },
    include_package_data=True,
    url='https://github.com/ajinabraham/libsast',
    long_description=description,
    install_requires=[],
)

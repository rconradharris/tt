from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

name = 'tt'
version = '0.1'

setup(
    name=name,
    version=version,
    description='the stupid timetracker',
    license='Apache License (2.0)',
    author='Rick Harris',
    author_email='rconradharris@gmail.com',
    packages=find_packages(exclude=['tests', 'bin']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6'
    ],
    install_requires=[], # removed for better compat
    scripts=['bin/tt', 'bin/_tt_completer'])

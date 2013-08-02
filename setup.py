import os
import sys
from setuptools import setup, find_packages

version = '0.1dev'

if sys.version_info < (2, 6):
    sys.stderr.write("This package requires Python 2.6 or newer. "
                     "Yours is " + sys.version + os.linesep)
    sys.exit(1)

requires = []

setup(
    name="pycoda",
    version=version,
    author="Laurent Mignon (Acsone)",
    author_email="laurent.mignon__at __acsone.eu",
    description="Python library for Coded statement of account (CODA) ",
    license="GNU Affero GPL v3",
    long_description='\n'.join((
        open('README.rst').read(),
        open('CHANGES.rst').read())),
    url="https://launchpad.net/pycoda",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    setup_requires = ['nose'],
    tests_require=requires + ['nose', 'coverage'],
    test_suite = 'nose.collector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup'
    ],
)

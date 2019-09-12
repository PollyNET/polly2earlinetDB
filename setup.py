#!/usr/bin/env python

from setuptools import setup
import os
import re
import io

# Read the long description from the readme file
with open("readme.md", "rb") as f:
    long_description = f.read().decode("utf-8")


# Read the version parameters from the __init__.py file. In this way
# we keep the version information in a single place.
def read(*names, **kwargs):
    with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8")
                ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Run setup
setup(name='polly_2_earlinet_convertor',
      packages=['src', 'config', 'include'],
      package_data={
        # If any package contains *.txt or *.rst files, include them:
        'config': ['*.toml'],
        # And include any *.msg files found in the 'hello' package, too:
        'include': ['*'],
                    },

      version=find_version("src", "__init__.py"),
      description='Package for converting the polly profiles' +
                  ' from labview program to EARLINET format nc ' +
                  'files through command line.',
      long_description=long_description,
      url='https://github.com/ZPYin/polly_2_earlinet_convertor',
      download_url='https://github.com/ZPYin/polly_2_earlinet_convertor' +
                   '/archive/master.zip',
      author='Zhenping Yin',
      author_email='zhenping@tropos.de',
      license='MIT',
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
      ],
      keywords='polly EARLINET convertor',
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts': [
              'p2e_go=src.polly_2_earlinet_convertor:main',
          ],
      },
      )

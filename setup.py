#!/usr/bin/env python

import os
import subprocess
from setuptools import setup


# install external modules
subprocess.call([
    'pip', 'install',
    os.path.join(
        os.path.dirname(__file__), 'include',
        'iannis_b-lidar_molecular-de3d2ef2f36b')])

# Run setup
setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)

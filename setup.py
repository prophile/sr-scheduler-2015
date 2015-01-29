from setuptools import find_packages, setup
from sr.comp.scheduler.metadata import VERSION, DESCRIPTION

with open('README.rst') as f:
    long_description = f.read()

setup(name='sr.comp.scheduler',
      version=VERSION,
      packages=find_packages(),
      namespace_packages=['sr', 'sr.comp'],
      description=DESCRIPTION,
      long_description=long_description,
      license='MIT',
      author='Student Robotics Competition Software SIG',
      author_email='srobo-devel@googlegroups.com',
      install_requires=['PyYAML >=3.11, <4'])


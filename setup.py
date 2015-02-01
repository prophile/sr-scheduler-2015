from setuptools import find_packages, setup
import sr.comp.scheduler.metadata as md

with open('README.rst') as f:
    long_description = f.read()

setup(name='sr.comp.scheduler',
      version=md.VERSION,
      packages=find_packages(),
      namespace_packages=['sr', 'sr.comp'],
      description=md.DESCRIPTION,
      long_description=long_description,
      entry_points={
          'console_scripts': ['sr-comp-schedule=sr.comp.scheduler.scheduler:cli_main'],
      },
      license='MIT',
      author='Student Robotics Competition Software SIG',
      author_email='srobo-devel@googlegroups.com',
      install_requires=['PyYAML >=3.11, <4'],
      setup_requires=[
          'Sphinx >=1.3b, <2',
          'sphinx-argparse >=0.1.13, <0.2'
      ],
      zip_safe=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy'
      ])


from setuptools import setup

setup(name='apy',
      author='David Ewing, Mark Guagenti', 
      url='http://github.com/mgenti/apy', 
      maintainer='Mark Guagenti', 
      package_dir={'apy': ''},
      setup_requires=['vcversioner'],
      vcversioner={
          'version_module_paths': ['_version.py'],
      }, 
      packages=['apy'], 
      )

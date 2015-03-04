from setuptools import setup


import __init__


setup(name='apy',
      author='David Ewing, Mark Guagenti', 
      url='http://github.com/mgenti/apy', 
      maintainer='Mark Guagenti', 
      version=str(__init__.__version__), 
      package_dir={'apy': ''},
      setup_requires=['vcversioner'],
      vcversioner={
          'version_module_paths': ['_version.py'],
      }, 
      packages=['apy'], 
      )

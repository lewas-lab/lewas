from setuptools import setup

setup(name='lewas',
      version='0.1',
      packages=[ 'lewas' ],
      scripts = [ 'bin/sensor-init' ],
      install_requires = [ 'flask_restful', 'pyserial' ]
      )

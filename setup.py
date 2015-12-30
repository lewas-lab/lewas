from setuptools import setup

setup(name='lewas',
      version='0.9',
      packages=[ 'lewas', 'lewas.sources', 'lewas.models', 'lewas.parsers', 'lewas.stores' ],
      scripts = [ 'bin/sensor-init' ],
      install_requires = [ 'flask_restful', 'pyserial', 'RPi.GPIO' ]
      )

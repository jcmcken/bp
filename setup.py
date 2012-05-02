from setuptools import setup
from bp import __version__

setup(
    name='bp',
    version=__version__,
    description='A command-line interface for populating Jinja2 templates',
    author='Jon McKenzie',
    author_email='jcmcken@gmail.com',
    url='http://github.com/jcmcken/bp',
    packages=['bp'],
    scripts=['bin/bp'],
    license='BSD',
    install_requires=['Jinja2'],
)

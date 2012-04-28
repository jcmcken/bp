from setuptools import setup

setup(
    name='bp',
    version='0.1.0',
    description='A command-line interface for populating Jinja2 templates',
    author='Jon McKenzie',
    author_email='jcmcken@gmail.com',
    url='http://github.com/jcmcken/bp',
    packages=['bp'],
    scripts=['bin/bp'],
    license='BSD',
    install_requires=['Jinja2'],
)

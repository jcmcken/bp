from setuptools import setup

setup(
    name='bp',
    version=open('VERSION').read().strip(),
    description='A command-line interface for populating Jinja2 templates',
    long_description='Populate Jinja2 templates from plaintext JSON, YAML, or'
                     ' TXT files.',
    author='Jon McKenzie',
    author_email='jcmcken@gmail.com',
    url='http://github.com/jcmcken/bp',
    packages=['bp'],
    scripts=['bin/bp'],
    license='BSD',
    install_requires=['Jinja2'],
)

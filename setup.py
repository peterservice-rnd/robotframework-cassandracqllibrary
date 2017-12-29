"""Setup module for Robot Framework Cassandra CQL Library package."""

# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robotframework-cassandracqllibrary',
    version='1.0.0',
    description='A Robot Framework Cassandra Database Library',
    long_description=long_description,
    url='https://github.com/peterservice-rnd/robotframework-cassandracqllibrary',
    author='AIST',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='testing robotframework cassandra cql',
    py_modules=['CassandraCQLLibrary'],
    install_requires=['cassandra-driver', 'robotframework'],
)

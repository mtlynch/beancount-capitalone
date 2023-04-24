#!/usr/bin/env python

import os.path

import setuptools

setuptools.setup(
    name='beancount-capitalone',
    long_description=open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)),
                     'README.md')).read(),
    long_description_content_type="text/markdown",
    version='0.1.1',
    description='Import CapitalOne banking transactions into beancount format',
    author='Michael Lynch',
    license="MIT",
    keywords="capitalone beancount bookkeeping finance",
    url='https://github.com/mtlynch/beancount-capitalone.git',
    packages=['beancount_capitalone'],
    install_requires=[],
    python_requires='>=3.9',
)

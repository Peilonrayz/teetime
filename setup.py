#!/usr/bin/env python

"""setup.py."""

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='teetime',
    version='0.0.1',
    license='MIT',
    description='Add tee like functionally to Popen',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Peilonrayz',
    author_email='peilonrayz@gmail.com',
    url='https://github.com/Peilonrayz/teetime',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    keywords='tee popen command',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[],
    extras_require={
        'dev':  [
            'tox',
        ]
    },
)

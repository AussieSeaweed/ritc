#!/usr/bin/env python3

from distutils.core import setup

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(
    name='ritc',
    version='0.0.0.dev0',
    description='A Python library for interactions with Rotman Interactive '
                'Trader Market Simulator Client Application via REST exchange '
                'API',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/AussieSeaweed/ritc',
    author='Juho Kim',
    author_email='juho-kim@outlook.com',
    license='AGPLv3',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords=['rotman', 'rest', 'bmo', 'uoft'],
    project_urls={
        'Documentation': 'https://ritc.readthedocs.io/en/latest/',
        'Source': 'https://github.com/AussieSeaweed/ritc',
        'Tracker': 'https://github.com/AussieSeaweed/ritc/issues',
    },
    py_modules=['ritc'],
    install_requires=['requests~=2.28.2'],
    python_requires='>=3.8',
)

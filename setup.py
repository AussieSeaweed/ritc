#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name='ritc',
    version='1.0.0',
    description='A Python library for interactions with Rotman Interactive '
                'Trader Market Simulator Client Application via REST exchange '
                'API',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/AussieSeaweed/ritc',
    author='Juho Kim',
    author_email='juho-kim@outlook.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords=['rotman', 'rit', 'bmo', 'uoft'],
    project_urls={
        'Documentation': 'https://ritc.readthedocs.io/en/latest/',
        'Source': 'https://github.com/AussieSeaweed/ritc',
        'Tracker': 'https://github.com/AussieSeaweed/ritc/issues',
    },
    packages=find_packages(),
    install_requires=['requests>=2.28.0<3'],
    python_requires='>=3.9',
    package_data={'ritc': ['py.typed']},
)

.. ritc documentation master file, created by
   sphinx-quickstart on Mon Jan 16 00:22:38 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ritc's documentation!
================================

``ritc`` is a Python library for interactions with Rotman Interactive Trader
Market Simulator Client Application via REST exchange API.

The official REST API for Rotman Interactive Trader can be found in their
`API documentation`_.

.. _API documentation: https://rit.306w.ca/RIT-REST-API/

Features
--------

This library aims to be as lean and efficient as possible while automatically
handling all of the repetitive and frustrating parts of interacting with the
Rotman Interactive Trader. Some of the features include:

- Automatic handling of ``rate limit exceeded.`` error responses.
- Programmatic interface for all available RIT API.
- Strict ``mypy`` type-checking compatibility.
- Futureproof design compatible with all RIT API versions... past and future.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   setup
   examples
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

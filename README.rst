ritc
====

A Python library for interactions with Rotman Interactive Trader Market
Simulator Client Application via REST exchange API

The official REST API for Rotman Interactive Trader can be found in their
`API documentation`_.

.. _API documentation: https://rit.306w.ca/RIT-REST-API/

Features
--------

This library aims to be as lean and efficient as possible while automatically
handling all of the repetitive and frustrating parts of interacting with the
Rotman Interactive Trader. Some of the features include:

- Automatic handling of ``rate limit exceeded.`` error responses.
- Programmatic interface for all available RIT REST API.
- Strict ``mypy`` type-checking compatibility.
- Futureproof design compatible with every RIT REST API versions...

Installation
------------

This library is available on PyPI_.

.. _PyPI: https://pypi.org/project/ritc/

You can install it by executing the following command:

.. code-block:: sh

   pip install ritc

Documentation
-------------

You can read the latest_ and stable_ documentation online. Or, you can also
generate the documentation for offline viewing with Sphinx.

.. _latest: https://ritc.readthedocs.io/en/latest/
.. _stable: https://ritc.readthedocs.io/en/stable/

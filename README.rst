====
RITC
====

RITC is a Python library for interactions with Rotman Interactive Trader Market
Simulator Client Application via REST exchange API.

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

Usage
-----

Below shows a sample usage of RITC.

.. code-block:: python

   from ritc import Order, RIT

   rit = RIT('2X4P2XFA')

   rit.post_commands_cancel(query=f'Ticker=\'BEAR\' AND Volume>0')
   rit.post_orders(
       True,
       ticker='BULL',
       type=Order.Type.LIMIT,
       quantity=23,
       action=Order.Action.BUY,
       price=10.21,
   )

Testing and Validation
----------------------

RITC has extensive test coverage, passes mypy static type checking with strict
parameter, and has been validated through extensive use in real-life scenarios.

Contributing
------------

Contributions are welcome! Please read our Contributing Guide for more
information.

License
-------

RITC is distributed under the MIT license.

#################################################################
python-dlt645 - A basic DL/T645-2007 communication implementation
#################################################################

An incomplete implementation of the DL/T645 protocol designed to communicate
with energy meters through an infrared interface.

Development
===========

When cloning the repository for the first time:

.. code-block:: shell

    $ poetry install
    $ pre-commit install

Tests pre commit
----------------

.. code-block:: shell

    $ black --diff dlt645/
    $ flake8 dlt645/

Installation in a python virtual environment
============================================

1. Create a working directory

.. code-block:: shell

   mkdir my_project

2. Create a virtual environment

.. code-block:: shell

   python3 -m venv my_project/.venv

3. Enter the virtual environment

.. code-block:: shell

   source my_project/.venv

4. Install ``ftntlib``

.. code-block:: shell

   cd my_project
   git clone https://github.com/jpforcioli/ftntlib.git
   cd ftntlib
   python3 setup.py install

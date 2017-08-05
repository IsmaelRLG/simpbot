SimpBot
=======

.. image:: http://kwargs.net.ve/misc/mit_license-68x51.png
   :target: https://www.gnu.org/licenses/gpl-3.0.en.html

.. image:: https://www.python.org/static/community_logos/python-powered-w-140x56.png
   :target: http://python.org/

.. image:: icons/simpbot-text.png
   :target: https://github.com/IsmaelRLG/simpbot

Simpbot is a very simple bot, cross platform, multi network support, multilingual, extensible and configurable, powered by Python.

`simpbot` is currently tested on Python 2.6, 2.7, 3.4, 3.5 and 3.6.

Download and installation
=========================
First form: Only one step
-------------------------
SimpBot is available on the Python Package Index (PyPI),
this download and install the lasted stable version of simpbot; use the following command:

 .. code-block::

      pip install simpbot


Second form: Two steps
----------------------

1) Download:
 
   **Using HTTP**:
 
   .. table::

     =============== ================= ======================
     OS              Architecture      Downloads
     =============== ================= ======================
     Source code     All               simbpot-current-v-dev_
     =============== ================= ======================
   .. _simbpot-current-v-dev: https://github.com/IsmaelRLG/simpbot/archive/master.zip

   **Using GIT**:

   .. code-block::

      git clone git://github.com/IsmaelRLG/simpbot.git

2) Install running (from the source code):

  .. code-block::

     python setup.py install

Configuration
=============

1) Run the following command to generate base config:

   .. code-block::

      simpbot conf --admins --conf

2) Now edit the generated config:

   .. code-block::

      simpbot conf --admins --conf --edit

3) Add a new IRC server:

   .. code-block::

      simpbot server --add server-name
    
4) Edit IRC server:

   .. code-block::

      simpbot server --edit server-name

5) Now run SimpBot!

   .. code-block::

      simpbot status --start


License
=======
Copyright (c) 2016-2017 Ismael Lugo

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

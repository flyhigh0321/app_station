SEETopia AI Workstation
=======================

SEETopia is a Computer vision enabled deep learning based desktop application that allows warehouse staffs to do assisted quality assurance.::

The following functionalities are included in this application.

* Barcode scanning and decoding (supports EAN13 and QR codes. Can be extended to other barcode types)
* Measure length, width and depth of an object
* Send and receive real time update from WMS (in progress)
* Feature extraction based object detection (in progress)
* Deep learning based object detection (in progress)
* Kalman filtering based object tracker(in progress)
---------

Prerequisites
================
Before you begin, ensure you have met the following requirements:

* You have installed the latest version of python 3.7+
* You have a Windows/Mac machine.
-----------

Python modules (Dependencies)
================================
* `numpy <https://numpy.org/>`_
* `opencv-python <https://pypi.org/project/opencv-python/>`_
* `depthai <https://github.com/luxonis/depthai-python>`_
* `kivy <https://kivy.org/doc/stable/gettingstarted/installation.html>`_
* `hydra <https://hydra.cc/docs/intro/>`_
-----------

Installing QA APP
=====================
To get the latest versions of these packages you need for the program, use `poetry <https://python-poetry.org/docs/>`_.

Poetry Installation
-------------------
On osx install poetry from python package manager and add poetry's bin direction to your path.
::

	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

or use brew
::

	brew install poetry

On Windows install poetry and add poetry's bin direction to your path.
::

	(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python 

or use pip
::
	pip install poetry
----------

Install Dependencies
---------------------
To install the project dependencies use poetry, navigate to the ``seetopia`` directory and execute the following command
::
	poetry install

This will create a new virtual environment, store it in the cache directory, and display a randomly generated name for the virtual environment.

The virtual environment will be created here
::
	Unix: ~/.cache/pypoetry/virtualenvs
	MacOS: ~/Library/Caches/pypoetry/virtualenvs
	Windows: C:\Users\<username>\AppData\Local\pypoetry\Cache\virtualenvs or %LOCALAPPDATA%\pypoetry\Cache\virtualenvs

-------------------------------
To run the desktop application
------------------------------
From the ``seetopia`` directory, make sure the correct virtual environment is activated by executing the below commmand.
(This will output the name of the environment created in the above step)
::
	poetry env use python

After activating the correct environment,
::
	poetry run python src/kivy_qa_app.py


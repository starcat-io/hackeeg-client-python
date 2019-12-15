.. _wifi-streaming:

.. |br| raw:: html

   &nbsp;<br>

WiFi Streaming
==============

This part of the documentation is about streaming data from HackEEG via WiFi to software running
on a different computer using a Raspberry Pi 4.

You will need a Raspberry Pi 4 set up with Python 3.6. These instructions will show how to set
that up and install HackEEG on it.

Installing Raspbian
-------------------


#. Download and install `Balena Etcher <https://www.balena.io/etcher/>`_. This is a program that can write
   disk images to SD cards.
#. Download the latest `Raspbian Lite image <https://downloads.raspberrypi.org/raspbian_lite_latest>`_.
   This tutorial focuses on Raspbian Lite that has no GUI, but any version of Raspbian will work.
   (`Raspbian downloads page <https://www.raspberrypi.org/downloads/raspbian/>`_)
#. Use Etcher to write the Raspbian image to the SD card using the SD card reader.
#. Mount the card on your laptop by pulling out and reinserting the SD card. It should show up as a disk volume named ``boot`` It should show up as a disk volume named ``boot``.
#. Create a file named ``ssh`` — this will enable the ssh server.
#. Create a file called ``wpa_supplicant.conf``. This is a configuration file that will allow you to
   pre-configure the WiFi credentials. On boot, the Raspberry Pi will copy and use this as the default
   configuration file. Put the following content in it:

   .. code-block:: bash

      country=US
      ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
      update_config=1

      network={
      ssid="WIFI_SSID"
      scan_ssid=1
      psk="WIFI_PASSWORD"
      key_mgmt=WPA-PSK
      }

#. Put the SD card into the Raspberry Pi.
#. Connect the charged USB power bank to the Raspberry Pi's USB-C power connector.

Install Python 3.6
------------------

#. ssh to ``root@raspberrypi.local``
#. Install ``pip``:

   .. code-block:: bash

    sudo apt-get install python-pip

#. Install Python requirements:

   .. code-block:: bash

      sudo apt install bzip2 libbz2-dev libssl-dev libreadline-dev

#. Install ``pyenv``

   .. code-block:: bash

    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

#. Install Python 3.6 – this may take a while because it's going to compile Python.

   .. code-block:: bash

      pyenv install 3.6.8
      pyenv global 3.6.8

Installing HackEEG on a Raspberry Pi 4
--------------------------------------

#. Follow the regular :ref:`installation instructions for HackEEG <install>`.

Connecting OpenBCI to HackEEG via Lab Streaming Layer
-----------------------------------------------------

#. **IMPORTANT!** Ensure you are running on battery power. HackEEG has no mains isolation circuitry.
#. Connect to the Raspberry Pi 4 via ssh:

    .. code-block:: bash

       $ ssh root@raspberrypi.local
       $ cd hackeeg/

#. Start the ``hackeeg_stream`` program:

    .. code-block:: bash

       $ hackeeg_stream --sps 500 --continuous --lsl

#. You should see the HackEEG blue board LED blink briefly to indicate proper operation.
#. Start OpenBCI as described in :ref:`OpenBCI <openbci>`
#. Select ``Live (from Lab Streaming Layer)``
#. Select ``8 channels``
#. Click ``Start Session``
#. Click ``Start Data Stream``
#. In the lower right widget drop-down, select the Band Power widget
#. You should see something like this:

.. image:: ../images/openbci-lsl-streaming.png
   :scale: 25
   :alt: OpenBCI streaming LSL data from HackEEG
   :align: left

|br|

Credits
-------

Thanks to `Losant <https://www.losant.com>`_ for their article `Getting Started with the Raspberry Pi Zero W without a Monitor <https://www.losant.com/blog/getting-started-with-the-raspberry-pi-zero-w-without-a-monitor>`_
that part of this documentation is based on.

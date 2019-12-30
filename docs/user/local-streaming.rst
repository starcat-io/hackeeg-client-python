.. include:: /substitutions.rst
.. _local-streaming:

Local Streaming
===============

This part of the documentation is about streaming data from HackEEG to software running on the same
computer, like a laptop.

Installing HackEEG on a Raspberry Pi 4
--------------------------------------

First, :ref:`install HackEEG <install>` on your computer.

Connecting OpenBCI to HackEEG via Lab Streaming Layer
-----------------------------------------------------

#. **IMPORTANT!** Ensure you are running on battery power. HackEEG has no mains isolation circuitry.
#. Start the ``hackeeg_stream`` program:

    .. code-block:: bash

       $ hackeeg_stream --sps 500 --continuous --lsl

#. You should see the HackEEG blue board LED blink briefly to indicate proper operation.
#. Start OpenBCI as described in :ref:`openbci`
#. Select ``Live (from Lab Streaming Layer)``
#. Select ``8 channels``
#. Click ``Start Session``
#. Click ``Start Data Stream``
#. In the lower right widget drop-down, select the Band Power widget
#. You should see something like this:

  .. image:: ../images/openbci-lsl-streaming.png
     :scale: 25
     :alt: OpenBCI streaming LSL data from HackEEG

 |br|

hackeeg_stream Usage Information
--------------------------------

    .. code-block:: bash

       $ hackeeg_stream -h
       usage: hackeeg_stream.py [-h] [--debug] [--samples SAMPLES] [--continuous]
                                [--sps SPS] [--gain GAIN] [--lsl]
                                [--lsl-stream-name LSL_STREAM_NAME] [--messagepack]
                                [--hex] [--quiet]
                                serial_port

       positional arguments:
         serial_port           serial port device path

       optional arguments:
         -h, --help            show this help message and exit
         --debug, -d           enable debugging output
         --samples SAMPLES, -S SAMPLES
                               how many samples to capture
         --continuous, -C      read data continuously (until <return> key is pressed)
         --sps SPS, -s SPS     ADS1299 samples per second setting- must be one of
                               [250, 500, 1024, 2048, 4096, 8192, 16384], default is
                               500
         --gain GAIN, -g GAIN  ADS1299 gain setting for all channels– must be one of
                               [1, 2, 4, 6, 8, 12, 24], default is 1
         --lsl, -L             Send samples to an LSL stream instead of terminal
         --lsl-stream-name LSL_STREAM_NAME, -N LSL_STREAM_NAME
                               Name of LSL stream to create
         --messagepack, -M     MessagePack mode– use MessagePack format to send
                               sample data to the host, rather than JSON Lines
         --hex, -H             hex mode– output sample data in hexidecimal format for
                               debugging
         --quiet, -q           quiet mode– do not print sample data (used for
                               performance testing)


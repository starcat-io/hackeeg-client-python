.. _quickstart:

Quickstart
==========

Here's the quick version of getting things going. This assumes you have your HackEEG
connected to your Arduino Due, and it's plugged in to your laptop's USB port.

#. **IMPORTANT!** Ensure you are running on battery power. HackEEG has no mains isolation circuitry.
#. Install hackeeg

    .. code-block:: bash

       $ pipenv install
       $ pipenv install hackeeg
       $ pipenv shell

#. Run the hackeeg streaming program

    .. code-block:: bash

       $ hackeeg_stream --sps 500 --continuous --lsl

hackeeg_stream Usage Information
--------------------------------

If you run ``hackeeg_stream --help``, this is what you will get::

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


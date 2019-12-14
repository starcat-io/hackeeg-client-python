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




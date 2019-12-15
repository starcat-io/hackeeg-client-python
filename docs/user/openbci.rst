.. _openbci:

Installing OpenBCI
==================

This section covers installing and running the Lab Streaming Layer branch of Starcat's fork of
`OpenBCI <https://github.com/OpenBCI/OpenBCI_GUI>`_.
We can't use the regular released version of OpenBCI because Starcat has modified OpenBCI to take
`Lab Streaming Layer <https://github.com/sccn/labstreaminglayer>`_ input,
and these changes haven't made it back into the main released version.

#. Download the latest version of the `Processing <https://processing.org/download/>`_ app
#. Using git, clone the Starcat fork of `OpenBCI_GUI <https://github.com/adamfeuer/openbci_gui>`_

    .. code-block:: bash

       $ git clone https://github.com/adamfeuer/OpenBCI_GUI.git

#. Switch to the ``feature/lsl-input-and-clinical-eeg-bandpass-filter`` branch

    .. code-block:: bash

       $ git checkout feature/lsl-input-and-clinical-eeg-bandpass-filter

#. Using Processing, open the ``OpenBCI_GUI`` directory that you cloned in the step 2 (File > Open on a Mac, for instance).
#. Click the Run button
#. OpenBCI should start up



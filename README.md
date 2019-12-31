# hackeeg-client-python
Python client software for [HackEEG TI ADS1299 Arduino shield](https://github.com/starcat-io/hackeeg-shield)

## Python Client Software

The Python client software is designed to run on a laptop computer. There is a `hackeeg` driver Python module for communicating with the Arduino over the USB serial port, a command line client (`hackeeg_shell` wrapper and `hackeeg_shell.py` Python client), and a demonstration and performance testing script (`hackeeg_test.py`). 

The `hackeeg_shell.py` and `hackeeg_test.py` programs set the Arduino driver to JSON Lines mode, and communicate with it that way. They issue JSON Lines commands to the Arduino, and recieve JSON Lines or MessagePack data in response.

Using Python 3.6.5 on a 2017 Retina Macbook Pro, connected to an Arduino Due configured to use the SPI DMA included in the driver, and using the MessagePack mode, the `hackeeg_test.py` program can read and transfer 8 channels of 24-bit resolution data at 16,384 samples per second, the maximum rate of the ADS1299 chip.

The Python client software requires the [PySerial](https://github.com/pyserial/pyserial) module.

## General Operation

The ADS129x chips are configured by reading and writing registers. See the chip datasheet for more information about configuring the ADS129x and reading data from it.

If the host program (the program that reads data from the driver) does not pull data from the serial or USB interface fast enough, the driver will block on sending when the serial or USB buffers fill up. This will cause the driver to lose samples. 

The driver uses the Arduino Native port for serial communication, because it is capable of 2 megabits per second or more.


In most applications, the Python 3 usage will go something like this:

```python
#!/usr/bin/env python

SERIAL_PORT_PATH="/dev/cu.usbmodem14434401"  # your actual path to the Arduino Native serial port device goes here
import sys
import hackeeg
from hackeeg import ads1299

hackeeg = hackeeg.HackEEGBoard(SERIAL_PORT_PATH)
hackeeg.connect()
hackeeg.sdatac()
hackeeg.reset()
hackeeg.blink_board_led()
hackeeg.disable_all_channels()
sample_mode = ads1299.HIGH_RES_250_SPS | ads1299.CONFIG1_const
hackeeg.wreg(ads1299.CONFIG1, sample_mode)
test_signal_mode = ads1299.INT_TEST_4HZ | ads1299.CONFIG2_const
hackeeg.wreg(ads1299.CONFIG2, test_signal_mode)
hackeeg.enable_channel(7)
hackeeg.wreg(ads1299.CH7SET, ads1299.TEST_SIGNAL | ads1299.GAIN_1X)
hackeeg.rreg(ads1299.CH5SET)

# Unipolar mode - setting SRB1 bit sends mid-supply voltage to the N inputs
hackeeg.wreg(ads1299.MISC1, ads1299.SRB1)
# add channels into bias generation
hackeeg.wreg(ads1299.BIAS_SENSP, ads1299.BIAS8P)
hackeeg.rdatac()
hackeeg.start()

while True:
    result = hackeeg.read_response()
    status_code = result.get('STATUS_CODE')
    status_text = result.get('STATUS_TEXT')
    data = result.get(hackeeg.DataKey)
    if data:
        decoded_data = result.get(hackeeg.DecodedDataKey)
        if decoded_data:
            timestamp = decoded_data.get('timestamp')
            ads_gpio = decoded_data.get('ads_gpio')
            loff_statp = decoded_data.get('loff_statp')
            loff_statn = decoded_data.get('loff_statn')
            channel_data = decoded_data.get('channel_data')
            print(f"timestamp:{timestamp} | gpio:{ads_gpio} loff_statp:{loff_statp} loff_statn:{loff_statn} |   ",
                  end='')
            for channel_number, sample in enumerate(channel_data):
                print(f"{channel_number + 1}:{sample} ", end='')
            print()
        else:
            print(data)
        sys.stdout.flush()
```



#!/usr/bin/env python


import argparse
import uuid
import time
import sys
import select
from multiprocessing import Process, Queue
import logging
import math
import collections
import threading
import pdb

import dearpygui.dearpygui as dpg

from pylsl import StreamInfo, StreamOutlet

import hackeeg
from hackeeg import ads1299
from hackeeg.driver import SPEEDS, GAINS, Status

DEFAULT_NUMBER_OF_SAMPLES_TO_CAPTURE = 50000
GRAPH_SIZE_IN_ROWS = 150000

NUM_SAMPLES_TO_KEEP = 1000000

# global data_y
# global data_x
# Can use collections if you only need the last 100 samples
global data_y
global data_x
# data_y = collections.deque([0.0, 0.0],maxlen=NUM_SAMPLES_TO_KEEP)
# data_x = collections.deque([0.0, 0.0],maxlen=NUM_SAMPLES_TO_KEEP)
data_y = [0.0] * NUM_SAMPLES_TO_KEEP
data_x = [0.0] * NUM_SAMPLES_TO_KEEP


class HackEEGTestApplicationException(Exception):
    pass


class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def init(self):
        import tty
        import termios

    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False


class WindowsNonBlockingConsole(object):
    def init(self):
        import msvcrt

    def get_data(self):
        if msvcrt.kbhit():
            char = msvcrt.getch()
            return char
        return False


class HackEEGTestApplication:
    """HackEEG commandline tool."""

    def __init__(self, queue=None):
        # if queue is None:
        #     raise HackEEGTestApplicationException("No queue given.")
        self.queue = queue

        self.serial_port_name = None
        self.hackeeg = None
        self.debug = False
        self.channel_test = False
        self.quiet = False
        self.hex = False
        self.messagepack = False
        self.channels = 8
        self.samples_per_second = 500
        self.gain = 1
        self.max_samples = 5000
        self.lsl = False
        self.lsl_info = None
        self.lsl_outlet = None
        self.lsl_stream_name = "HackEEG"
        self.stream_id = str(uuid.uuid4())
        self.read_samples_continuously = True
        self.continuous_mode = False
        self.last_timestamp = time.time()
        self.update_seconds = 1.0/60.0
        self.start_time = time.time()

        print(f"platform: {sys.platform}")
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.non_blocking_console = NonBlockingConsole()
        elif sys.platform == "win32":
            self.non_blocking_console = WindowsNonBlockingConsole()
        self.non_blocking_console.init()
        # self.debug = True

    def find_dropped_samples(self, samples, number_of_samples):
        sample_numbers = {self.get_sample_number(sample): 1 for sample in samples}
        correct_sequence = {index: 1 for index in range(0, number_of_samples)}
        missing_samples = [sample_number for sample_number in correct_sequence.keys()
                           if sample_number not in sample_numbers]
        return len(missing_samples)

    def get_sample_number(self, sample):
        sample_number = sample.get('sample_number', -1)
        return sample_number

    def read_keyboard_input(self):
        char = self.non_blocking_console.get_data()
        if char:
            self.read_samples_continuously = False

    def setup(self, samples_per_second=500, gain=1, messagepack=False):
        if samples_per_second not in SPEEDS.keys():
            raise HackEEGTestApplicationException("{} is not a valid speed; valid speeds are {}".format(
                samples_per_second, sorted(SPEEDS.keys())))
        if gain not in GAINS.keys():
            raise HackEEGTestApplicationException("{} is not a valid gain; valid gains are {}".format(
                gain, sorted(GAINS.keys())))

        self.hackeeg.stop_and_sdatac_messagepack()
        self.hackeeg.sdatac()
        self.hackeeg.blink_board_led()
        sample_mode = SPEEDS[samples_per_second] | ads1299.CONFIG1_const
        self.hackeeg.wreg(ads1299.CONFIG1, sample_mode)

        gain_setting = GAINS[gain]

        self.hackeeg.disable_all_channels()
        if self.channel_test:
            self.channel_config_test()
        else:
            self.channel_config_input(gain_setting)


        # Route reference electrode to SRB1: JP8:1-2, JP7:NC (not connected)
        # use this with humans to reduce noise
        #self.hackeeg.wreg(ads1299.MISC1, ads1299.SRB1 | ads1299.MISC1_const)

        # Single-ended mode - setting SRB1 bit sends mid-supply voltage to the N inputs
        # use this with a signal generator
        self.hackeeg.wreg(ads1299.MISC1, ads1299.SRB1)

        # Dual-ended mode
        self.hackeeg.wreg(ads1299.MISC1, ads1299.MISC1_const)
        # add channels into bias generation
        # self.hackeeg.wreg(ads1299.BIAS_SENSP, ads1299.BIAS8P)

        if messagepack:
            self.hackeeg.messagepack_mode()
        else:
            self.hackeeg.jsonlines_mode()
        self.hackeeg.start()
        self.hackeeg.rdatac()
        return

    def channel_config_input(self, gain_setting):
        # all channels enabled
        # for channel in range(1, 9):
        #     self.hackeeg.wreg(ads1299.CHnSET + channel, ads1299.TEST_SIGNAL | gain_setting )

        # self.hackeeg.wreg(ads1299.CHnSET + 1, ads1299.INT_TEST_DC | gain_setting)
        # self.hackeeg.wreg(ads1299.CHnSET + 6, ads1299.INT_TEST_DC | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 1, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 2, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 3, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 4, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 5, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 6, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 7, ads1299.ELECTRODE_INPUT | gain_setting)
        self.hackeeg.wreg(ads1299.CHnSET + 8, ads1299.ELECTRODE_INPUT | gain_setting)

    def channel_config_test(self):
        # test_signal_mode = ads1299.INT_TEST_DC | ads1299.CONFIG2_const
        test_signal_mode = ads1299.INT_TEST_4HZ | ads1299.CONFIG2_const
        self.hackeeg.wreg(ads1299.CONFIG2, test_signal_mode)
        self.hackeeg.wreg(ads1299.CHnSET + 1, ads1299.INT_TEST_DC | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 2, ads1299.SHORTED | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 3, ads1299.MVDD | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 4, ads1299.BIAS_DRN | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 5, ads1299.BIAS_DRP | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 6, ads1299.TEMP | ads1299.GAIN_1X)
        self.hackeeg.wreg(ads1299.CHnSET + 7, ads1299.TEST_SIGNAL | ads1299.GAIN_1X)
        self.hackeeg.disable_channel(8)

        # all channels enabled
        # for channel in range(1, 9):
        #     self.hackeeg.wreg(ads1299.CHnSET + channel, ads1299.TEST_SIGNAL | gain_setting )
        pass


    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("serial_port", help="serial port device path",
                            type=str)
        parser.add_argument("--debug", "-d", help="enable debugging output",
                            action="store_true")
        parser.add_argument("--samples", "-S", help="how many samples to capture",
                            default=DEFAULT_NUMBER_OF_SAMPLES_TO_CAPTURE, type=int)
        parser.add_argument("--continuous", "-C", help="read data continuously (until <return> key is pressed)",
                            action="store_true")
        parser.add_argument("--sps", "-s",
                            help=f"ADS1299 samples per second setting- must be one of {sorted(list(SPEEDS.keys()))}, default is {self.samples_per_second}",
                            default=self.samples_per_second, type=int)
        parser.add_argument("--gain", "-g",
                            help=f"ADS1299 gain setting for all channels– must be one of {sorted(list(GAINS.keys()))}, default is {self.gain}",
                            default=self.gain, type=int)
        parser.add_argument("--lsl", "-L",
                            help=f"Send samples to an LSL stream instead of terminal",
                            action="store_true"),
        parser.add_argument("--lsl-stream-name", "-N",
                            help=f"Name of LSL stream to create",
                            default=self.lsl_stream_name, type=str),
        parser.add_argument("--messagepack", "-M",
                            help=f"MessagePack mode– use MessagePack format to send sample data to the host, rather than JSON Lines",
                            action="store_true")
        parser.add_argument("--channel-test", "-T",
                            help=f"set the channels to internal test settings for software testing",
                            action="store_true")
        parser.add_argument("--hex", "-H",
                            help=f"hex mode– output sample data in hexidecimal format for debugging",
                            action="store_true")
        parser.add_argument("--quiet", "-q",
                            help=f"quiet mode– do not print sample data (used for performance testing)",
                            action="store_true")
        args = parser.parse_args()
        if args.debug:
            self.debug = True
            print("debug mode on")
        self.samples_per_second = args.sps
        self.gain = args.gain

        if args.continuous:
            self.continuous_mode = True

        if args.lsl:
            self.lsl = True
            if args.lsl_stream_name:
                self.lsl_stream_name = args.lsl_stream_name
            self.lsl_info = StreamInfo(self.lsl_stream_name, 'EEG', self.channels, self.samples_per_second, 'int32',
                                       self.stream_id)
            self.lsl_outlet = StreamOutlet(self.lsl_info)

        self.serial_port_name = args.serial_port
        self.hackeeg = hackeeg.HackEEGBoard(self.serial_port_name, baudrate=2000000, debug=self.debug)
        self.max_samples = args.samples
        self.channel_test = args.channel_test
        self.quiet = args.quiet
        self.hex = args.hex
        self.messagepack = args.messagepack
        self.hackeeg.connect()
        self.setup(samples_per_second=self.samples_per_second, gain=self.gain, messagepack=self.messagepack)

    def process_sample(self, result, samples):
        # print("process sample")
        data = None
        channel_data = None
        if result:
            status_code = result.get(self.hackeeg.MpStatusCodeKey)
            data = result.get(self.hackeeg.MpDataKey)
            samples.append(result)
            timestamp = result.get('timestamp')
            channel_data = result.get('channel_data')
            if status_code == Status.Ok and data:
                if not self.quiet:
                    sample_number = result.get('sample_number')
                    ads_gpio = result.get('ads_gpio')
                    loff_statp = result.get('loff_statp')
                    loff_statn = result.get('loff_statn')
                    data_hex = result.get('data_hex')
                    print(
                        f"timestamp:{timestamp} sample_number: {sample_number}| gpio:{ads_gpio} loff_statp:{loff_statp} loff_statn:{loff_statn}   ",
                        end='')
                    if self.hex:
                        print(data_hex)
                    else:
                        for channel_number, sample in enumerate(channel_data):
                            print(f"{channel_number + 1}:{sample} ", end='')
                        print()
                self.update_data(timestamp, channel_data[6])
                if self.lsl and channel_data:
                    self.lsl_outlet.push_sample(channel_data)
            else:
                if not self.quiet:
                    print(data)
        else:
            print("no data to decode")
            print(f"result: {result}")

    def decode_sample(self, reading):
        # Scale reading
        # See ADS1299 datasheet https://www.ti.com/lit/ds/symlink/ads1299.pdf 
        # VREF = ADS1299 internal reference voltage, 4.5V ; datasheet page 10
        # Equation: 1 LSB = (2 × VREF / Gain) / 2**24 = +FS / 2**23 
        # Section 9.5.1, page 38

        # print("sample")
        # print(f"  reading: {reading:#x}")
        # print(f"  reading: {reading:d}")
        fs = 4.5 # Full Scale = VREFP
        value_of_one_lsb_code = fs / (math.pow(2, 23) - 1)
        scaled_reading = (reading * value_of_one_lsb_code) + (fs/2)
        # print(f"  scaled reading decimal: {scaled_reading:-f}")
        return scaled_reading 

    def _update_data(self, timestamp, sample_value):
        global data_x
        global data_y
        sample = 1
        frequency=1.0
            # Get new data sample. Note we need both x and y values
            # if we want a meaningful axis unit.
        t = time.time() - self.start_time
        y = math.sin(2.0 * math.pi * frequency * t)
        data_x.append(t)
        data_y.append(y)
            
        #set the series x and y to the last nsamples
        num_samples_in_window = 10*1000
        dpg.set_value('series_tag', [list(data_x[-num_samples_in_window:]), list(data_y[-num_samples_in_window:])])          
        dpg.fit_axis_data('x_axis')
        dpg.fit_axis_data('y_axis')

    def update_data(self, timestamp, sample_value):
        global data_x
        global data_y
        now = time.time()
        if not self.started:
            self.start_time = now
            data_x = [time.time()] * NUM_SAMPLES_TO_KEEP
        self.started = True
        # print("update data")
        data_x.append(now-self.start_time)
        data_y.append(self.decode_sample(sample_value))

        if now - self.start_time >= self.update_seconds:
            self.last_timestamp = now
            num_samples_in_window = 10*250
            #set the series x and y to the last nsamples
            dpg.set_value('series_tag', [list(data_x[-num_samples_in_window:]), list(data_y[-num_samples_in_window:])])          
            dpg.fit_axis_data('x_axis')
            dpg.fit_axis_data('y_axis')

    def main(self):
        # print("about to parse args")
        self.parse_args()
        self.started = False

        samples = []
        sample_counter = 0

        # print("about to start HackEEG sampling")
        end_time = time.perf_counter()
        start_time = time.perf_counter()
        while ((sample_counter < self.max_samples and not self.continuous_mode) or \
               (self.read_samples_continuously and self.continuous_mode)):
            result = self.hackeeg.read_rdatac_response()
            end_time = time.perf_counter()
            sample_counter += 1
            # if self.continuous_mode:
            #     self.read_keyboard_input()
            self.process_sample(result, samples)

        duration = end_time - start_time
        # print("about to end HackEEG sampling")
        self.hackeeg.stop_and_sdatac_messagepack()
        self.hackeeg.blink_board_led()

        print(f"duration in seconds: {duration}")
        samples_per_second = sample_counter / duration
        print(f"samples per second: {samples_per_second}")
        dropped_samples = self.find_dropped_samples(samples, sample_counter)
        print(f"dropped samples: {dropped_samples}")


class HackEEGGui:
    def __init__(self):
        pass
            
    def start_gui(self):
        global data_y
        global data_x

        dpg.create_context()
        with dpg.window(label='Tutorial', tag='win',width=3000, height=800):

            with dpg.plot(label='Line Series', height=-1, width=-1):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes, set to auto scale.
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')
                #dpg.set_axis_limits("y_axis", 5.0, -5.0)
                # dpg.set_axis_limits("y_axis", 50.0, -50.0)

                # series belong to a y axis. Note the tag name is used in the update
                # function update_data
                dpg.add_line_series(x=list(data_x),y=list(data_y), 
                                    label='Temp', parent='y_axis', 
                                    tag='series_tag')
                                    
        dpg.create_viewport(title='HackEEG Samples', width=3050, height=840)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # print("started dearpygui")
        hackeeg = HackEEGTestApplication()
        thread = threading.Thread(target=hackeeg.main)
        thread.start()
        dpg.start_dearpygui()
        dpg.destroy_context()
        dpg.create_context()


if __name__ == "__main__":
    HackEEGGui().start_gui()
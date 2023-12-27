#!/usr/bin/env python

import argparse
import uuid
import time
import sys
import select
from multiprocessing import Process, Queue
import logging

from pylsl import StreamInfo, StreamOutlet

import hackeeg
from hackeeg import ads1299
from hackeeg.driver import SPEEDS, GAINS, Status

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import callback, Dash, dcc, html
from dash.dependencies import Input, Output

DEFAULT_NUMBER_OF_SAMPLES_TO_CAPTURE = 50000
GRAPH_SIZE_IN_ROWS = 15000
SCALE_FACTOR = 1000000.0

class Plotter:
    def __init__(self, app=None, queue=None):
        self.app = app
        if self.app is None:
            self.app = Dash(__name__)
        self.callbacks(self.app)

        self.queue = queue
        if self.queue is None:
            raise Exception("No queue given.")

        self.cols = None
        self.df = None
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    def callbacks(self, app):
        @app.callback(
            Output('graph', 'figure'),
            [Input('interval-component', "n_intervals")]
        )
        def streamFig(value):
            for i in range(0, 100):
                time, reading = self.get_datapoint()
                # print(f'time: {time}    reading:{reading}')
                new_record_df = pd.DataFrame({'time': [time], 'channel_7': [reading]}, columns=self.cols)
                self.df = pd.concat([self.df, new_record_df])
            # print(self.df.tail())

            number_of_rows = len(self.df)
            if number_of_rows < GRAPH_SIZE_IN_ROWS:
                number_of_rows_to_display = number_of_rows
            else:
                number_of_rows_to_display = GRAPH_SIZE_IN_ROWS
            df_window = self.df.iloc[-number_of_rows_to_display:]
            # df_window = self.df
            fig = px.line(df_window, x='time', y='channel_7', markers = True, template = 'plotly_dark')
            fig.update_layout(title='HackEEG data', xaxis_title='Time (seconds)', yaxis_title='Reading',
                              yaxis_range=[-10.0, 10.0])

            colors = px.colors.qualitative.Plotly
            for i, col in enumerate(df_window.columns):
                    fig.add_annotation(x=df_window.index[-1], y=df_window[col].iloc[-1],
                                        text = str(df_window[col].iloc[-1])[:4],
                                        align="right",
                                        arrowcolor = 'rgba(0,0,0,0)',
                                        ax=25,
                                        ay=0,
                                        yanchor = 'middle',
                                        font = dict(color = colors[i]))
            return(fig)


    def get_datapoint(self):
        time, reading = self.queue.get(block=True)
        return time, reading / SCALE_FACTOR

    def main(self):
        pd.options.plotting.backend = "plotly"

        np.random.seed(4) 
        self.cols = ['time', 'channel_7']
        self.df = pd.DataFrame({'time': [0.1], 'channel_7': [1]}, columns=self.cols)
        self.df.set_index('time', inplace=True)
        print(self.df.tail())
        # print(self.df.columns)

        time, reading = self.get_datapoint()
        new_record_df = pd.DataFrame({'time': [time], 'channel_7': [reading]}, columns=self.cols)
        self.df = pd.concat([self.df, new_record_df])
        print(self.df.tail())

        # X = pd.DataFrame(np.array([self.get_datapoint()], dtype=float))
        # self.df=pd.DataFrame(X, columns=self.cols)

        self.df.iloc[0]=0;

        fig = self.df.plot(template = 'plotly_dark')

        self.app.layout = html.Div([
            html.H1("Streaming of HackEEG samples"),
                    dcc.Interval(
                    id='interval-component',
                    interval=200, # milliseconds
                    n_intervals=0
                ),
            dcc.Graph(id='graph'),
        ])

        self.app.run(port = 8069, dev_tools_ui=True, #debug=True,
                dev_tools_hot_reload =True, threaded=True)
                


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
        if queue is None:
            raise HackEEGTestApplicationException("No queue given.")
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
                if self.queue:
                    self.queue.put([timestamp, channel_data[6]])
                if self.lsl and channel_data:
                    self.lsl_outlet.push_sample(channel_data)
            else:
                if not self.quiet:
                    print(data)
        else:
            print("no data to decode")
            print(f"result: {result}")

    def main(self):
        self.parse_args()

        samples = []
        sample_counter = 0

        end_time = time.perf_counter()
        start_time = time.perf_counter()
        while ((sample_counter < self.max_samples and not self.continuous_mode) or \
               (self.read_samples_continuously and self.continuous_mode)):
            result = self.hackeeg.read_rdatac_response()
            end_time = time.perf_counter()
            sample_counter += 1
            if self.continuous_mode:
                self.read_keyboard_input()
            self.process_sample(result, samples)

        duration = end_time - start_time
        self.hackeeg.stop_and_sdatac_messagepack()
        self.hackeeg.blink_board_led()

        print(f"duration in seconds: {duration}")
        samples_per_second = sample_counter / duration
        print(f"samples per second: {samples_per_second}")
        dropped_samples = self.find_dropped_samples(samples, sample_counter)
        print(f"dropped samples: {dropped_samples}")


def plotter_process(app, queue):
    if queue is None:
        raise Exception("no q")
    Plotter(app=app, queue=queue).main()


def hackeeg_process():
    queue = Queue()
    app = None
    p = Process(target=plotter_process, args=(app, queue))
    p.start()
    HackEEGTestApplication(queue=queue).main()
    p.join()


if __name__ == "__main__":
    hackeeg_process()
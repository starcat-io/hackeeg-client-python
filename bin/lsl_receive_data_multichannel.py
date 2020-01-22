#!/usr/bin/env python

# Example program to show how to read a multi-channel time series from LSL.

from pylsl import StreamInlet, resolve_stream

print("looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
print(len(streams))
for stream in streams:
    print(stream)

inlets = []
for i, stream in enumerate(streams):
    inlets.append(StreamInlet(streams[i]))

while True:
    for i, inlet in enumerate(inlets):
        sample, timestamp = inlets[i].pull_sample()
        print(f"{i} {timestamp} {sample}")

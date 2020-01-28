#!/usr/bin/env python

# Example program to show how to read a multi-channel time series from LSL.

from pylsl import StreamInlet, resolve_stream

print("looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
print(len(streams))
for stream in streams:
    print(f"{stream.type()} {stream.name()}")

inlets = []
for i, stream in enumerate(streams):
    inlets.append(StreamInlet(streams[i]))

while True:
    print("loop")
    for i, inlet in enumerate(inlets):
        print(f"about to pull from inlet {i}")
        sample, timestamp = inlets[i].pull_sample()
        print(f"{i} {timestamp} {sample}")

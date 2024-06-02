# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
# Read music sequence from text file and translate it to timed MIDI messages.
#
import os, sys
from .sequencer import sequencer
from .player import Player


def usage():
    print("Usage:\n   python3 -m txtseq <text-file>")

def midi_tx(data):
    # You could implement code here for sending MIDI on desktop python using
    # the library of your choice. For a CircuitPython implementation example,
    # see code.py
    pass

def main():
    if (len(sys.argv) != 2) or (not os.path.isfile(sys.argv[1])):
        usage()
        exit(1)
    with open(sys.argv[1], 'rb') as f:
        db = sequencer(f)
        print()
        for (i, e) in enumerate(db['buf']):
            print(f"{e:08X}", end=' ')
            if i % 10 == 9:
                print()
        print()
        print('\nStarting player')
        for idle_ms in Player(db, midi_out_callback=midi_tx, debug=True):
            if idle_ms > 2:
                # you can do other work here between MIDI events
                pass
            else:
                pass
        print('Done')

main()

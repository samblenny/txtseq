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

def main():
    if (len(sys.argv) != 2) or (not os.path.isfile(sys.argv[1])):
        usage()
        exit(1)
    with open(sys.argv[1], 'rb') as f:
        db = sequencer(f)
        print()
        for (i, e) in enumerate(db['buf']):
            print(f"{e:08X}", end=' ')
            if i & 7 == 7:
                print()
        print()
        print('\nStarting player')
        for idle_ms in Player(db, debug=True):
            if idle_ms > 2:
                # you can do other work here between MIDI events
                pass
            else:
                pass
        print('\nDone')

main()

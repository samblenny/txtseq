# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
# Read music sequence from text file and translate it to timed MIDI messages.
#
import os, sys
from .sequencer import sequencer


PROFILE = False  #True

if PROFILE:
    import cProfile


def usage():
    print("Usage:\n   python3 -m txtseq <text-file>")

def main():
    if (len(sys.argv) != 2) or (not os.path.isfile(sys.argv[1])):
        usage()
        exit(1)
    with open(sys.argv[1], 'rb') as f:
        seq = sequencer(f)
        print()
        for (i, s) in enumerate(seq):
            print(f"{s:08X}", end=' ')
            if i & 7 == 7:
                print()
        print()


if PROFILE:
    cProfile.run('main()', sort='cumulative')
else:
    main()

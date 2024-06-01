# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from gc import collect, mem_free
from time import monotonic
from txtseq.sequencer import sequencer
from txtseq.player import Player


def main():
    # preload global names
    p = print

    collect()
    a = mem_free()          # a: baseline free mem
    with open('track1.txt', 'rb') as f:
        collect()
        b = mem_free()      # b: free mem before parse
        t = monotonic()     # t: timestamp before parse
        db = sequencer(f)   # parse song
        T = monotonic()     # T: timestamp after parse
        collect()
        c = mem_free()      # c: free mem after parse
        p(f'[parse time: %s ms]' % int((T - t) * 1000))
        t = monotonic()     # timestamp before hexdump
        p()                 # hexdump the midi events
        for (i, e) in enumerate(db['buf']):
            p(f"{e:08X}", end=' ')
            if i & 7 == 7:
                p()
        p(f'\n[midi event dump time: %s ms]\n' % int((monotonic() - t) * 1000))
        p('mem_free:', a, b, c, '  diffs:', a-b, b-c)
        p('\nStarting player')
        collect()
        # Player is a generator that is meant to be called frequently to play
        # MIDI events at their scheduled timestamps. The generator yields
        # the remaining ms until its next scheduled MIDI event (idle_ms).
        for idle_ms in Player(db, debug=True):
            if idle_ms > 2:
                # you can do other work here like checking buttons or whatever
                pass
            else:
                pass
        p('\nDone')

    while True:
        pass

main()

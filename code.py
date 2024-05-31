# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from gc import collect, mem_free
from time import monotonic
from txtseq.sequencer import sequencer


def main():
    # preload global names
    p = print

    collect()
    a = mem_free()          # a: baseline free mem
    with open('track1.txt', 'rb') as f:
        collect()
        b = mem_free()      # b: free mem before parse
        t = monotonic()     # t: timestamp before parse
        seq = sequencer(f)  # parse song
        T = monotonic()     # T: timestamp after parse
        collect()
        c = mem_free()      # c: free mem after parse
        p(f'[parse time: %s ms]' % int((T - t) * 1000))
        t = monotonic()     # timestamp before hexdump
        p()                 # hexdump the midi events
        for (i, s) in enumerate(seq):
            p(f"{s:08X}", end=' ')
            if i & 7 == 7:
                p()
        p(f'\n[midi event dump time: %s ms]\n' % int((monotonic() - t) * 1000))
        p('mem_free:', a, b, c, '  diffs:', a-b, b-c)

    while True:
        pass

main()

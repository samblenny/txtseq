# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from gc import collect, mem_free
from txtseq import sequencer


collect()
a = mem_free()
with open('track1.txt', 'rb') as f:
    collect()
    b = mem_free()
    seq = sequencer(f)
    collect()
    print()
    for (i, s) in enumerate(seq):
        print(f"{s:08X}", end=' ')
        if i & 7 == 7:
            print()
    print("\n")
    collect()
    c = mem_free()
    print(a, b, c, a-b, b-c)

while True:
    pass

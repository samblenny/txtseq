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
    c = mem_free()
    print(a, b, c, a-b, b-c)

while True:
    pass

# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from array import array
from .util import comment, whitespace, p_ppb, p_bpm
from .staff import p_staff


# Parse plaintext music notation from binary input file f.
# Returns a sequence object with note on/off events.
# CAUTION: This raises ValueError for syntax errors.
def sequencer(f):
    # preload names to avoid repeated dictionary lookups
    rd = f.read
    tell = f.tell
    seek = f.seek
    ws = whitespace
    ppb = p_ppb
    bpm = p_bpm
    com = comment
    staff = p_staff

    mark = None
    db = {
        'line': 1,
        'bpm': 120,
        'ppb': 24,              # pulses per beat @24 ppqn
        'ticks': [0, 0, 0, 0],  # ppqn timestamps for each voice
        'buf': array('L')}      # note on/off events encoded as uint32
    # Parse the leading token of each line (staff, bpm, comment, etc)
    while b := rd(1):
        ws(f)
        if b == b'\r':         # CR or CRLF line ending?
            db['line'] += 1
            mark = tell()      # skip the LF
            b = f.read(1)
            if b == b'\n':
                seek(mark)
        elif b == b'\n':       # LF line ending
            db['line'] += 1
        elif b == b'#':        # commment?
            com(f)
        elif b == b'U':
            ppb(f, db)         # U (updates db['ppb'])
        elif b == b'B':
            bpm(f, db)         # B (updates db['bpm'])
        elif b == b'1':
            staff(0, f, db)    # 1 | ...
        elif b == b'2':
            staff(1, f, db)    # 2 | ...
        elif b == b'3':
            staff(2, f, db)    # 3 | ...
        elif b == b'4':
            staff(3, f, db)    # 4 | ...
        else:
            raise ValueError(f"unexpected token, line {line}: {b}")
    return db['buf']

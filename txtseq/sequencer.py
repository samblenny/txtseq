# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from array import array
from .data import crlf
from .util import skip_comment, skip_whitespace, parse_ppb, parse_bpm
from .staff import parse_staff


# Parse plaintext music notation from binary input file f.
# Returns a sequence object with note on/off events.
# CAUTION: This raises ValueError for syntax errors.
def sequencer(f):
    rewind = None
    db = {
        'line': 1,
        'bpm': 120,
        'ppb': 24,              # pulses per beat @24 ppqn
        'ticks': [0, 0, 0, 0],  # ppqn timestamps for each voice
        'buf': array('L')}      # note on/off events encoded as uint32
    # Parse the leading token of each line (staff, bpm, comment, etc)
    while b := f.read(1):
        skip_whitespace(f)
        if b == b'\r':         # CR or CRLF line ending?
            db['line'] += 1
            rewind = f.tell()  # skip the LF
            b = f.read(1)
            if b == b'\n':
                f.seek(rewind)
        elif b == b'\n':       # LF line ending
            db['line'] += 1
        elif b == b'#':        # commment?
            skip_comment(f)
        elif b == b'U':
            parse_ppb(f, db)       # U (updates db['ppb'])
        elif b == b'B':
            parse_bpm(f, db)       # B (updates db['bpm'])
        elif b == b'1':
            parse_staff(0, f, db)  # 1 | ...
        elif b == b'2':
            parse_staff(1, f, db)  # 2 | ...
        elif b == b'3':
            parse_staff(2, f, db)  # 3 | ...
        elif b == b'4':
            parse_staff(3, f, db)  # 4 | ...
        else:
            raise ValueError(f"unexpected token, line {line}: {b}")
    return db['buf']

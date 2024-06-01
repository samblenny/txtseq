# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from array import array
from gc import collect
from .util import comment, whitespace, p_ppb, p_bpm
from .staff import p_staff


# Parse plaintext music notation from binary input file f.
# Returns a sequence object with note on/off events.
# CAUTION: This raises ValueError for syntax errors.
def sequencer(f):
    # preload names to avoid repeated dictionary lookups
    ri = f.readinto
    tell = f.tell
    seek = f.seek
    ws = whitespace
    com = comment
    line = 1
    ppb = p_ppb
    bpm = p_bpm
    staff = p_staff

    mark = None
    db = {
        'bpm': 120,
        'ppb': 24,              # pulses per beat @24 ppqn
        'ticks': [0, 0, 0, 0],  # ppqn timestamps for each voice
        'buf': array('L')}      # note on/off events encoded as uint32
    # Parse the leading token of each line (staff, bpm, comment, etc)
    b = bytearray(1)
    while ri(b):
        ws(f)
        if b == b'\r':         # CR or CRLF line ending?
            line += 1
            mark = tell()      # skip the LF
            b = f.read(1)
            if b == b'\n':
                seek(mark)
        elif b == b'\n':       # LF line ending
            line += 1
        elif b == b'#':        # commment?
            com(f)
        elif b == b'U':
            ppb(f, line, db)   # U (updates db['ppb'])
        elif b == b'B':
            bpm(f, line, db)   # B (updates db['bpm'])
        elif b == b'1' or b == b'2' or b == b'3' or b == b'4':  # staff?
            staff(int(b) - int(b'1'), f, line, db)  # 1st argument is voice
        else:
            raise ValueError(f"unexpected token, line {line}: {b}")
    # Sort the array.array('L) (uint32) encoded sequence of midi events by
    # ascending timestamp.
    # CAUTION: The call to sorted() below will allocate a copy of the whole
    # array, so there is some risk of running out of memory for long sequences!
    # But, the parser is pretty efficient, so spending some memory here should
    # probably be fine. In case of problems, switching to an in place sort
    # might help.
    collect()
    db['buf'] = sorted(db['buf'])
    return db

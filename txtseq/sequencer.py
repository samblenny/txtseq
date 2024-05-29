# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from gc import collect
from .data import crlf
from .util import skip_comment, skip_whitespace, parse_time_unit, parse_bpm
from .staff import parse_staff


# Parse plaintext music notation from binary input file f.
# Returns a sequence object with lists of note-on and note-off events.
# CAUTION: This raises ValueError for syntax errors.
def sequencer(f):
    collect()  # gc to avoid fragmentation
    rewind = None
    line = 1
    time_unit = None
    bpm = None
    notes = [[], [], [], []]
    # Parse the leading token of each line (staff, bpm, comment, etc)
    while b := f.read(1):
        collect()
        skip_whitespace(f)
        if b == b'\r':         # CR or CRLF line ending?
            line += 1
            rewind = f.tell()  # skip the LF
            b = f.read(1)
            if b == b'\n':
                f.seek(rewind)
        elif b == b'\n':       # LF line ending
            line += 1
        elif b == b'#':        # commment?
            skip_comment(f)
        elif b == b'U':
            time_unit = parse_time_unit(f, line) # U = time unit
        elif b == b'B':
            bpm = parse_bpm(f, line)             # B = bpm
        elif b == b'1':
            parse_staff(0, f, line, notes)       # 1..4 = staff lines
        elif b == b'2':
            parse_staff(1, f, line, notes)
        elif b == b'3':
            parse_staff(2, f, line, notes)
        elif b == b'4':
            parse_staff(3, f, line, notes)
        else:
            raise ValueError(f"unexpected token, line {line}: {b}")
    for (i, chan) in enumerate(notes):
        print(f"ch{i}:", end=' ')
        for (mn, duration) in chan:
            print(f"{mn}/{duration}", end=' ')
        print()
    return notes

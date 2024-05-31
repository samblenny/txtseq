# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from .data import beat_len_d


# Advance cursor in binary file f to skip comment
def comment(f):
    ri = f.readinto
    seek = f.seek
    tell = f.tell
    mark = tell()
    b = bytearray(1)
    while ri(b):
        if b == b'\r' or b == b'\n':
            seek(mark)
            break
        mark = tell()

# Advance cursor in binary file f to skip whitespace
def whitespace(f):
    seek = f.seek
    tell = f.tell
    mark = tell()
    while b := f.read(1):
        if b != b'\t' and b != b' ':
            seek(mark)
            break
        mark = tell()

# Return rest of line but strip the whitespace
def get_line(f):
    seek = f.seek
    tell = f.tell
    chars = []
    whitespace(f)
    mark = tell()
    while b := f.read(1):
        if b == b'\r' or b == b'\n':
            seek(mark)
            break
        elif b == b'#':
            comment(f)
            break
        else:
            chars.append(b)
        mark = tell()
    return b''.join(chars).rstrip()

# Parse a time unit header line like, "U 1/8" or "U 1/16".
# Result: updates value of db['ppb'].
# CAUTION: this can raise ValueError for syntax errors.
def p_ppb(f, db):
    p = print
    line = db['line']
    p(f'{line:2}: ', end='')
    x = beat_len_d.get(get_line(f), None)  # look up pulses per beat
    if not x:
        raise ValueError(f"U: line {line}")
    p(f'ppb={x}')
    db['ppb'] = x

# Parse a bpm header line like, "B 80" or "B 140".
# Result: updates value of db['bpm'].
# CAUTION: this can raise ValueError for syntax errors.
def p_bpm(f, db):
    p = print
    line = db['line']
    p(f'{line:2}: ', end='')
    x = int(get_line(f))
    p(f'bpm={x}')
    db['bpm'] = x

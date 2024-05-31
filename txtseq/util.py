# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#


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
    ri = f.readinto
    seek = f.seek
    tell = f.tell
    chars = bytearray()
    whitespace(f)
    mark = tell()
    b = bytearray(1)
    while ri(b):
        if b == b'\r' or b == b'\n':
            seek(mark)
            break
        elif b == b'#':
            comment(f)
            break
        else:
            chars.extend(b)
        mark = tell()
    return bytes(chars.rstrip())

# Parse a time unit header line like, "U 1/8" or "U 1/16".
# Result: updates value of db['ppb'].
# CAUTION: this can raise ValueError for syntax errors.
def p_ppb(f, line, db):
    d = {
        b'1/4':  24, b'1/8':  12, b'1/16':  6, b'1/32':  3,
        b'1/4T':  8, b'1/8T':  4, b'1/16T': 2, b'1/32T': 1}
    x = d.get(get_line(f), None)  # look up time unit -> pulses per beat
    if not x:
        raise ValueError(f"U: line {line}")
    print('%2d: ppb=%d' % (line, x))
    db['ppb'] = x

# Parse a bpm header line like, "B 80" or "B 140".
# Result: updates value of db['bpm'].
# CAUTION: this can raise ValueError for syntax errors.
def p_bpm(f, line, db):
    x = int(get_line(f))
    print('%2d: bpm=%d' % (line, x))
    db['bpm'] = x

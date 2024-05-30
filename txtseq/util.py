# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from .data import crlf, whitespace, beat_len_d


# Advance cursor in binary file f to skip comment
def skip_comment(f):
    rewind = f.tell()
    while b := f.read(1):
        if b in crlf:
            f.seek(rewind)
            break
        rewind = f.tell()

# Advance cursor in binary file f to skip whitespace
def skip_whitespace(f):
    rewind = f.tell()
    while b := f.read(1):
        if b not in whitespace:
            f.seek(rewind)
            break
        rewind = f.tell()

# Return rest of line but strip the whitespace
def get_rest_of_line(f):
    chars = []
    skip_whitespace(f)
    rewind = f.tell()
    while b := f.read(1):
        if b in crlf:
            f.seek(rewind)
            break
        elif b == b'#':
            skip_comment(f)
            break
        else:
            chars.append(b)
        rewind = f.tell()
    return b''.join(chars).rstrip()

# Parse a time unit header line like, "U 1/8" or "U 1/16".
# Result: updates value of db['ppb'].
# CAUTION: this can raise ValueError for syntax errors.
def parse_ppb(f, db):
    line = db['line']
    print(f"{line:2}: U", end=' ')
    ppb = beat_len_d.get(get_rest_of_line(f), None)  # look up pulses per beat
    if not ppb:
        raise ValueError(f"U: line {line}")
    print(f'ppb={ppb}')
    db['ppb'] = ppb

# Parse a bpm header line like, "B 80" or "B 140".
# Result: updates value of db['bpm'].
# CAUTION: this can raise ValueError for syntax errors.
def parse_bpm(f, db):
    line = db['line']
    print(f"{line:2}: B", end=' ')
    bpm = int(get_rest_of_line(f))
    print(bpm)
    db['bpm'] = bpm

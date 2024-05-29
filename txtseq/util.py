# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from gc import collect
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

# Parse a time unit header line like, "U 1/8" or "U 1/16".
# CAUTION: this can raise ValueError for syntax errors.
def parse_time_unit(f, line):
    print(f"{line:2}: U", end=' ')
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
    word = b''.join(chars).rstrip()
    beat_len = beat_len_d.get(word, None)
    if beat_len is None:
        raise ValueError(f"beat length: line {line}")
    print(str(word, 'ascii'), "->", beat_len)
    return beat_len

# Parse a bpm header line like, "B 80" or "B 140".
# CAUTION: this can raise ValueError for syntax errors.
def parse_bpm(f, line):
    print(f"{line:2}: B", end=' ')
    skip_whitespace(f)
    digits = []
    rewind = f.tell()
    while b := f.read(1):
        if b in crlf:
            f.seek(rewind)
            break
        elif b == b'#':
            skip_comment(f)
            break
        else:
            digits.append(b)
        rewind = f.tell()
    if not digits:
        raise ValueError(f"bpm: line {line}")
    bpm = int(b''.join(digits).rstrip())
    print(bpm)

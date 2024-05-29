# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from gc import collect


collect()

crlf = {b'\r', b'\n'}

whitespace = {b' ', b'\t'}

accidental_d = {b'_': -1, b'^': 1}

pitch_d = {
    b'C':  0, b'D':  2, b'E':  4, b'F':  5, b'G':  7, b'A':  9, b'B': 11,
    b'c': 12, b'd': 14, b'e': 16, b'f': 17, b'g': 19, b'a': 21, b'b': 23}

beat_len_d = {b'1/4': 0, b'1/8': 1, b'1/16': 2, b'1/32': 3}

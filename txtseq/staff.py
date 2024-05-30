# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from .data import crlf, accidental_d, pitch_d
from .notebuf import add_note
from .util import skip_comment


# Parse a staff line of plaintext music sequencing notation.
# Arguments: 'line', 'ticks', 'ppb', and 'buf' from db
# Results: update'buf' and 'ticks' from db
# CAUTION: This can raise ValueError for syntax errors.
# CAUTION: This includes a hardcoded voice to midi channel mapping!
def parse_staff(voice, f, db):
    line = db['line']
    print(f"{line:2}: {voice+1} ", end='')
    ticks = db['ticks'][voice]
    ppb = db['ppb']
    channel = voice + 10
    state = 0
    chord = None
    note = None
    duration = None
    digits = None
    chord_notes = None
    # Start the state machine
    rewind = f.tell()
    while b := f.read(1):
        if b == b'#':     # Comment works from any state
            skip_comment(f)
            continue
        if state == 0:    # State 0: start of note or chord
            if b in crlf:
                f.seek(rewind)
                break
            elif b == b'|' or b == b'\t' or b == b' ':  # ignore these
                pass
            elif b == b'{':      # chord?
                chord = True
                chord_notes = []
            else:                # start a note (accidental?)
                state = 1
                note = 60        # "C" is MIDI middle C
                digits = []
                if b in accidental_d:
                    note += accidental_d[b]
                else:
                    f.seek(rewind)
        elif state == 1:         # State 1: pitch (required)
            state = 2
            if not b in pitch_d:
                raise ValueError(f"pitch: {b}, line {line}")
            note += pitch_d[b]
        elif state == 2:         # State 2: octave?
            if b == b',':
                note -= 12
            elif b == b"'":
                note += 12
            else:                # end of octave...
                if chord:
                    chord_notes.append(note)
                    if b == b'}':    # end chord?
                        state = 3
                    else:            # more chord notes?
                        state = 0
                        f.seek(rewind)
                else:                # single note
                    state = 3
                    f.seek(rewind)
        elif state == 3:             # State 3: duration?
            if (b'0' <= b <= b'9'):  # digit?
                digits.append(b)
            else:                    # not digit -> record note(s)
                duration = 1
                if digits:
                    duration = int(b''.join(digits))
                    digits = None
                pulses = ppb * duration
                if chord:            # record chord notes
                    for mn in chord_notes:
                        print(f"{ticks}/{mn}/{duration}", end=' ')
                    for mn in chord_notes:
                        add_note(ticks, channel, mn, pulses, db['buf'])
                    chord_notes = None
                    chord = False
                    ticks += pulses
                else:                # record single note
                    print(f"{ticks}/{note}/{duration}", end=' ')
                    add_note(ticks, channel, note, pulses, db['buf'])
                    ticks += pulses
                state = 0            # reset for next note or chord
                f.seek(rewind)
        rewind = f.tell()
    # End of state machine loop
    if chord:
        raise ValueError(f"unclosed chord, line {line}")
    print()
    db['ticks'][voice] = ticks

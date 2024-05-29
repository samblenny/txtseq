# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from gc import collect
from .data import crlf, accidental_d, pitch_d
from .util import skip_comment


# Parse a staff line of plaintext music sequencing notation.
#  expected arguments:
#    voice: 1..4
#    f: binary file
#    line: current line number of f (for debug prints)
#    notes: array of 4 arrays for recording notes
# CAUTION: this can raise ValueError for syntax errors.
#
def parse_staff(voice, f, line, notes):
    print(f"{line:2}: {voice+1} ", end='')
    collect()
    state = 0
    chord = None
    midi_note = None
    duration = None
    digits = None
    chord_notes = None
    # Start the state machine
    rewind = f.tell()
    while b := f.read(1):
        collect()
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
                midi_note = 60   # "C" is MIDI middle C
                digits = []
                if b in accidental_d:
                    midi_note += accidental_d[b]
                else:
                    f.seek(rewind)
        elif state == 1:         # State 1: pitch (required)
            state = 2
            if not b in pitch_d:
                raise ValueError(f"not a pitch: {b}, line {line}")
            midi_note += pitch_d[b]
        elif state == 2:         # State 2: octave?
            if b == b',':
                midi_note -= 12
            elif b == b"'":
                midi_note += 12
            else:                # end of octave...
                if chord:
                    chord_notes.append(midi_note)
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
                collect()            # gc before allocating notes
                if digits:
                    duration = int(b''.join(digits))
                    digits = None
                if chord:            # record chord notes
                    for mn in chord_notes:
                        notes[voice].append((mn, duration))
                    for mn in chord_notes:
                        print(f"{mn}/{duration}", end=' ')
                    chord_notes = None
                    chord = False
                else:                # record single note
                    notes[voice].append((midi_note, duration))
                    print(f"{midi_note}/{duration}", end=' ')
                state = 0            # reset for next note or chord
                f.seek(rewind)
        rewind = f.tell()
    # End of state machine loop
    if chord:
        raise ValueError(f"unfinished chord, line {line}")
    elif state != 0:
        raise ValueError(f"staff ended in state {state}, line {line}")
    print()

# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#
from .util import comment


# Parse a staff line of plaintext music sequencing notation.
# Arguments: 'line', 'ticks', 'ppb', and 'buf' from db
# Results: update db['buf'] and db['ticks'][voice]
# CAUTION: This can raise ValueError for syntax errors.
# CAUTION: This includes a hardcoded voice to midi channel mapping!
def p_staff(voice, f, line, db):
    # preload names to avoid repeated dictionary lookups
    ticks = db['ticks'][voice]
    buf = db['buf']
    ppb = db['ppb']
    p = print
    ri = f.readinto
    tell = f.tell
    seek = f.seek
    pitches = b'CDEFGABcdefgab'
    #               0,  2,  4,  5,  7,  9,  11, 12, 14, 16, 17, 19, 21, 23
    pitch_int = b'\x00\x02\x04\x05\x07\x09\x0b\x0c\x0e\x10\x11\x13\x15\x17'
    pfind = pitches.find

    # Encode note and append it to the array of uint32 ('L' typecode)
    #  arguments:
    #    ticks: note on timestamp in pulses per quarter note
    #    ch: MIDI channel in range 0..15
    #    note: midi note in range 0..127
    #    pulses: note duration in pulses per quarter note
    #    ppb: pulses per beat for calculating gate % time
    #    buf: an array of uint32 created with array.array('L')
    # CAUTION: This includes a hardcoded gate time percentage!
    def add_note(ticks, ch, note, pulses, ppb, buf):
        if not ((0 <= ticks + pulses <= 0xFFFF)
            and (0 <= ch <= 15)
            and (0 <= note <= 127) ):
            raise ValueError('note OOR')  # out of range
        print('%d/%d/%d ' % (ticks, note, pulses), end='')
        # store note on/off events packed as uint32 (omit velocity)
        # 75% gate time ajustment formula...
        # - for notes shorter than 1 beat, subtract 25% of note's pulses
        # - for notes longer than 1 beat, subtract 25% of one beat
        ba = buf.append
        ba((ticks << 16) | ((0x90 | ch) << 8) | note)  # note on
        ba(((ticks + max(1,                            # note off
            pulses - (min(pulses, ppb) // 4)           # gate time adjustment
            )) << 16)
            | ((0x80 | ch) << 8) | note)

    p('%2d: %d ' % (line, voice+1), end='')
    ch = voice + 10
    s = 0       # state
    chord = None
    note = None
    dur = None
    digits = bytearray()
    c_notes = []
    # Start the state machine
    mark = tell()
    b = bytearray(1)
    while ri(b):
        if b == b'#':     # Comment works from any state
            comment(f)
            continue
        if s == 0:    # State 0: start of note or chord
            if b == b'\r' or b == b'\n':  # line end?
                seek(mark)
                break
            elif b == b'|' or b == b'\t' or b == b' ':  # ignore these
                pass
            elif b == b'{':      # chord?
                chord = True
            else:                # start a note (accidental?)
                s = 1
                note = 60        # "C" is MIDI middle C
                if b == b'_':    # flat?
                    note -= 1
                elif b == b'^':  # sharp?
                    note += 1
                else:
                    seek(mark)
        elif s == 1:             # State 1: pitch (required)
            s = 2
            i = pfind(b)  # do fast lookup for C->60, D->62, c->72, etc
            if i < 0:
                raise ValueError(f"pitch: {b}, line {line}")
            note += int(pitch_int[i])
        elif s == 2:                 # State 2: octave?
            if b == b',':
                note -= 12
            elif b == b"'":
                note += 12
            else:                    # end of octave...
                if chord:
                    c_notes.append(note)
                    if b == b'}':    # end chord?
                        s = 3
                    else:            # more chord notes?
                        s = 0
                        seek(mark)
                else:                # single note
                    s = 3
                    seek(mark)
        elif s == 3:                 # State 3: duration?
            if (b'0' <= b <= b'9'):  # digit?
                digits.extend(b)
            else:                    # not digit -> record note(s)
                dur = 1
                if digits:
                    dur = int(digits)
                    digits = bytearray()
                pulses = ppb * dur
                if chord:            # record chord notes
                    for note in c_notes:
                        add_note(ticks, ch, note, pulses, ppb, buf)
                    c_notes = []
                    chord = False
                else:                # record single note
                    add_note(ticks, ch, note, pulses, ppb, buf)
                ticks += pulses
                s = 0                # reset for next note or chord
                seek(mark)
        mark = tell()
    # End of state machine loop
    if chord:
        raise ValueError(f"unclosed chord, line {line}")
    p()
    db['ticks'][voice] = ticks

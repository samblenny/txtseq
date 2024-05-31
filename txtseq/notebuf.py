# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#


# Encode note and append it to the array of uint32 ('L' typecode)
#  arguments:
#    ticks: note on timestamp in pulses per quarter note
#    ch: MIDI channel in range 0..15
#    note: midi note in range 0..127
#    pulses: note duration in pulses per quarter note
#    ppb: pulses per beat for calculating gate % time
#    buf: an array of uint32 created with array.array('L')
# CAUTION: This includes a hardcoded gate time percentage!
#
def add_note(ticks, ch, note, pulses, ppb, buf):
    if not (0 <= ticks + pulses <= 0xFFFF):
        raise Exception('ticks OOR')
    if not (0 <= ch <= 15):
        raise Exception('ch OOR')
    if not (0 <= note <= 127):
        raise Exception('note OOR')
    print(f"{ticks}/{note}/{pulses}", end=' ')
    # store note on/off events packed as uint32 (omit velocity)
    # 75% gate time ajustment formula...
    # - for notes shorter than 1 beat, subtract 25% of note's pulses
    # - for notes longer than 1 beat, subtract 25% of one beat
    ba = buf.append
    ba((ticks << 16) | ((0x90 | ch) << 8) | note)  # note on
    ba(((ticks + max(1,                            # note off
        pulses - (min(pulses, ppb) // 4)           #   gate time adjustment
        )) << 16)
        | ((0x80 | ch) << 8) | note)

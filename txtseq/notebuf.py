# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
#


# Encode note and append it to the array of uint32 ('L' typecode)
#  arguments:
#    ticks: note on timestamp in pulses per quarter note
#    channel: MIDI channel in range 0..15
#    note: midi note in range 0..127
#    pulses: note duration in pulses per quarter note
#    buf: an array of uint32 created with array.array('L')
# CAUTION: This includes a hardcoded gate time percentage!
#
def add_note(ticks, channel, note, pulses, buf):
    if not (0 <= ticks + pulses <= 0xFFFF):
        raise Exception('ticks OOR')
    if not (0 <= channel <= 15):
        raise Exception('channel OOR')
    if not (0 <= note <= 127):
        raise Exception('note OOR')
    print(f"{ticks}/{note}/{pulses}", end=' ')
    note_on  = ((0x90 | channel) << 8) | note  # yes, really omit velocity
    note_off = ((0x80 | channel) << 8) | note
    on_ticks = (ticks << 16)
    off_ticks = (ticks + max(1, int(0.8 * pulses))) << 16  # 80% gate time
    buf.append(on_ticks | note_on)
    buf.append(off_ticks | note_off)  # these get sorted later

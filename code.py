# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from gc import collect, mem_free
from time import monotonic
import usb_midi
from txtseq.sequencer import sequencer
from txtseq.player import Player


# Callback to send raw bytes on the default CircuitPython USB MIDI output port
def midi_tx(data):
    # Doing it this way saves RAM and CPU compared to importing adafruit_midi,
    # which allows for longer songs and tighter timing on SAMD21 boards.
    #
    # If you want to send DIN-5 or TRS MIDI on an IO pin, you could try
    # changing `usb_midi.ports[1]` to a busio.UART object configured to send
    # 31250 baud 8N1 serial on an IO pin.
    usb_midi.ports[1].write(data, len(data))

# Parse plaintext music notation into MIDI events, then play the MIDI events
def main():
    # preload global names (see Damien George's 2018 PyconAU MicroPython talk)
    p = print

    collect()               # Start measuring time and memory use
    a = mem_free()          # a: baseline free mem
    with open('track1.txt', 'rb') as f:
        collect()
        b = mem_free()      # b: free mem before parse
        t = monotonic()     # t: timestamp before parse
        db = sequencer(f)   # Parse the song
        T = monotonic()     # T: timestamp after parse
        collect()
        c = mem_free()      # c: free mem after parse
        p(f'[parse time: %s ms]' % int((T - t) * 1000))
        t = monotonic()     # timestamp before hexdump
        p()
        # Hexdump the array.array('L') of midi events packed as uint32 integers
        for (i, e) in enumerate(db['buf']):
            p(f"{e:08X}", end=' ')
            if i % 10 == 9:
                p()
        p(f'\n[midi event dump time: %s ms]\n' % int((monotonic() - t) * 1000))
        # Print summary of memory use
        p('mem_free:', a, b, c, '  diffs:', a-b, b-c)

        # Play MIDI events
        p('\nPlaying on USB MIDI ch10-13...')
        collect()
        # Player is a generator that is meant to be called frequently to play
        # MIDI events at their scheduled timestamps. The generator yields
        # the remaining ms until its next scheduled MIDI event (idle_ms).
        for idle_ms in Player(db, midi_out_callback=midi_tx, debug=False):
            if idle_ms > 60:
                collect()  # gc.collect() if there's lots of spare time
            if idle_ms > 10:
                # you can do other work here (check buttons or whatever)
                pass
            else:
                pass
        p('Done')


main()

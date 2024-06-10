# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
from board import A0, LED
from digitalio import DigitalInOut, DriveMode, Pull
from gc import collect, mem_free
from time import monotonic, sleep
import usb_midi
from txtseq.sequencer import sequencer
from txtseq.player import Player


# Initialize input pin to control looping playback.
#
# I chose the A0 name here because most Adafruit CircuitPython board
# definititions include board.A0, and it often corresponds to a pin with "A0"
# as its silkscreen. The Trinket M0 is a rare exception with "1~" for A0.
#
def init_loop_pin():
    p = DigitalInOut(A0)  # <-- Change this if you want a different input pin
    p.pull = Pull.UP
    return p

# Initialize LED pin (usually D13) to indicate looping playback is on.
# CAUTION: Some boards don't define board.LED.
def init_LED():
    p = DigitalInOut(LED)
    p.switch_to_output(value=False)
    return p

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
    with open('track2.txt', 'rb') as f:
        collect()
        b = mem_free()      # b: free mem before parse
        t = monotonic()     # t: timestamp before parse
        db = sequencer(f)   # Parse the song
        T = monotonic()     # T: timestamp after parse
        collect()
        c = mem_free()      # c: free mem after parse
        p(f'[parse time: %s ms]' % int((T - t) * 1000))
        # Print summary of memory use
        p('\nmem_free:', a, b, c, '  diffs:', a-b, b-c)

        # Play MIDI events
        p('\nPlaying on USB MIDI ch10-13...')
        collect()
        # This always plays the sequence on the first time through after reset,
        # then it begins watching the loop-mode input pin. To make the sequence
        # play as a loop, close the switch between the loop input pin (A0) and
        # GND. To pause playback, open the switch.
        loop_pin = init_loop_pin()
        loop_led = init_LED()
        first = True
        while True:
            loop_led.value = not loop_pin.value
            if (not first) and loop_pin.value:  # Only loop if loop_pin is low
                sleep(0.01)
                continue
            # Player is a generator that is meant to be called frequently to
            # play MIDI events at their scheduled timestamps. The generator
            # yields the remaining ms until its next scheduled MIDI event
            # (idle_ms).
            for idle_ms in Player(db, midi_out_callback=midi_tx, debug=False):
                if idle_ms > 60:
                    collect()  # gc.collect() if there's lots of spare time
                if idle_ms > 10:
                    # you can do other work here (check buttons or whatever)
                    pass
                else:
                    pass
            first = False


main()

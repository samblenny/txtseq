# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny


# Generator to send timed MIDI event messages from the list in events.
#
# This returns a generator which you should call repeatedly from your event
# loop to send the scheduled MIDI events. The yield value is an integer of ms
# remaining until the next scheduled event. The idea is that, when yield
# returns control to your event loop, you can check how many idle ms are
# available for doing other work without delaying the MIDI event timing.
#
def Player(db, debug=False):
    # Unpack a db object created by .sequencer.sequencer()
    ppb = db['ppb']  # pulses per beat (derived from time unit cmd, U)
    bpm = db['bpm']  # beats per minute (from bpm command, B)
    buf = db['buf']  # array.array('L') uint32 of packed midi events
    # preload a function to get milliseconds
    try:
        # The supervisor module only works on CircuitPython
        # CAUTION: timestamp rolls over at 2**29 ms, with first rollover at
        # 65 s after reset
        from supervisor import ticks_ms  # only works on CircuitPython
        ms = ticks_ms
    except:
        # Fallback to time module which should work anywhere (e.g. mac)
        # CAUTION: time()'s precision degrades on SAMD21 as uptime increases
        from time import monotonic
        ms = lambda: int(monotonic() * 1000)

    # Calculate microseconds per pulse at 24 pulses per beat
    # 60 [s/m] * 1e3 [ms/s] / bpm [beat/m] / 24 [pulse/beat] = n [ms/pulse]
    # 60e3 / bpm / 24 reduces to 2500 / bpm
    mspp = 2500 / bpm    # ms per pulse at 24 pulse per beat
    mask = 0x3fffffff    # (2**29)-1, because ticks_ms rolls over at 2**29
    yield 0              # return generator before sending first event
    t0 = ms()            # first iteration: get epoch timestamp in ms
    t1 = t0
    for e in buf:             # loop over all scheduled MIDI events
        tNext = mspp * (e >> 16)  # convert event time from pulses to ms
        t1 = ((ms() - t0) & mask)
        while tNext > t1:         # yield while not yet time for next event
            yield tNext - t1      # return value is remaining ms
            t1 = ((ms() - t0) & mask)
        # Once scheduled time is reached, send the MIDI message
        if(debug):
            print('%5d ms: %04x' % (t1, ((e & 0xffff) << 8) | 0x64))
        else:
            print('.', end='')

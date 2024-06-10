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
def Player(db, midi_out_callback, debug=False):
    # Unpack a db object created by .sequencer.sequencer()
    ppb = db['ppb']  # pulses per beat (derived from time unit cmd, U)
    bpm = db['bpm']  # beats per minute (from bpm command, B)
    buf = db['buf']  # array.array('L') uint32 of packed midi events
    end = max(db['ticks'])  # length of track (including rests at the end!)
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
    now = t0
    # Expected encoding format of MIDI event packed into uint32:
    # - (e >> 16)       :  timestamp in pulses
    # - (e >>  8) & 0xff:  MIDI status byte (note-on or note-off)
    # - (e      ) & 0xff:  MIDI note data byte (velocity is appended below)
    for e in buf:                   # loop over all scheduled MIDI events
        tNext = mspp * (e >> 16)    # convert event time from pulses to ms
        now = ((ms() - t0) & mask)
        while tNext > now:          # yield while not yet time for next event
            yield tNext - now       # return value is remaining ms
            now = ((ms() - t0) & mask)
        # Once scheduled time is reached, use callback to send MIDI message
        msg = ((e & 0xffff) << 8) | 0x64   # hardcode velocity as 0x64=100
        midi_out_callback(msg.to_bytes(3, 'big'))
        if(debug):
            # Print ms timestamp for this event (for checking latency)
            print(now)
    # If sequence ends on a rest, wait until the end of the rest
    tNext = mspp * end
    now = ((ms() - t0) & mask)
    while tNext > now:
        yield tNext - now
        now = ((ms() - t0) & mask)
    if(debug):
        print(now)

<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2024 Sam Blenny -->
# TxtSeq

**WORK IN PROGRESS (some of this is still a bit aspirational)**

A four track MIDI sequencer using plaintext music notation.

This module is meant to run on CircuitPython boards, providing an alternative
to sequencing with a tracker or laptop and DAW. The point is to make little
MIDI gadgets with tactile controls to help you build and play synth patches.

The sequencer's music notation is loosely based on elements of the [abc music
standard](https://abcnotation.com/wiki/abc:standard:v2.1). Notation for note
pitch, accidentals, octave, and duration is very similar to abc. For everything
else, the sequencer uses a simpler grammar and syntax that is easy to parse on
a microcontroller.


## How to Run the Code

I've been testing this with CircuitPython 9.0.5 on a Trinket M0 (SAMD21), but
it also runs on desktop python3.


### CircuitPython Version

1. Update CircuitPython and bootloader the normal way. (no additional libraries
   are needed)

2. Copy [txtseq](txtseq) module to CIRCUITPY drive (okay to omit `__main__.py`)

3. Copy [code.py](code.py), [boot.py](boot.py), and [track1.txt](track1.txt) to
   CIRCUITPY drive

The parser output should show on the serial console. The numbers on the last
line indicate free memory at different points during loading and parsing of
the song from track1.txt (see code in `code.py`).


### Desktop Version

1. Clone this repo

2. `cd txtseq`

3. `python3 -m txtseq track1.txt`


## On Timing and Polyphony

To support chords, dynamics, and some automation of other control parameters on
a CircuitPython board, this module budgets flash, RAM, and CPU carefully. The
data structures, timing resolution, number of allowed simultaneous voices, and
so on aim to balance expressiveness against resource use.


### MIDI Bandwidth and Timing

By modern standards, MIDI 1.0 over 5-pin DIN connectors is slow. Although USB
MIDI can run faster, I want to plan for a timing budget that can work with
hardware synths using old-style DIN-5 MIDI or the newer TRS equivalents.

DIN-5 and TRS MIDI ports use 31250 baud 8N1 serial:

1. Max data rate is 3125 bytes per second

2. Note-on, note-off, and CC messages are each 3 bytes long

3. Sending 3 bytes takes about 0.960 ms, assuming the device uses firmware that
   can buffer outgoing messages to be sent back to back without gaps.

So, approximately, it takes 1 ms to send 1 MIDI message.


### Polyphony and Human Perception of Audio Latency

Based on browsing a bunch of forum posts of musicians discussing latency for
studio and live performance settings, it seems there's a general opinion that
latency beyond about 10 ms begins to "feel wrong" and seriously complicate the
task of playing live music in time with other musicians. Some people believe
latency lower than 10 ms (2-5 ms?) is important for percussion instruments to
sound on beat. Some people believe that latency much higher than 10 ms can be
acceptable for instruments with a slow attack (organ, pads, etc).

For perspective, the speed of sound in air is approximately 340 m/s, which
works out to sound traveling 1 foot in 1 ms. So, a group of musicians playing
acoustic instruments less than 10 feet away from each other should experience
latencies under 10 ms. On the other hand, an orchestra seated across a 50 foot
wide stage could experience latencies up to 50 ms. But, since orchestras keep
time visually by watching a conductor's baton, it can still work.

Similar principles apply to bands performing modern music on large stages. Each
performer usually has their own monitor speaker or in-ear monitors. With the
monitors receiving audio over copper wires or radio waves, the signals
propagate at something like 0.6c to 0.99c (see
[speed of light](https://en.wikipedia.org/wiki/Speed_of_light) and
[velocity factor](https://en.wikipedia.org/wiki/Velocity_factor)). That works
out to around 112 to 184 miles per 1 ms, so the link latency is very low.

The point is that, to make a MIDI gadget that would be suitable for use in live
performances, aiming for MIDI link latency of 5 ms or less under normal
conditions would probably be worth the trouble.


### Priority Scheduling of MIDI Messages

For a MIDI link that can move 1 message per 1 ms, playing a chord of 3 notes
would take 3 ms to send. If the chord was meant to play on the same beat as a
drum strike and a CC update, the whole group would take 5 ms to send. But, if
the drum messages get sent first, the timing will sound tighter.

Considering that low latency matters more for percussion, giving scheduling
priority to messages for the percussion channel should help to make the most of
available MIDI bandwidth.


## System Architecture Plan

My plan for a system to get good timing resolution using limited resources...

1. Provide notation that can represent up to 4 simultaneous voices, each with
   its own MIDI channel.

   For example, it should be possible to write that voice 1 has a kick drum on
   measure 1, beat 1, and that voice 2 has the openning note of a bass line
   starting on that same beat. Voice 1 could play on MIDI channel 10, and voice
   2 could use channel 2 (or 3, or whatever).

2. Provide notation for polyphony within a voice (chords). For example, a chord
   of 3 notes would get sent as a series of 3 note-on messages, then 3 note-off
   messages after a delay, with all the messages using the same channel.

3. Assign scheduling priority by voice number, with the lowest voice getting
   highest priority. For example, to get the tightest drum timing, you can put
   percussion on voice 1.

4. Store MIDI events as list of list, list of tuple, or list of namedtuple,
   because those all take much less CircuitPython RAM compared to a list of
   class instances.

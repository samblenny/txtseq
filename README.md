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


### Example Output

This is from running `code.py` on a Trinket M0 with CircuitPython 9.0.5:

```
 3: ppb=12
 4: bpm=140
 9: 1 0/60/24 24/62/24 48/64/24 72/65/24 96/67/24 120/69/24 144/71/24 168/72/24
10: 2 0/48/192
12: 1 192/71/24 216/69/24 240/67/24 264/65/24 288/64/24 312/62/24 336/60/48
13: 2 192/48/96 288/84/96
15: 1 384/60/48 384/62/48 384/67/48 432/69/48 432/60/48 432/62/48 480/60/24 504/60/24 528/62/24 552/67/24
16: 2 384/47/96 480/58/96
[parse time: 210 ms]

00009A3C 00158A3C 00189A3E 002D8A3E 00309A40 00458A40 00489A41 005D8A41
00609A43 00758A43 00789A45 008D8A45 00909A47 00A58A47 00A89A48 00BD8A48
00009B30 00BD8B30 00C09A47 00D58A47 00D89A45 00ED8A45 00F09A43 01058A43
01089A41 011D8A41 01209A40 01358A40 01389A3E 014D8A3E 01509A3C 017D8A3C
00C09B30 011D8B30 01209B54 017D8B54 01809A3C 01AD8A3C 01809A3E 01AD8A3E
01809A43 01AD8A43 01B09A45 01DD8A45 01B09A3C 01DD8A3C 01B09A3E 01DD8A3E
01E09A3C 01F58A3C 01F89A3C 020D8A3C 02109A3E 02258A3E 02289A43 023D8A43
01809B2F 01DD8B2F 01E09B3A 023D8B3A
[midi event dump time: 42 ms]

mem_free: 12096 12000 11696   diffs: 96 304
```

1. The top section has debug print output from the parsing functions.

2. The middle section is a dump of the array of timestamped midi events
   created by the note parsing code. (not sorted by timestamp yet)

3. The last line summarizes `mem_free()` measurements. (see `code.py`)


## Reading the Code

1. The [txtseq](txtseq) module exports a function,
   [`sequencer(f)`](txtseq/sequencer.py) which expects its argument, `f`, to be
   a binary mode file object (e.g. `open('some-song.txt', 'rb')`). For usage
   examples, see [`code.py`](code.py) or
   [`txtseq/__main__.py`](txtseq/__main__.py).

2. The `seqencer()` function parses its input file to find top level commands,
   which it then uses to call further parsing functions. For example, the
   commands `1`, `2`, `3`, and `4` call the [`p_staff()`](txtseq/staff.py)
   function. The numbers correspond to each of the four voices (tracks).

3. To get all the parser code to compile and run on a SAMD21, the module is
   split into several files of mostly less than 100 lines. The parsing style is
   based on state machine loops that examine one byte at a time. When one of
   the parser functions or state if-branches recognizes a byte that should be
   processed by a different function or state branch, it will mark the file's
   cursor position by one byte using the `f.seek(mark)` idiom.

4. The [`txtseq/util.py`](txtseq/util.py) file holds parsing functions for
   dealing with comments (`# ...`), semantically irrelevant whitespace, and
   setting of header options (`B` for bpm, `U` for time unit)

5. Parsing of note pitch and duration for staff lines happens in the
   `p_staff()` function of [`txtseq/staff.py`](txtseq/staff.py).

   Currently, I'm packing note on and off events as uint32 values in an
   `array.array('L')`. The most significant 16 bits have a timestamp (units of
   MIDI pulses per quarter note). The low 16 bits have MIDI status and data
   bytes. This allows for adding note events one voice at a time without
   worrying about out-of-order events. My plan is to do an in-place sort at the
   end to merge all the events from different voices into one list ordered by
   ascending timestamps (similar to an SMF format 0 file).


## Music Notation Grammar and Syntax

For examples of how the plaintext music notation works, check out the comments
in [`track1.txt`](track1.txt).

The ASCII note transcription style used here is loosely based on the abc music
standard, but the two notations are not compatible. In particular, this
notation uses `{}` for chords, requires chord durations to be specified after
the closing `}`, and omits a lot of abc's features such as configurable key
signature.

The short summary:

- Single note: `<accidental><pitch><octave><duration>` (e.g. `C` `_B,` `c2`)

- Chord note: `<accidental><pitch><octave>`

- Chord: `{<chord note><chord note>...}<duration>` (e.g. `{C^DA}4` `{ceg}`)

- Accidental: `_` (flat), `^` (sharp), or the empty string (natural)

- Note: `C D E F G A B c d e f g a b` (`C` is middle-c, `c` is 1 octave up)

- Octave: `,` (lower by 1 octave), `'` (raise by one octave), repeated commas
  or single-quotes are cumulative (`,,` lowers 2 octaves, `'''` raises by 3).
  Examples: `C,,,`  `d'`

- Duration: An integer representing the length of a note or chord as a multiple
  of the current time unit. Duration is optional with a default value of 1.
  With the time unit set for `1/8`, `C2` would mean a quarter note of middle-c,
  and `C` would be an eighth note.

- Staff: staff lines start with a voice number then have an arbitrary sequence
  of whitespace, bar lines (`|`), notes, and chords. Bar lines and whitespace
  are ignored by the parser, but you can use them to help organize your notes
  for better readability. It's fine to make long notes that last for more than
  one measure (e.g. `C,16` with time unit set to `1/8` would be played the same
  as 2 tied whole notes in 4/4 time)

  Example: `1 | {CDG}4 {ACD}4 | C2 C2 D2 G2 |`

  For more examples, see [`track1.txt`](track1.txt)


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

4. Store MIDI events packed as integers in an `array.array('L')` to save memory
   compared to regular lists of objects.

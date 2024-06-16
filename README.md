<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2024 Sam Blenny -->
# TxtSeq

A tiny 4-voice plaintext midi sequencer for CircuitPython.

This module is meant to run on CircuitPython boards, providing an alternative
to sequencing with a tracker or laptop and DAW. The point is to make little
MIDI gadgets with tactile controls to help you build and play synth patches.

The sequencer's music notation is loosely based on elements of the [abc music
standard](https://abcnotation.com/wiki/abc:standard:v2.1). Notation for note
pitch, accidentals, octave, and duration is very similar to abc. For everything
else, the sequencer uses a simpler grammar and syntax that is easy to parse on
a microcontroller.


### For Adafruit Playground Guide Readers

If you found your way here by way of the
[Tiny Plaintext MIDI Sequencer for SAMD21](https://adafruit-playground.com/u/SamBlenny/pages/tiny-plaintext-midi-sequencer-for-samd21)
page on the Adafruit Playground site, that writeup refers to the sequencer code
as of release v0.2.1. By the time you read this, the sequencer code here may
have evolved a bit. If you want to see the state of this project at the time I
wrote the Playground guide, take a look at:
- [v0.2.1 README and code browser](https://github.com/samblenny/txtseq/tree/v0.2.1)
- [v0.2.1 Release page](https://github.com/samblenny/txtseq/releases/tag/v0.2.1)


### CircuitPython + GarageBand Audio Demo

To hear what the commit 9c73ec4 version of
[`track1.txt`](https://github.com/samblenny/txtseq/blob/9c73ec461f7b4e2ec9c85522e71e7e66b72405bd/track1.txt)
sounds like when played from a Trinket M0 over USB MIDI into a MIDI drum
instrument in GarageBand, you can listen to
[`demos/track1-180bpm.mp3`](demos/track1-180bpm.mp3).


## Hardware and Looping Playback

I developed the sequencer on a Trinket M0 (non-Express SAMD21) to make sure it
would be small and fast. While I haven't tested on other CircuitPython boards,
probably the code will run fine, as long as you use a board that supports USB
MIDI. If you want to use hardwired DIN-5 or TRS MIDI, take a look at the
`midi_tx()` callback function defined in `code.py`.

The current `code.py` configures `board.A0` (silkscreen `1~` on Trinket M0) as
a digital input to control looping playback. If you don't connect anything to
`A0`, the sequence will play through once when the code loads. If you connect
`A0` to `GND`, the sequence plays in a loop.


## How to Run the Code

I've been testing this with CircuitPython 9.0.5 on a Trinket M0 (SAMD21), but
most of the code (all but MIDI out) also runs on desktop python3.


### CircuitPython Version

1. Prepare a host computer with something that can play sounds for incoming
   USB MIDI notes on channels 10, 11, 12, and 13. For example, on macOS, you
   can use the GarageBand app by adding a MIDI track to an empty project. If
   you only care about drum parts, you could try my browser-based drum synth,
   [web-midi-drumkit](https://samblenny.github.io/web-midi-drumkit/) (requires
   Chrome browser for WebMIDI support).

2. Update CircuitPython and bootloader
   [the normal way](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython).
   (no additional libraries are needed)

3. Copy [txtseq](txtseq) module to CIRCUITPY drive (okay to omit `__main__.py`)

4. Copy [code.py](code.py), [boot.py](boot.py), and [track2.txt](track2.txt) to
   CIRCUITPY drive

When `code.py` runs, it will parse music notation from `track2.txt` into an
array of MIDI note event data, then start playing the notes over USB MIDI. The
parser and playback code print a variety of debug info to the serial console to
help with measuring memory and CPU use along with MIDI playback latency.


### Desktop Version

This will give debug prints only, without actual MIDI playback. But, you could
easily modify the code to use a library that is capable of sending MIDI. (see
definition of `midi_tx(data)` callback in `txtseq/__main__.py`)

1. Clone this repo

2. `cd txtseq`

3. `python3 -m txtseq track2.txt`


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

   Note on and off events generated by the parser get packed as uint32 values
   in an `array.array('L')`. The most significant 16 bits have a timestamp
   (units of MIDI pulses). The low 16 bits have MIDI status and data bytes.
   This allows for adding note events one voice at a time without worrying
   about out-of-order events. I sort the array at the end to merge all the
   events from different voices into one list ordered by ascending timestamps.

3. To get all the parser code to compile and run on a SAMD21, the module is
   split into several files of less than 150 lines each. Also, I used several
   MicroPython optimization techniques from Damien George's 2018 PyCon AU talk,
   "Writing fast and efficient MicroPython".

4. The [`txtseq/util.py`](txtseq/util.py) file holds parsing functions for
   dealing with comments (`# ...`), semantically irrelevant whitespace, and
   setting of header options (`B` for bpm, `U` for time unit)

5. Parsing of note pitch and duration for staff lines happens in the
   `p_staff()` function of [`txtseq/staff.py`](txtseq/staff.py).

   The parsing style is based on state machine loops that examine one byte at a
   time, reading bytes with `readinto()` to limit heap allocations. When one of
   the parser functions or state machine branches recognizes a byte that should
   be processed by a different function or state branch, it will rewind the
   file's cursor position by one byte using the `f.seek(mark)` idiom.

6. Playback uses a generator defined in [`txtseq/player.py`](txtseq/player.py).
   By using the generator as the iterator for an event loop, it's easy to run
   your own code interleaved with the MIDI player (see `main()` in `code.py`).
   Also, holding playback state in the local scope of a generator makes it
   possible to avoid many heap allocations and dictionary lookups that would
   add jitter and latency if the MIDI player used a class instance.


## Music Notation Grammar and Syntax

For examples of how the plaintext music notation works, check out the comments
in [`track2.txt`](track2.txt).

The ASCII note transcription style used here is loosely based on the abc music
standard, but the two notations are not compatible. In particular, this
notation uses `{}` for chords, requires chord durations to be specified after
the closing `}`, and omits a lot of abc's features such as configurable key
signature.

The short summary:

- Single note: `<accidental><pitch><octave><duration>` (e.g. `C` `_B,` `c2`)

- Rest: `z<duration>` (e.g. `z` `z2` `z16`)

- Chord note: `<accidental><pitch><octave>`

- Chord: `{<chord note><chord note>...}<duration>` (e.g. `{C^DA}4` `{ceg}`)

- Accidental: `_` (flat), `^` (sharp), or the empty string (natural)

- Note: `C D E F G A B c d e f g a b` (`C` is middle-c, `c` is 1 octave up)

- Note aliases: you can use some shorter aliases to write percussion parts:
  `h` for `^F _G` (closed hi-hat), `H` for `_B ^A` (open hi-hat), and `r` for
  `_e ^d` (ride cymbal)

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

  Example: `2 | {CDG}4 {ACD}4 | C2 C2 D2 G2 |`

  For more examples, see [`track1.txt`](track1.txt) and
  [`track2.txt`](track2.txt)


### Setting BPM and Time Unit

The `B` command sets bpm, which is a global setting that gets applied during
playback. For example, a line with `B 120` would set the playback speed to 120
beats per minute.

The `U` command sets the time unit, which relates to the duration numbers. For
example, You can set the time unit to 1 eighth note with a `U 1/8` command. In
that case, if you wrote `C2` in a staff, that note's duration would be 2 eighth
notes (1 quarter note). Or, for quarter note triplets, you could use the `U
1/4T` command. In that case, the duration of a `C2` would be 2/3 of one quarter
note.

The time unit options are: `1/4`, `1/8`, `1/16`, `1/32`, `1/4T`, `1/8T`,
`1/16T`, and `1/32T`.


### Bass Clef Percussion Notes on Voice 1

The General MIDI standard includes a mapping of percussion sounds for MIDI
channel 10, notes 35 to 81. The sounds for a typical Western drum kit (kick,
snare, hi-hat, cymbal, etc) use notes in the bass clef, starting approximately
2 octaves below middle C. To avoid having to write things like `B,,,` or `C,,`
every time you want a kick drum, voice 1 uses bass clef note names.

Bass clef note names are 2 octaves (24 MIDI notes) lower than the equivalent
treble clef note names. So, bass clef `C` is the same MIDI note as `C,,` in
treble clef.

Also, because the hi-hats and ride cymbal would otherwise need to be spelled
with a flat or sharp prefix, I included the aliases `h`, `H`, and `r`. For
quick reference, these are the notes for some common drum sounds:

| Bass Note | MIDI # | Sound               |
| --------- | ------ | ------------------- |
|  C        | 36     | Electric Bass Drum  |
|  E        | 40     | Electric Snare      |
| ^F _G h   | 42     | Closed Hi-Hat       |
| _B ^A H   | 46     | Open Hi-Hat         |
| _e ^d r   | 51     | Ride Cymbal         |


### Priority Scheduling of MIDI Messages

For a MIDI link that can move 1 message per 1 ms, playing a chord of 3 notes
would take 3 ms to send. If the chord was meant to play on the same beat as a
drum strike and a CC update, the whole group would take 5 ms to send. But, if
the drum messages get sent first, the timing will sound tighter.

Considering that low latency matters more for percussion, giving scheduling
priority to messages for the percussion (usually MIDI channel 10) should help
to make the most of available MIDI bandwidth.

To allow for efficient percussion-priority sorting of MIDI events, I hardcoded
the player to use the following txtseq voice to MIDI channel mapping:

| voice | MIDI channel | Scheduling Priority |
| ----- | ------------ | ------------------- |
| 1     | 10           | 1                   |
| 2     | 11           | 2                   |
| 3     | 12           | 3                   |
| 4     | 13           | 4                   |


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

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


## How to Run the Code

I've been testing this with CircuitPython 9.0.5 on a Trinket M0 (SAMD21), but
most of the code (all but MIDI out) also runs on desktop python3.


### CircuitPython Version

1. Prepare a host computer with something that can play sounds for incoming
   USB MIDI notes on channels 10, 11, 12, and 13. For example, on macOS, you
   can use the GarageBand app by adding a MIDI track to an empty project.

2. Update CircuitPython and bootloader the normal way. (no additional libraries
   are needed)

3. Copy [txtseq](txtseq) module to CIRCUITPY drive (okay to omit `__main__.py`)

4. Copy [code.py](code.py), [boot.py](boot.py), and [track1.txt](track1.txt) to
   CIRCUITPY drive

When `code.py` runs, it will parse music notation from `track1.txt` into an
array of MIDI note event data, then start playing the notes over USB MIDI. The
parser and playback code print a variety of debug info to the serial console to
help with measuring memory and CPU use along with MIDI playback latency.

#### Audio Demo

To hear what track1.txt sounds like (as of
[commit 9c73ec4](https://github.com/samblenny/txtseq/commit/9c73ec461f7b4e2ec9c85522e71e7e66b72405bd))
when played through a MIDI drum instrument in GarageBand, you can listen to
[`demos/track1-180bpm.mp3`](demos/track1-180bpm.mp3).


### Desktop Version

This will give debug prints only, without actual MIDI playback. But, you could
easily modify the code to use a library that is capable of sending MIDI. (see
definition of `midi_tx(data)` callback in `txtseq/__main__.py`)

1. Clone this repo

2. `cd txtseq`

3. `python3 -m txtseq track1.txt`


### Example Output

This is from running `code.py` on a Trinket M0 with CircuitPython 9.0.5:

```
10: ppb=4
11: bpm=180
19: 1 ................
20: 1 ...................
21: 1 ...............................
22: 1 ................
23: 1 ...................
24: 1 ......................
[parse time: 517 ms]

00009924 00078924 0010992A 0017892A 00189924 001F8924 0028992E 002F892E 00309928 00378928
0040992A 0047892A 00489924 004F8924 0058992E 005F892E 00609924 00678924 0070992A 0077892A
00789924 007F8924 0088992E 008F892E 00909928 00978928 00A0992A 00A7892A 00A89924 00AF8924
00B8992E 00BF892E 00C09924 00C78924 00D0992A 00D7892A 00D89924 00DF8924 00E8992E 00EF892E
00F09928 00F78928 0100992A 0107892A 01089924 010F8924 0118992E 011F892E 01209924 0120992E
01278924 0127892E 0128992A 012F892A 0130992E 0137892E 01389924 013F8924 0140992E 0147892E
0148992A 014F892A 01509928 01578928 0160992A 0167892A 01689924 016F8924 01789924 017F8924
01809924 01838924 01849924 01878924 01889924 018B8924 018C9924 018F8924 01909924 01938924
01949924 01978924 01989924 019B8924 019C9924 019F8924 01A09924 01A38924 01A49924 01A78924
01A89924 01AB8924 01B09933 01B38933 01B49933 01B78933 01B89933 01BB8933 01BC9933 01BF8933
01C09933 01C38933 01C49933 01C78933 01C89933 01CB8933 01CC9933 01CF8933 01D09933 01D38933
01D49933 01D78933 01DC9924 01DF8924 01E09924 01E38924 01E49924 01E78924 01E89924 01EB8924
01EC9924 01EF8924 01F09924 01F38924 01F49924 01F78924 01F89924 01FB8924 01FC9924 01FF8924
02049931 020F8931 02109924 02178924 0220992A 0227892A 02289924 022F8924 0238992E 023F892E
02409928 02478928 0250992A 0257892A 02589924 025F8924 0268992E 026F892E 02709924 02778924
0280992A 0287892A 02889924 028F8924 0298992E 029F892E 02A09928 02A78928 02B0992A 02B7892A
02B89924 02BF8924 02C8992E 02CF892E 02D09924 02D78924 02E0992A 02E7892A 02E89924 02EF8924
02F8992E 02FF892E 03009928 03078928 0310992A 0317892A 03189924 031F8924 0328992E 032F892E
03309924 0330992E 03378924 0337892E 0338992A 033F892A 0340992E 0347892E 03489924 034F8924
0350992E 0357892E 0358992A 035F892A 03609928 03678928 0370992A 0377892A 03789924 037F8924
03889924 038F8924 03909924 03938924 03949924 03978924 03989924 039B8924 039C9924 039F8924
03A09924 03A38924 03A49924 03A78924 03A89924 03AB8924 03AC9924 03AF8924 03B09924 03B38924
03B49924 03B78924 03B89924 03BB8924 03C09933 03C38933 03C49933 03C78933 03C89933 03CB8933
03CC9933 03CF8933 03D09933 03D38933 03D49933 03D78933 03D89933 03DB8933 03DC9933 03DF8933
03E09933 03E38933 03E49933 03E78933 03F09931 03FB8931
[midi event dump time: 191 ms]

mem_free: 10976 10880 9728   diffs: 96 1152

Playing on USB MIDI ch10-13...
Done
```

1. The top section has debug print output from the parsing functions.

2. The second section is a dump of the array of timestamped midi events
   created by the note parsing code.

3. The third section summarizes `mem_free()` measurements. (see `code.py`)

4. The last section has debug prints from the MIDI event player.


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
in [`track1.txt`](track1.txt).

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

  For more examples, see [`track1.txt`](track1.txt)


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


## System Architecture Plan

My plan for a system to get good timing resolution using limited resources...

1. Provide notation that can represent up to 4 simultaneous voices, each with
   its own MIDI channel.

   For example, it should be possible to write that voice 1 has a kick drum on
   measure 1, beat 1, and that voice 2 has the openning note of a bass line
   starting on that same beat.

2. Provide notation for polyphony within a voice (chords). For example, a chord
   of 3 notes would get sent as a series of 3 note-on messages, then 3 note-off
   messages after a delay, with all the messages using the same channel.

3. Assign scheduling priority by voice number, with the lowest voice getting
   highest priority. For example, to get the tightest drum timing, you can put
   percussion on voice 1.

4. Store MIDI events packed as integers in an `array.array('L')` to save memory
   compared to regular lists of objects. This works for note on and off events
   with a very straightforward encoding, as long as I always send the velocity
   as a hardcoded constant. MIDI CC messages would be a hassle to pack into
   uint32, so I won't worry about those for now.

#!/bin/sh
# Begin by clearing extended attributes from source files because, if they
# exist, macOS rsync seems to always attempt to copy them to CIRCUITPY.
xattr -cr txtseq track1.txt
rsync -rcvO --delete --exclude="__main__.py" txtseq/ /Volumes/CIRCUITPY/txtseq
rsync -cvO track1.txt /Volumes/CIRCUITPY/track1.txt
# Redundantly attempt to delete previously copied ._ extended attribute files
xattr -cr /Volumes/CIRCUITPY/txtseq
sync

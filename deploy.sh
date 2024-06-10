#!/bin/sh
# Begin by clearing extended attributes from source files because, if they
# exist, macOS rsync seems to always attempt to copy them to CIRCUITPY.
xattr -cr txtseq track*.txt code.py
xattr -cr /Volumes/CIRCUITPY/*
rsync -rcvO --delete --exclude="__main__.py" txtseq/ /Volumes/CIRCUITPY/txtseq
rsync -cvO track*.txt code.py /Volumes/CIRCUITPY
sync

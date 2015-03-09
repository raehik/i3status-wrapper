#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Insert more information into the i3status line.
#
# To use, ensure your i3status config (default '~/.i3status.conf')
# contains:
#
#     output_format = "i3bar"
#
# in the 'general' section. Then in your i3 config (default
# '~/.i3/config'):
#
#     status_command i3status | i3status-wrapper.py
#
# in the 'bar' section.
#
# Originally a Python rewrite of a Perl wrapper
# (http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl)
# by Valentin Haenel, heavily adapted by me (raehik).
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
# © 2014 Ben Orchard <thefirstmuffinman@gmail.com>
#
# This program is free software. It comes without any warranty, to the
# extent permitted by applicable law. You can redistribute it and/or
# modify it under the terms of the Do What The Fuck You Want To Public
# License (WTFPL), Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import json
import sys
import subprocess
import os
import re

mpd_symbol = "♬"
mpd_playing = mpd_symbol + "  %s"
mpd_stopped = "&lt;" + mpd_symbol +"  stopped>"

vol_colour = "#6666FF"
mpd_play_colour = "#AA5500"
mpd_stop_colour = "#555555"

def run_command(arg_list):
    """Run a command, returning the output and the error code."""
    proc = subprocess.Popen(arg_list, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode("utf-8").strip()

def alsa_percent():
    """Get the volume of the master ALSA device as a (mapped) percent."""
    # -M: "Use the mapped volume for evaluating the percentage
    #      representation like alsamixer, to be more natural for human
    #      ear."
    # whatever that means!
    out = run_command(["amixer", "-M", "get", "Master"])

    p = re.compile("[0-9]*%")
    percent = p.search(out)
    return percent.group()

def mpd_current_song():
    """Get the current MPD song."""
    song = ''

    artist = run_command(["mpc", "current", "-f", "%artist%"])
    if artist != '':
        song = artist + " - "

    title = run_command(["mpc", "current", "-f", "%title%"])
    if title == '':
        title = os.path.basename(
                  run_command(["mpc", "current", "-f","%file%"]))

    song += title
    return song

def print_line(message):
    """Non-buffered printing to stdout."""
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """Interrupted respecting reader for stdin."""
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

# Skip the first line which contains the version header.
print_line(read_line())

# The second line contains the start of the infinite array.
print_line(read_line())

while True:
    line, prefix = read_line(), ''

    # ignore lines starting with a comma (see docs)
    if line.startswith(','):
        line, prefix = line[1:], ','

    # grab the line in json format
    j = json.loads(line)

    j.insert(0,
        {'full_text': alsa_percent(),
         'color': vol_colour})

    song = mpd_current_song()

    # insert information into the start of the json, but could be anywhere
    if song == '':
        j.insert(0,
            {'full_text': mpd_stopped,
             'color': mpd_stop_colour})
    else:
        j.insert(0,
            {'full_text': mpd_playing % song,
             'color': mpd_play_colour})

    #j[-1]['color'] = '#888888'

    # and echo back new encoded json
    print_line(prefix+json.dumps(j))

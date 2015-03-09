#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Insert more information into the i3status line.
#
# To use, ensure your i3status config (default '~/.i3status.conf' or
# '~/.config/i3status/config') contains:
#
#     output_format = "i3bar"
#
# in the 'general' section. Then in your i3 config (default
# '~/.i3/config' or '~/.config/i3status/config'):
#
#     status_command i3status | i3status-wrapper.py
#
# in the 'bar' section.
#
# Originally a Python rewrite of a Perl wrapper
# (http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl)
# by Valentin Haenel, rewritten by raehik.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
# © 2014 Ben Orchard <thefirstmuffinman@gmail.com>
#
# This program is free software. It comes without any warranty, to the
# extent permitted by applicable law. You can redistribute it and/or
# modify it under the terms of the Do What The Fuck You Want To Public
# License (WTFPL), Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import mpd

import json
import sys
import subprocess
import os
import re

class i3WrapperHelper:
    JSON_START = 0
    TEXT = "full_text"
    COLOUR = "color"
    HOST = "localhost"
    MPD_PORT = 6600

    def __init__(self):
        # skip first line (version header)
        print_line(read_line())

        # skip second line (empty, start of streaming array)
        print_line(read_line())



    def run_command(self, arg_list):
        """Run a command, returning the output."""
        proc = subprocess.Popen(arg_list, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.decode("utf-8").strip()

    def alsa_percent(self):
        """Get the volume of the master ALSA device as a (mapped) percent."""
        # -M: "Use the mapped volume for evaluating the percentage
        #      representation like alsamixer, to be more natural for
        #      human ear."
        # whatever that means!
        out = run_command(["amixer", "-M", "get", "Master"])

        # grab the percentage part & return
        r = re.compile("[0-9]*%")
        percent = r.search(out).group()
        return percent

    def connect(self):
        """Connect to MPD."""
        client.connect(HOST, MPD_PORT)

    def disconnect(self):
        """Disconnect from MPD."""
        client.disconnect()

    def mpd_song_desc(self):
        """Return a description of the current MPD song."""
        self.connect()

        song = client.currentsong()

        if song['artist'] != '':
            song_string = song['artist'] + " - "

        if song['title'] != '':
            song_string += song['title']
        else:
            song_string += os.path.basename(song['file'])

        self.disconnect()
        return song_string

    def mpd_state(self):
        """Return a text string showing MPD's state."""
        self.connect()

        state = client.status()['state']

        self.disconnect()
        return state

    def print_line(message):
        """Print to stdout."""
        sys.stdout.write(message + '\n')
        sys.stdout.flush()

    def read_line():
        """Return a line from stdin, respecting Ctrl-C interruptions."""
        try:
            # try to read a line, removing any extra whitespace
            line = sys.stdin.readline().strip()

            # EOF or empty line received
            if not line:
                sys.exit(3)
            return line
        # exit on ctrl-c
        except KeyboardInterrupt:
            sys.exit()

    def insert(self, text, colour="", pos=JSON_START):
        bar.insert(pos, {
            TEXT: text
            COLOUR: colour
            })

    def run(self):
        while True:
            line = read_line

            # if line starts with comma, start from after it (why?)
            if line.startswith(','):
                line, prefix = line[1:], ','

            # grab the line in json format
            j = json.loads(line)

            helper.insert(helper.alsa_percent(), vol_colour)
            j.insert(0, {
                TEXT: alsa_percent(),
                COLOUR : vol_colour
                })

            song = mpd_song_desc()
            status = mpd_status()

            # insert info into json
            if song == '':
                j.insert(0, {
                    TEXT: mpd_stopped,
                    COLOUR: mpd_stop_colour
                    })
            else:
                j.insert(0, {
                    TEXT: mpd_playing % song,
                    COLOUR: mpd_play_colour
                    })

            # 'retroactively' apply colours to earlier parts
            #j[-1]['color'] = '#888888'

            # echo back new encoded json
            print_line(prefix+json.dumps(j))



mpd_symbol = "♬"
mpd_playing = mpd_symbol + "  %s"
mpd_stopped = "<" + mpd_symbol +"  stopped>"

vol_colour = "#6666FF"
mpd_play_colour = "#AA5500"
mpd_pause_colour = mpd_play_colour
mpd_stop_colour = "#555555"



helper = i3WrapperHelper()

helper.run()


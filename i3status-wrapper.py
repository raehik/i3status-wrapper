#!/usr/bin/env python
#
# Edit i3status's line.
#

import sys
from os.path import basename
import json

from mpd import (MPDClient, CommandError, ConnectionError)
from socket import error as SocketError

class i3Wrapper:
    BROWN = "#AA5500"
    GREY = "#555555"
    BLUE = "#6666FF"

    host = "localhost"
    port = "6600"

    vol_pos = 0
    vol_color = BLUE

    text_play = "♬  {artist}{name}"
    color_play = BROWN
    text_pause = text_play
    color_pause = GREY
    text_stop = "<♬  stopped>"
    color_stop = GREY
    text_off = "<♬  off>"
    color_off = GREY
    color_error = GREY

    def __init__(self):
        """Initialise the wrapper."""
        self.__init_statusline()
        self.__mpd_connect()

    def print_line(self, line):
        """Print to stdout & flush the buffer."""
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def __init_statusline(self):
        """Get the header lines from i3status out of the way."""
        # print first line (version header)
        self.print_line(self.__next_line())

        # print second line (start of infinite array)
        self.print_line(self.__next_line())

    def __next_line(self):
        """Get the next line from stdin, respecting interrupts."""
        # try to get the next line, exiting if cancelled
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            sys.exit(1)

        if not line:
            # EOF or empty line received
            sys.exit(2)

        return line

    def __mpd_connect(self):
        """Try to connect to an MPD instance on a specified socket."""
        self.client = MPDClient()
        try:
            self.client.connect(host=self.host, port=self.port)
        except ConnectionRefusedError:
            pass

    def mpd_status(self):
        """Insert a part with info about MPD's current status."""
        # try to get song & status info
        try:
            song = self.client.currentsong()
            status = self.client.status()["state"]
        except:
            self.__mpd_connect()
            self.insert_part(self.form_part(self.text_off, self.color_error))
            return

        # set colour & format based on MPD status
        if status == "play":
            text = self.text_play
            color = self.color_play
        elif status == "pause":
            text = self.text_pause
            color = self.color_pause
        elif status == "stop":
            # if we're stopped, exit before trying to get info
            text = self.text_stop
            color = self.color_stop
            self.insert_part(self.form_part(text, color))
            return

        # get info about song (to use in formatting)
        info = {}
        info["file"] = basename(song["file"])

        try:
            info["artist"] = song["artist"] + " - "
        except KeyError:
            # song has no artist set, so none
            info["artist"] = ""

        try:
            info["title"] = song["title"]
            info["name"] = song["title"]
        except KeyError:
            # song has no title set, so use filename instead
            info["title"] = ""
            info["name"] = info["file"]

        # replace format parts with actual values
        # e.g. {artist} -> info["artist"]
        for key, value in info.items():
            text = text.replace("{" + key + "}", value)

        part = self.form_part(text, color)
        self.insert_part(part)

    def alsa_color(self):
        """Insert colour into the ALSA volume display part."""
        self.line[self.vol_pos]["color"] = self.vol_color

    def get_json(self):
        line = self.__next_line()
        prefix = ""

        # ignore lines starting with a comma (see docs)
        if line.startswith(","):
            line = line[1:]
            prefix = ","

        j = json.loads(line)

        return j, prefix

    def form_part(self, text, color):
        part = {}

        part["full_text"] = text
        part["color"] = color

        return part

    def insert_part(self, part, pos=0):
        self.line.insert(pos, part)

    def start(self):
        while True:
            # get next line & parse it as JSON
            self.line, prefix = self.get_json()

            # run insertion functions
            # note that they must be in a certain order!
            self.alsa_color()
            self.mpd_status()

            # print line
            self.print_line(prefix + json.dumps(self.line))



if __name__ == "__main__":
    wrapper = i3Wrapper()
    wrapper.start()

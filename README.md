i3status-wrapper
================

Take piped output from i3status and play around with it!

Makes it easy to insert extra fields into the status bar and edit other
ones (to add colour, for example).


Installation
------------

To use i3status-wrapper, first ensure that your i3status config (default
location `~/.i3status.conf` or `~/.config/i3status/config`) contains
this line:

    output_format = "i3bar"

It should be in the 'general' block. Then in your i3 config (default
`~/.i3/config` or `~/.config/i3/config`):

    status_command i3status | i3status-wrapper.py

If you're not using i3, all you need to do is pipe i3status into this
wrapper.

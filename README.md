# Router-rebooter

This is a Python project designed for Raspberry Pi.

Monitors network connectivity with pings to public addresses. If the internet is down,
attempts to reboot the home router by pulsing a GPIO pin, which toggles a relay that
supplies power to the router.

Overall project inspired by [this blog post](http://justinblaber.org/how-to-control-a-power-outlet-with-a-raspberry-pi/);
I figured this could be paired with some simple network monitoring to fix the common
issue where home routers get "stuck" from time to time and need to be reset. If you're
not at home to pull the plug, this can be a real drag.

## Usage

Run `./router_rebooter.py --help` for a list of options and default settings.

## Running it as a daemon

I recommend using [supervisord](http://supervisord.org/introduction.html) to do this, 
which avoids the trouble of writing and installing rc.d scripts or mucking with systemd.
A quick intro of how this works on the RPi is in
[this StackExchange answer](https://raspberrypi.stackexchange.com/a/96676).

A sample supervisord configuration file that can be dropped into `/etc/supervisor/conf.d`\
is included in this repo. I recommend running the script as a unique, low-privilege user.

## Author

[Theodore Pak](https://github.com/powerpak)

## License

MIT. See LICENSE.txt

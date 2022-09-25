# Router-rebooter

This is a Python project designed for [Raspberry Pi][rpi].

It monitors network connectivity with pings to public addresses that should always
be reachable. If the internet is down, it attempts to reboot your home router by 
pulsing a GPIO pin, which is intended to toggle a relay that supplies power to your 
home router (hopefully fixing the connectivity issue).

Overall project inspired by [a blog post by Justin Blaber][jb].
I figured this could be paired with some simple network monitoring to fix a common
issue: most home routers get "stuck" from time to time and need to be reset. If you're
not at home to pull the plug, this can be a real drag, especially if you're counting
on something at home to have continual internet access. This project gives you a fully
automated solution requiring only about $50 worth of hardware.

[jb]: http://justinblaber.org/how-to-control-a-power-outlet-with-a-raspberry-pi/

## Getting started

1. You'll need a [Raspberry Pi][rpi] that runs Linux and a full Python (i.e., Pico won't 
work, but anything Zero or bigger will do.) I use an antiquated One Model B+. Setup any 
Linux on it, such as Raspberry Pi OS.

2. You'll need an [IoT Power Relay][iot] and a couple of wires. If your Pi has male GPIO 
header pins, [male/female jumper wires][jumper] work really nicely. Connect the Pi
to the relay as in [Justin's blog post][jb]. Remember which GPIO pin # you picked.

3. Clone this repo to your Pi. Run `./router_rebooter.py --help` for a list of options 
and default settings.

_If you used GPIO pin 21 and intend to test the internet using WiFi 
interface `wlan0`, all default settings can be used. In this case, you can run
`./router_rebooter.py` to kick off the monitoring cycle. Messages will be printed to `STDERR`._

[rpi]: https://www.raspberrypi.com/products/
[iot]: https://www.adafruit.com/product/2935
[jumper]: https://www.adafruit.com/product/1952

## Running router-rebooter as a daemon

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

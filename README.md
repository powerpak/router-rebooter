# Router-rebooter

This is a Python project designed for Raspberry Pi.

Monitors network connectivity with pings to public addresses. If the internet is down,
attempts to reboot the home router by pulsing a GPIO pin, which toggles a relay that
supplies power to the router.

Overall project inspired by [this blog post](http://justinblaber.org/how-to-control-a-power-outlet-with-a-raspberry-pi/); I figured this could be paired with some simple network monitoring to allay the common issue that home routers get "stuck" from time to time and need to be reset.

## Author

[Theodore Pak](https://github.com/powerpak)

## License

MIT. See LICENSE.txt

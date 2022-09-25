#!/usr/bin/env python3

"""
Monitors network connectivity with pings to public addresses. If the internet is down,
attempts to reboot the home router by pulsing a GPIO pin, which toggles a relay that 
supplies power to the router.
"""
# Overall project inspired by:
# http://justinblaber.org/how-to-control-a-power-outlet-with-a-raspberry-pi/
#
# Author: Theodore Pak

import subprocess
from time import sleep
from pulse_gpio_pin import pin_pulser, MAX_PIN_NUM 
from random import shuffle
from datetime import datetime
import sys
import argparse

PING_INTERFACE = 'wlan0'
INTERFACE_CHECK_CMD = ['cat', '/sys/class/net/{}/operstate']
PING_CMD = ['ping', '-i', '0.2', '-c', '5', '-I']
PING_DESTINATIONS = ['1.1.1.1', '4.2.2.2', '8.8.8.8']
PING_INTERVAL = 15.0
MIN_PING_INTERVAL = 1.0
POST_REBOOT_INTERVAL = 5 * 60.0
REBOOT_LIMIT = 3
POST_REBOOT_LIMIT_INTERVAL = 3 * 60 * 60.0

RELAY_GPIO_PIN = 21
PULSE_FOR_SECONDS = 2.0

#####
# The main class that handles the network monitoring and rebooting
# After creating an instance, call `start_main_loop()` to kick things off 
#####

class RouterRebooter():
    def __init__(self, interface=PING_INTERFACE, ping_interval=PING_INTERVAL, 
                post_reboot_interval=POST_REBOOT_INTERVAL, reboot_limit=REBOOT_LIMIT,
                post_reboot_limit_interval=POST_REBOOT_LIMIT_INTERVAL,
                relay_gpio_pin=RELAY_GPIO_PIN, pulse_for_seconds=PULSE_FOR_SECONDS):
        # configuration options
        self.interface = interface
        self.ping_interval = ping_interval
        self.post_reboot_interval = post_reboot_interval
        self.reboot_limit = reboot_limit
        self.post_reboot_limit_interval = post_reboot_limit_interval
        self.relay_gpio_pin = relay_gpio_pin
        self.pulse_for_seconds = pulse_for_seconds
        
        # internal state while running the main loop
        self.reboot_count = 0
        self.reboots_reached_limit = False

    def verify_interface(self):
        cmd = INTERFACE_CHECK_CMD.copy()
        cmd[1] = cmd[1].format(self.interface)
        proc_result = subprocess.run(cmd, capture_output=True)
        return proc_result.returncode == 0 and proc_result.stdout == b"up\n"

    def ping(self, destination):
        """Pings an IPv4 destination using the PING_CMD above.
        Returns True if succeeded, False if not (based on the exit code of the command)."""
        proc_result = subprocess.run(PING_CMD + [self.interface, destination], capture_output=True)
        return proc_result.returncode == 0

    def is_network_up(self):
        """Determines whether the internet is working by seeing if pings to any of the
        PING_DESTINATIONS succeeds. If any respond, we believe all is OK, and return True.
        Otherwise, return False.
        (Having multiple PING_DESTINATIONS guards against one of them going down or blocking us.)"""
        ping_dests = PING_DESTINATIONS.copy()
        shuffle(ping_dests)
        return any(map(lambda dest: self.ping(dest), ping_dests))

    def start_main_loop(self):
        if not self.verify_interface():
            log(f"Interface {self.interface} doesn't exist or isn't up. Check `ifconfig -a` output.")
            log("Exiting.")
            sys.exit(5)
            
        log(f"Router-rebooter started successfully.")
        log(f"First ping will be sent in {self.ping_interval} seconds.")
        sleep(self.ping_interval)

        while True:
            if self.is_network_up():
                if self.reboot_count > 0 or self.reboots_reached_limit:
                    log("Network is back up.")
                    self.reboots_reached_limit = False
                    self.reboot_count = 0
                sleep(self.ping_interval)
            elif self.reboot_limit > 0 and self.reboot_count >= self.reboot_limit:
                self.reboot_count = 0
                self.reboots_reached_limit = True
                log(f"Reached reboot limit of {self.reboot_limit} attempts.")
                log(f"Sleeping for {self.post_reboot_limit_interval} seconds.")
                sleep(self.post_reboot_limit_interval)
            else:
                log(f"Network appears down. Pulsing GPIO pin {self.relay_gpio_pin}.")
                with pin_pulser(self.relay_gpio_pin) as pulse_pin:
                    pulse_pin(self.pulse_for_seconds)
                self.reboot_count += 1
                log(f"This is reboot attempt {self.reboot_count}.")
                sleep(self.post_reboot_interval)

#####
# utilities for argument parsing and error handling
#####

def eprint(*args, **kwargs):
    """Print to standard error"""
    print(*args, file=sys.stderr, **kwargs)

def log(*args, **kwargs):
    """Same as eprint, except we prefix messages with a timestamp."""
    eprint(datetime.now().strftime("[%Y-%m-%d %H:%M:%S] "), *args, **kwargs)

class ArgumentParser(argparse.ArgumentParser):
    """Subclass ArgumentParser by enhancing the error handler to print a longer usage message."""
    def __init__(self, *args, **kwargs):
        super().__init__(formatter_class=argparse.ArgumentDefaultsHelpFormatter, *args, **kwargs)

    def error(self, message):
        eprint(f"ERROR :: {self.prog}: {message}\n")
        eprint(f"DESCRIPTION\n{__doc__.strip()}\n")
        eprint("ARGUMENTS\n" + self.format_help())
        eprint("OUTPUTS\nEvents are logged to stderr. This program runs endlessly in the foreground.\n"
            "We recommend using something like supervisord if you want to run it as a daemon:\n"
            "https://serversforhackers.com/c/monitoring-processes-with-supervisord\n")
        sys.exit(2)

#####
# code that runs if this script is invoked directly
#####

if __name__ == "__main__":
    parser = ArgumentParser(prog=sys.argv[0])
    parser.add_argument("--interface", "-I", default=PING_INTERFACE,
            help="Which interface pings are sent on to determine if the network is up.")
    parser.add_argument("--ping-interval", "-t", default=PING_INTERVAL, type=float,
            help="How many seconds between each ping")
    parser.add_argument("--post-reboot-interval", "-P", default=POST_REBOOT_INTERVAL, type=float,
            help="How many seconds to wait after rebooting the router before retesting connectivity.")
    parser.add_argument("--reboot-limit", "-L", default=REBOOT_LIMIT, type=int,
            help="How many reboots to attempt before backing off. Set to 0 to retry indefinitely.")
    parser.add_argument("--post-reboot-limit-interval", "-R", default=POST_REBOOT_LIMIT_INTERVAL, type=float,
            help="After hitting the reboot limit, wait this many seconds before retesting connectivity.")
    parser.add_argument("--relay-gpio-pin", "-p", default=RELAY_GPIO_PIN, type=int,
            help="Which GPIO pin the relay is connected to.")
    parser.add_argument("--pulse-for-seconds", "-s", default=PULSE_FOR_SECONDS, type=float,
            help="How long to pulse the GPIO pin to reset the router, in seconds.")

    # Parse arguments.
    args = parser.parse_args()
    # On error, this will print help and exit with an explanation message.

    # Validate some of the arguments.
    if not 0 < args.relay_gpio_pin < MAX_PIN_NUM:
        parser.error(f"--relay-gpio-pin must be an integer between 1 and {MAX_PIN_NUM}.")
    if args.pulse_for_seconds <= 0:
        parser.error("--pulse-for-seconds must be a positive number.")
    if args.ping_interval < MIN_PING_INTERVAL:
        parser.error(f"--ping-interval should be at least {MIN_PING_INTERVAL} (seconds).")
    if args.post_reboot_interval < args.ping_interval:
        parser.error("--post-reboot-interval needs to be longer than --ping-interval.")
    if args.post_reboot_limit_interval < args.post_reboot_interval:
        parser.error("--post-reboot-limit-interval needs to be longer than --post-reboot-interval.")

    # Kick off the main loop.
    rebooter = RouterRebooter(**vars(args))
    rebooter.start_main_loop()

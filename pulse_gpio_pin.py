#!/usr/bin/env python3

"""
Usage: {0} PIN_NUM [PULSE_FOR_SECONDS]

Pulses a GPIO pin off -> ON -> off for a given number of seconds (default is {2} seconds).
Written for the Raspberry Pi; requires the RPi.GPIO library.
Note that since the timing is done within Python and a Linux kernel, it is not exact.

  PIN_NUM - Which GPIO pin # (BCM mode); run `pinout` for a helpful diagram.
            Must be an integer between 1 and {1}.
  PULSE_FOR_SECONDS - How many seconds the pulse should last.
                      Optional; default is {2}. Any positive number is accepted.
"""

import RPi.GPIO as GPIO
from time import sleep
from contextlib import contextmanager
import sys

DEFAULT_PULSE_SECONDS = 2.0
MAX_PIN_NUM = 27

__doc__ = __doc__.format(sys.argv[0], MAX_PIN_NUM, DEFAULT_PULSE_SECONDS).strip()

def print_usage_and_exit(exit_code):
    sys.stderr.write(__doc__ + "\n\n")
    sys.exit(exit_code)

@contextmanager
def pin_pulser(pin_num):
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_num, GPIO.OUT)

        def pulse_pin(for_seconds):
            GPIO.output(pin_num, True)
            sleep(for_seconds)
            GPIO.output(pin_num, False) 

        yield pulse_pin
    finally:
        GPIO.cleanup()

# Runs when this script is invoked directly.
if __name__ == "__main__":
    if len(sys.argv) == 1 or '-h' in sys.argv or '--help' in sys.argv:
        print_usage_and_exit(1)

    try:
        pin_num = int(sys.argv[1])
    except:
        sys.stderr.write("FATAL: PIN_NUM is not an integer\n\n")
        print_usage_and_exit(2)

    if pin_num < 1 or pin_num > MAX_PIN_NUM:
        sys.stderr.write(f"FATAL: PIN_NUM must be an integer between 1 and {MAX_PIN_NUM}\n\n")
        print_usage_and_exit(3)

    if len(sys.argv) > 2:
        try:
            pulse_for_seconds = float(sys.argv[2])
            if pulse_for_seconds <= 0.0: raise ValueError("cannot be negative")
        except:
            sys.stderr.write("FATAL: PULSE_FOR_SECONDS should be a positive number\n\n")
            print_usage_and_exit(4)
    else:
        pulse_for_seconds = DEFAULT_PULSE_SECONDS

    if len(sys.argv) > 3:
        sys.stderr.write(f"WARN: Unused arguments {' '.join(sys.argv[3:])}\n")

    with pin_pulser(pin_num) as pulse_pin:
        pulse_pin(pulse_for_seconds)

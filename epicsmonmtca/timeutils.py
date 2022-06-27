#!/usr/bin/env python
import logging
import time

log = logging.getLogger(__name__)
NTIMERS = 10
_timers = [0] * NTIMERS


def time_ms():
    return int(time.monotonic() * 1000)


def reset_timer(timer=0, ms=0):
    _timers[timer] = time_ms() + ms


def reset_timers(ms=0):
    global _timers
    _timers = [time_ms() + ms] * NTIMERS


def wait_period(timer=0, ms=0):
    diff_ms = _timers[timer] - time_ms()
    if diff_ms >= 0:
        time.sleep(diff_ms / 1000.0)
    else:
        log.debug("Overrun of {} ms".format(-1*diff_ms))

    _timers[timer] += ms

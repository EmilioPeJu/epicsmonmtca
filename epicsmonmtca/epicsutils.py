#!/usr/bin/env python
import logging
import time

log = logging.getLogger(__name__)


def sanitise_pv_name(pv_name):
    ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                    "abcdefghijklmnopqrstuvwxyz" \
                    "0123456789:_.{}"
    return "".join([char for char in pv_name if char in ALLOWED_CHARS])


def get_sensor_pv_suffix(slot_id, sensor_name):
    return sanitise_pv_name("{}{}:{}".format(
        slot_id[0], slot_id[1],
        sensor_name.strip().replace(" ", ":").replace(".", "_")).upper())

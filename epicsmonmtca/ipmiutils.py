#!/usr/bin/env python
from math import floor, log10


_units2_table = [
    "", "C", "F", "K", "V", "A", "W", "J", "Coulombs", "VA",
    "Nits", "lumen", "lux", "Candela", "kPa", "PSI", "N", "CFM", "RPM", "Hz",
    "microsecond", "millisecond", "sec", "min", "hour", "day", "week", "mil",
    "inch", "ft", "cu in", "cu feet", "mm", "cm", "m", "cu cm", "cu m", "l",
    "fluid ounce", "radians", "steradians", "rev", "hz", "gravities", "ounce",
    "pound", "ft-lb", "oz-in", "gauss", "gilberts", "henry", "millihenry",
    "farad", "microfarad", "ohms", "siemens", "mole", "becquerel",
    "PPM (parts/million)", "reserved", "Decibels", "DbA", "DbC", "gray",
    "sievert", "color K", "bit", "Kb", "Mb", "Gb", "B", "KB", "MB", "gigabyte",
    "word", "dword", "qword", "line", "hit", "miss", "retry", "reset",
    "overrun / overflow", "underrun", "collision", "packets", "msgs",
    "characters", "error", "correctable error", "uncorrectable error",
    "fatal error", "grams"
]

_units1_rate_table = ["", "uS", "mS", "s", "min", "hr", "day", ""]
_units1_mod_table = ["", "/", "*", ""]

hs_states2string = {
        0x80: "Con lost",
        0x40: "Deactivating",
        0x20: "Deact Req",
        0x10: "Active",
        0x08: "Activating",
        0x04: "Act Req",
        0x02: "Inactive",
        0x01: "N/A"
}

threshold_offsets_msg = [
    "Lower Non-critical - going low",
    "Lower Non-critical - going high",
    "Lower Critical - going low",
    "Lower Critical - going high",
    "Lower Non-recoverable - going low",
    "Lower Non-recoverable - going high",
    "Upper Non-critical - going low",
    "Upper Non-critical - going high",
    "Upper Critical - going low",
    "Upper Critical - going high",
    "Upper Non-recoverable - going low",
    "Upper Non-recoverable - going high",
    "Unknown",
    "Unknown",
    "Unknown",
    "Unknown",
]


def get_sdr_egu(entry):
    unit1 = entry.units_1
    unit2 = entry.units_2
    rate_part = (unit1 >> 3) & 0x7
    mod_part = (unit1 >> 1) & 0x3
    percentage = '% ' if unit1 & 0x1 else ''
    base_unit = _units2_table[unit2]
    mod_unit = _units1_mod_table[mod_part]
    rate_unit = _units1_rate_table[rate_part]
    return (percentage + base_unit
            + ((mod_unit + rate_unit) if rate_unit else "")).strip()


def get_sdr_prec(entry):
    delta = entry.convert_sensor_raw_to_value(0) - \
        entry.convert_sensor_raw_to_value(1)
    offset = entry.convert_sensor_raw_to_value(0)
    delta_frac = delta % 1
    offset_frac = offset % 1
    prec = 0
    if delta_frac != 0.0:
        prec = int(max(prec, -floor(log10(abs(delta_frac)))))

    if offset_frac != 0.0:
        prec = int(max(prec, -floor(log10(abs(offset_frac)))))

    return prec
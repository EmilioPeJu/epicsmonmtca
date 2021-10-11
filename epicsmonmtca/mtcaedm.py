#!/usr/bin/env python
import logging

from os import chmod, path, stat
from stat import S_IEXEC

from epicsmonmtca.manifest import parse_manifest
from epicsmonmtca.epicsutils import get_sensor_pv_suffix
from epicsmonmtca.edmwidgets import (banner, embed, related_display, screen,
                                     static_text, text_monitor, BH, GRID, TH,
                                     TW, WH, WW)

log = logging.getLogger(__name__)


def create_edm_startup(pv_prefix, rack_name, output_path="start-gui"):
    with open(output_path, 'w') as fhandle:
        fhandle.write('''#!/bin/bash
TOP="$(cd $(dirname "$0"); pwd)"
export EDMDATAFILES="$TOP"
exec edm -x -eolc -m 'device={device}' '{rack_name}.edl'
'''.format(device=pv_prefix, rack_name=rack_name))

    st = stat(output_path)
    chmod(output_path, st.st_mode | S_IEXEC)


def create_edm_from_manifest(
        manifest_path, pv_prefix, rack_name, output_dir="data"):
    slots = parse_manifest(manifest_path)
    create_edm(rack_name, slots, output_dir)
    create_edm_startup(
        pv_prefix, rack_name, path.join(output_dir, 'start-gui'))


def create_edm(rack_name, slots, output_dir):
    # this slot type appears in main screen
    main_slot_type = 'AMC'
    # this slot types appear in separate screens and
    # they are linked in the main screen
    extra_slot_types = ['CU', 'PM', 'MCMC']
    for slot_type in extra_slot_types:
        create_edm_for_slot_type(rack_name, slots, slot_type, output_dir)
    title = rack_name
    macros = ""
    filepath = path.join(output_dir, "{}.edl".format(rack_name))
    w, h = create_edm_for_slot_type(
        rack_name, slots, main_slot_type, output_dir)
    x, y = GRID, h
    parts = []
    parts.append(
        embed(0, 0, w, h, "{}-AMC.edl".format(rack_name), macros))

    h += 24 + GRID * 2
    y += GRID
    for slot_type in extra_slot_types:
        parts.append(related_display(
            x, y, 64, 24, slot_type,
            "{}-{}.edl".format(rack_name, slot_type), macros))
        x += 64 + GRID

    parts.insert(0, screen(w, h, title))

    with open(filepath, 'w') as f:
        f.write("".join(parts))

    return (w, h)


def create_edm_for_slot_type(rack_name, slots, slot_type, output_dir):
    w = GRID * 2  # left and right margin
    initial_h = BH + GRID * 2  # main and botton margin plus banner
    h = initial_h
    x = GRID
    y = BH + GRID
    parts = []
    title = "{} {}s".format(rack_name, slot_type)
    filepath = path.join(output_dir, "{}-{}.edl".format(rack_name, slot_type))
    macros = ""
    for slot_id in sorted(slots):
        if slot_id[0] == slot_type:
            mod_filepath = path.join(
                output_dir, "{}{}.edl".format(slot_id[0], slot_id[1]))
            part_size = create_edm_for_slot(
                slot_id, slots[slot_id], mod_filepath)
            parts.append(
                embed(x, y, part_size[0], part_size[1],
                      path.basename(mod_filepath), macros))
            w += part_size[0]
            h = max(h, part_size[1] + initial_h)
            x += part_size[0]
    parts.insert(0, banner(w, title))
    parts.insert(0, screen(w, h, title))
    with open(filepath, 'w') as f:
        f.write("".join(parts))
    return (w, h)


def create_edm_for_slot(slot_id, mtca_mod, filepath):
    if not mtca_mod:
        return
    x = GRID
    y = GRID
    size = ((TW + GRID) * 2, (TH + GRID) * len(mtca_mod.sensors) + GRID + BH)
    title = "{}{}: {}".format(slot_id[0], slot_id[1], mtca_mod.name)
    log.info("Creating EDM screen for %s", title)

    with open(filepath, 'w') as f:
        f.write(screen(size[0], size[1], title))
        f.write(banner(size[0], title))
        y += BH
        for sensor in mtca_mod.sensors:
            f.write(static_text(x, y, sensor.name))
            f.write(text_monitor(x + TW, y, "$(device):{}".format(
                get_sensor_pv_suffix(slot_id, sensor.name))))
            y += TH + GRID

    return size

#!/usr/bin/env python
import logging

from os import chmod, path, stat
from stat import S_IXUSR, S_IXGRP, S_IXOTH

from epicsmonmtca.manifest import parse_manifest
from epicsmonmtca.epicsutils import get_sensor_pv_suffix
from epicsmonmtca.edmwidgets import (banner, embed, embedded_grid,
                                     related_display, screen, static_text,
                                     text_monitor, BH, GRID, TH, TW, WH, WW)
from epicsmonmtca.mtcautils import valid_mtca_module_types

log = logging.getLogger(__name__)


def create_edm_startup(pv_prefix, crate_name, output_path="start-gui"):
    with open(output_path, 'w') as fhandle:
        fhandle.write('''#!/bin/bash
TOP="$(cd $(dirname "$0"); pwd)"
export EDMDATAFILES="$TOP"
exec edm -x -eolc -m 'device={device}' '{crate_name}.edl'
'''.format(device=pv_prefix, crate_name=crate_name))

    st = stat(output_path)
    chmod(output_path, st.st_mode | S_IXUSR | S_IXGRP | S_IXOTH)


def create_edm_from_manifest(
        manifest_path, pv_prefix, crate_name, output_dir="data"):
    slots = parse_manifest(manifest_path)
    create_edm(crate_name, slots, output_dir)
    create_edm_startup(
        pv_prefix, crate_name, path.join(output_dir, 'start-gui'))


def create_edm(crate_name, slots, output_dir):
    # this slot type appears in main screen
    main_slot_type = 'AMC'
    # this slot types appear in separate screens and
    # they are linked in the main screen
    extra_slot_types = list(valid_mtca_module_types)
    extra_slot_types.remove(main_slot_type)
    for slot_type in extra_slot_types:
        create_edm_for_slot_type(crate_name, slots, slot_type, output_dir)
    title = crate_name
    macros = ""
    w, h = create_edm_for_slot_type(
        crate_name, slots, main_slot_type, output_dir)
    x, y = GRID, h
    parts = []
    parts.append(
        embed(0, 0, w, h, "{}-AMC.edl".format(crate_name), macros))

    h += 24 + GRID * 2
    y += GRID

    for slot_type in extra_slot_types:
        parts.append(related_display(
            x, y, 64, 24, slot_type,
        x += 64 + GRID
            "{}-{}.edl".format(crate_name, slot_type), macros))

    create_edm_for_info(crate_name, slots, output_dir)
    parts.append(related_display(
        x, y, 64, 24, 'INFO',
        '{}-INFO.edl'.format(crate_name, slot_type), macros))

    parts.insert(0, screen(w, h, title))

    filepath = path.join(output_dir, "{}.edl".format(crate_name))
    with open(filepath, 'w') as f:
        f.write("".join(parts))

    return (w, h)


def create_edm_for_slot_type(crate_name, slots, slot_type, output_dir):
    w_h_filenames = []
    for slot_id in sorted(slots):
        if slot_id[0] == slot_type:
            mod_filename = "{}{}.edl".format(slot_id[0], slot_id[1])
            mod_filepath = path.join(output_dir, mod_filename)
            part_size = create_edm_for_slot(
                slot_id, slots[slot_id], mod_filepath)
            w_h_filenames.append((part_size[0], part_size[1], mod_filename))

    title = "{} {}s".format(crate_name, slot_type)
    edm_content, size = embedded_grid(title, w_h_filenames)
    filepath = path.join(output_dir, "{}-{}.edl".format(crate_name, slot_type))
    with open(filepath, 'w') as f:
        f.write(edm_content)
    return size


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


def create_edm_for_info(crate_name, slots, output_dir):
    title = "{} FRU Info".format(crate_name)
    w_h_filenames = []

    for slot_id in sorted(slots):
        mod_filename = "{}-{}{}-INFO.edl".format(crate_name,
                                                 slot_id[0],
                                                 slot_id[1])
        mod_filepath = path.join(output_dir, mod_filename)
        part_size = create_edm_for_one_info(slot_id, mod_filepath)
        w_h_filenames.append((part_size[0], part_size[1], mod_filename))

    edm_content, size = embedded_grid(title, w_h_filenames)
    filepath = path.join(output_dir, "{}-INFO.edl".format(crate_name))
    with open(filepath, 'w') as f:
        f.write(edm_content)
    return size


def create_edm_for_one_info(slot_id, filepath):
    x = GRID
    y = GRID
    name_suffix = [
        ('Manufacturer', 'MANUFACTURER'),
        ('Part Number', 'PARTNUMBER'),
        ('Serial Number', 'SERIALNUMBER'),
        ('Version', 'VERSION')
    ]
    size = ((TW + GRID) * 2, (TH + GRID) * len(name_suffix) + GRID + BH)
    title = "{}{}".format(slot_id[0], slot_id[1])
    log.info("Creating info EDM screen for %s", title)

    with open(filepath, 'w') as f:
        f.write(screen(size[0], size[1], title))
        f.write(banner(size[0], title))
        y += BH
        for name, suffix in name_suffix:
            f.write(static_text(x, y, name))
            f.write(text_monitor(x + TW, y, "$(device):{}{}:{}".format(
                slot_id[0], slot_id[1], suffix)))
            y += TH + GRID

    return size

#!/usr/bin/env python
from collections import namedtuple

from epicsmonmtca.mtcautils import valid_mtca_module_types

ManifestModule = namedtuple('ManifestModule', ['name', 'sensors'])
ManifestSensor = namedtuple('ManifestSensor', ['name'])
SENSOR_START_MARK = '-'


def create_manifest(slots, output_path):
    with open(output_path, 'w') as fhandle:
        for slot_id, mtca_mod in sorted(slots.items()):
            fhandle.write("{},{}: {}\n".format(
                slot_id[0], slot_id[1], mtca_mod.name))
            for sensor in mtca_mod.sensors:
                fhandle.write("{} {}\n".format(SENSOR_START_MARK, sensor.name))


def parse_manifest(filepath):
    slots = {}
    first_line = True
    slot_id = None
    with open(filepath, 'r') as fhandle:
        for line in fhandle:
            sline = line.strip()
            if sline.startswith("#") or not sline:
                continue
            if sline.startswith(SENSOR_START_MARK):
                if not slot_id:
                    raise ValueError(
                        'No module associated to {}'.format(sline))
                slots[slot_id].sensors.append(ManifestSensor(sline[1:]))
            else:
                field, key = sline.split(':')
                mod_type, mod_number = field.split(',')
                slot_id = (mod_type.strip(), int(mod_number))
                if slot_id[0] not in valid_mtca_module_types:
                    raise ValueError('Invalid module type')
                slots[slot_id] = ManifestModule(key, [])

    return slots

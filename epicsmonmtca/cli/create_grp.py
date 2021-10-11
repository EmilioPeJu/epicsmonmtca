#!/usr/bin/env python
import argparse

from os import path

from epicsmonmtca.epicsutils import get_sensor_pv_suffix
from epicsmonmtca.manifest import parse_manifest


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest_path')
    parser.add_argument('pv_prefix')
    parser.add_argument('output_path')
    return parser.parse_args()


def main():
    args = parse_args()
    slots = parse_manifest(args.manifest_path)
    with open(args.output_path, 'w') as fhandle:
        for slot_id, mod in slots.items():
            for sensor in mod.sensors:
                line = "{}:{} 10 Monitor\n".format(
                    args.pv_prefix, get_sensor_pv_suffix(slot_id, sensor.name))
                fhandle.write(line)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import argparse

from epicsmonmtca.monitor import EpicsMonMTCA


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mch_ip")
    parser.add_argument("output_path")
    return parser.parse_args()


def main():
    args = parse_args()
    ipmi_manager = EpicsMonMTCA(args.mch_ip)
    ipmi_manager.process_sdr_repository()
    ipmi_manager.create_manifest(args.output_path)


if __name__ == "__main__":
    main()

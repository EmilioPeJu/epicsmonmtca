#!/usr/bin/env python
import argparse

from os import path

from epicsmonmtca.mtcaedm import create_edm_from_manifest, create_edm_startup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest_path')
    parser.add_argument('pv_prefix')
    parser.add_argument('crate_name')
    parser.add_argument('output_dir')
    return parser.parse_args()


def main():
    args = parse_args()
    create_edm_from_manifest(
        args.manifest_path, args.pv_prefix, args.crate_name, args.output_dir)


if __name__ == "__main__":
    main()

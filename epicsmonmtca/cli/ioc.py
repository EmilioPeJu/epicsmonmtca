#!/usr/bin/env python

import argparse
import logging
import os

from softioc import softioc, builder
from epicsmonmtca import EpicsMonMTCA
from epicsmonmtca.manifest import parse_manifest_sensor_names

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('mch_ip', help='IP address of the MCH')
    parser.add_argument('pv_prefix', help='EPICS PV prefix')
    parser.add_argument('--log-level', default='info', choices=['debug',
                                                                'info',
                                                                'warning',
                                                                'error',
                                                                'critical'])
    parser.add_argument('--ipmi-timeout', type=float, default=5.0,
                        help='Timeout for IPMI commands')
    parser.add_argument('--sensors-polling-rate', type=float, default=1.0,
                        help='Rate at which to poll the sensors in seconds')
    parser.add_argument(
        '--sel-polling-rate', type=float, default=-1.0,
        help='Rate at which to poll the SEL in seconds, -1 to disable')
    parser.add_argument('--manifest-path', default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(level=log_level)
    builder.SetDeviceName(args.pv_prefix)
    builder.stringIn("HOSTNAME", VAL=os.uname()[1])
    allowed_sensors = parse_manifest_sensor_names(args.manifest_path) \
        if args.manifest_path else None
    monitor = EpicsMonMTCA(args.mch_ip, 'rmcp',
                           allowed_sensors=allowed_sensors)
    # this crate seems to have a slower IPMI interface
    monitor.ipmi.interface.set_timeout(args.ipmi_timeout)
    monitor.watch_sensors(int(args.sensors_polling_rate * 1000))
    if args.sel_polling_rate > 0:
        monitor.watch_sel(int(args.sel_polling_rate * 1000))

    # Now get the IOC started
    builder.LoadDatabase()
    softioc.iocInit()
    local = locals()
    local.update(globals())
    # Leave the iocsh running
    softioc.interactive_ioc(local)


if __name__ == "__main__":
    main()

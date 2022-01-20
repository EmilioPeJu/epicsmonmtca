#!/usr/bin/env python
import logging

from pyipmi import sdr

log = logging.getLogger(__name__)
MAX_AMC = 12
MAX_CU = 2
MAX_PM = 4
MAX_MCMC = 2
valid_mtca_modules = ["AMC", "PM", "CU", "MCMC", "CARRIER"]
fruid_base_offsets = {
    'AMC': 5,
    'PM': 50,
    'CU': 40,
    'MCMC': 3,
    'CARRIER': 253
}


def get_slot_fru_id(slot_id):
    fruid_base = fruid_base_offsets.get(slot_id[0])
    if not fruid_base:
        return None
    fruid = fruid_base + slot_id[1] - 1
    log.debug("Requesting fru %d for %s", fruid, slot_id)
    return fruid


def entity_to_slot_id(entity_id, instance_id):
    if entity_id == 0xc2 and instance_id > 0 and instance_id < 10:
        return ("CARRIER", instance_id)
    elif entity_id == 0xc1 \
            and instance_id >= 0x61 and instance_id < (0x61 + MAX_AMC):
        return ("AMC", instance_id - 0x60)
    elif (entity_id == 0x1e or entity_id == 0x1d) \
            and instance_id >= 0x61 and instance_id < (0x61 + MAX_CU):
        return ("CU", instance_id - 0x60)
    elif entity_id == 0x0a \
            and instance_id >= 0x61 and instance_id < (0x61 + MAX_PM):
        return ("PM", instance_id - 0x60)
    elif entity_id == 0xc2 \
            and instance_id >= 0x61 and instance_id < (0x61 + MAX_MCMC):
        return ("MCMC", instance_id - 0x60)
    return None


class MTCAModule(object):
    def __init__(self, slot_id, fru):
        if slot_id[0] not in valid_mtca_modules:
            raise ValueError("Module type not valid")

        self.slot_id = slot_id
        self.fru = fru
        self.sensors = []

    @property
    def manufacturer(self):
        return self.fru.product_info_area.manufacturer.value

    @property
    def part_number(self):
        return self.fru.product_info_area.part_number.value

    @property
    def serial_number(self):
        return self.fru.product_info_area.serial_number.value

    @property
    def version(self):
        return self.fru.product_info_area.version.value

    @property
    def name(self):
        return self.part_number

    @property
    def product_name(self):
        return self.fru.board_info_area.product_name.value

    def __repr__(self):
        return "<{} {}>".format(self.slot_id[0], self.name)

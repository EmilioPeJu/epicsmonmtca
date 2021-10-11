#!/usr/bin/env python
import logging

from pyipmi import sdr

log = logging.getLogger(__name__)
MAX_AMC = 12
MAX_CU = 2
MAX_PM = 4
MAX_MCMC = 2
valid_mtca_modules = ["AMC", "CU", "PM", "MCMC", "UNK"]
fruid_base_offsets = {
    'AMC': 5,
    'CU': 40,
    'PM': 50,
    'MCMC': 3
}


def get_slot_fru_id(slot_id):
    fruid_base = fruid_base_offsets.get(slot_id[0])
    if not fruid_base:
        return None
    fruid = fruid_base + slot_id[1] - 1
    log.debug("Requesting fru %d for %s", fruid, slot_id)
    return fruid


def entity_to_slot_id(entity_id, instance_id):
    if entity_id == 0xc1 \
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
    else:
        return ("UNK", entity_id * 1000 + instance_id)


class MTCAModule(object):
    def __init__(self, slot_id, fru):
        if slot_id[0] not in valid_mtca_modules:
            raise ValueError("Module type not valid")

        self.slot_id = slot_id
        self.fru = fru
        self.sensors = []

    @property
    def name(self):
        return self.fru.product_info_area.part_number.value

    @property
    def manufacturer(self):
        return self.fru.product_info_area.manufacturer.value

    def __repr__(self):
        return "<{} {}>".format(self.slot_id[0], self.name)

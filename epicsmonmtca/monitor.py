import atexit
import logging
import threading
import time

from os import path

from collections import namedtuple
from datetime import datetime

from pyipmi import create_connection, interfaces, sensor, sdr, Target
from softioc import softioc, builder, alarm

from epicsmonmtca.epicsutils import get_sensor_pv_suffix
from epicsmonmtca.ipmiutils import (hs_states2string, get_sdr_egu,
                                    get_sdr_prec, threshold_offsets_msg)
from epicsmonmtca.manifest import create_manifest
from epicsmonmtca.mtcautils import (entity_to_slot_id, get_slot_fru_id,
                                    MTCAModule, valid_mtca_module_types)
from epicsmonmtca.timeutils import reset_timer, wait_period

log = logging.getLogger(__name__)
sel_log = logging.getLogger('sel')

DEFAULT_SENSOR_POLLING_PERIOD = 1000  # ms
POLLING_TIMER = 0
DEFAULT_SEL_POLLING_PERIOD = 1000  # ms
SEL_TIMER = 1

HS_SENSOR_SUFFIX = 'HS'
SensorWatch = namedtuple('SensorWatch', ['sdr', 'record', 'type'])


class InfoType(object):
    FULL = 0
    COMPACT = 1
    HOTSWAP = 2


class EpicsMonMTCA(object):
    def __init__(self, mch_ip, backend='rmcp', user='', password=''):
        self._create_ipmi_session(mch_ip, backend, user, password)
        self._to_monitor = []
        self._sensor_index = {}
        self.slots = {}
        self.initialized = False
        self.ipmi_lock = threading.Lock()
        self.sensor_thread = None
        self.sel_thread = None
        self._quit_sensor_thread = False
        self._quit_sel_thread = False
        self.sensor_polling_period = DEFAULT_SENSOR_POLLING_PERIOD
        self.sel_polling_period = DEFAULT_SEL_POLLING_PERIOD

    def get_slot_module(self, slot_id):
        return self.slots.get(slot_id)

    def create_slot_module(self, slot_id):
        fru_id = get_slot_fru_id(slot_id)
        if not fru_id:
            log.debug('Ignoring module %s%d', slot_id[0], slot_id[1])
            return None

        log.info('Identifying module %s%d', slot_id[0], slot_id[1])
        fru = self.ipmi.get_fru_inventory(fru_id)
        self.slots[slot_id] = MTCAModule(slot_id, fru)
        return self.slots[slot_id]

    def _create_ipmi_session(self, ip, backend, user='', password=''):
        if backend == 'rmcp':
            interface = interfaces.create_interface(
                interface='rmcp', slave_address=0x81, host_target_address=0x20,
                keep_alive_interval=2)
        elif backend == 'ipmitool':
            interface = interfaces.create_interface(
                'ipmitool', interface_type='lan')
        else:
            raise ValueError('Unknown IPMI backend')

        self.ipmi = create_connection(interface)
        self.ipmi.session.set_session_type_rmcp(host=ip, port=623)
        self.ipmi.session.set_auth_type_user(username=user, password=password)
        self.ipmi.target = Target(
            ipmb_address=0x82, routing=[(0x81, 0x20, 0), (0x20, 0x82, None)])
        self.ipmi.session.establish()

    def create_amc_fru_records(self, **kwargs):
        for slot_id in self.slots:
            if slot_id[0] in valid_mtca_module_types:
                builder.stringIn(
                    '{}{}:MANUFACTURER'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].manufacturer,
                    **kwargs)
                builder.stringIn(
                    '{}{}:PARTNUMBER'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].part_number, **kwargs)
                builder.stringIn(
                    '{}{}:SERIALNUMBER'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].serial_number,
                    **kwargs)
                builder.stringIn(
                    '{}{}:VERSION'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].version,
                    **kwargs)
                builder.stringIn(
                    '{}{}:NAME'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].name, **kwargs)
                builder.stringIn(
                    '{}{}:PRODUCTNAME'.format(slot_id[0], slot_id[1]),
                    initial_value=self.slots[slot_id].product_name,
                    **kwargs)

    def _handle_sdr_full_sensor_record(self, entry):
        log.info('Monitoring full sensor for %s', entry.name)
        entity_id = entry.entity_id
        instance_id = entry.entity_instance
        slot_id = entity_to_slot_id(entity_id, instance_id)
        if not slot_id:
            return

        mtca_mod = self.get_slot_module(slot_id)
        if not mtca_mod:
            return  # ignore sensors for cards not inserted

        mtca_mod.sensors.append(entry)
        infotype = InfoType.FULL
        EGU = get_sdr_egu(entry)
        PREC = get_sdr_prec(entry)
        record = builder.aIn(
            get_sensor_pv_suffix(slot_id, entry.name), EGU=EGU, PREC=PREC)
        self._sensor_index[(entry.number, entry.owner_lun)] = entry
        self._to_monitor.append(SensorWatch(entry, record, infotype))

    def _handle_sdr_compact_sensor_record(self, entry):
        log.info(f'Monitoring compact sensor for %s', entry.name)
        entity_id = entry.entity_id
        instance_id = entry.entity_instance
        slot_id = entity_to_slot_id(entity_id, instance_id)
        if not slot_id:
            return

        mtca_mod = self.get_slot_module(slot_id)
        if not mtca_mod:
            return  # ignore sensors for cards not inserted

        mtca_mod.sensors.append(entry)
        infotype = InfoType.COMPACT
        EGU = get_sdr_egu(entry)
        record = builder.aIn(
            get_sensor_pv_suffix(slot_id, entry.name), EGU=EGU)

        self._sensor_index[(entry.number, entry.owner_lun)] = entry
        self._to_monitor.append(SensorWatch(entry, record, infotype))

    def _handle_sdr_hs_sensor(self, entry):
        log.info('Monitoring HS compact sensor for %s', entry.name)
        entity_id = entry.entity_id
        instance_id = entry.entity_instance
        slot_id = entity_to_slot_id(entity_id, instance_id)
        if not slot_id:
            return

        (raw, states) = self.ipmi.get_sensor_reading(entry.number,
                                                     entry.owner_lun)
        if states & 0x1 == 0:  # check if slot is installed (not in M0)
            mtca_mod = self.get_slot_module(slot_id)
            if not mtca_mod:
                mtca_mod = self.create_slot_module(slot_id)
                if not mtca_mod:
                    return
                mtca_mod.sensors.append(entry)

            infotype = InfoType.HOTSWAP
            record = builder.stringIn(
                get_sensor_pv_suffix(slot_id, entry.name))
            self._sensor_index[(entry.number, entry.owner_lun)] = entry
            self._to_monitor.append(SensorWatch(entry, record, infotype))

    def process_sdr_repository(self, **kwargs):
        sdr_entries = list(self.ipmi.sdr_repository_entries())
        for entry in sdr_entries:
            if hasattr(entry, 'device_id_string'):
                entry.name = entry.device_id_string.decode()

        for entry in sdr_entries:
            if entry.type == sdr.SDR_TYPE_COMPACT_SENSOR_RECORD and \
                    entry.name.endswith(HS_SENSOR_SUFFIX):
                # HS sensors should be handled first, as they are used to
                # know which slots are present
                self._handle_sdr_hs_sensor(entry)

        for entry in sdr_entries:
            if entry.type == sdr.SDR_TYPE_FULL_SENSOR_RECORD:
                self._handle_sdr_full_sensor_record(entry)
            elif entry.type == sdr.SDR_TYPE_COMPACT_SENSOR_RECORD and \
                    not entry.name.endswith(HS_SENSOR_SUFFIX):
                self._handle_sdr_compact_sensor_record(entry)

    def watch_sensors(self, polling_period=None):
        if not self._to_monitor:
            self.process_sdr_repository()
            self.create_amc_fru_records()

        if not self.sensor_thread:
            if polling_period:
                self.sensor_polling_period = polling_period
            self.sensor_thread = threading.Thread(
                None, self._sensor_polling_loop)
            self.sensor_thread.start()
        else:
            log.error("Sensor polling loop already started")

    def watch_sel(self, polling_period=None):
        if not self._to_monitor:
            self.process_sdr_repository()
            self.create_amc_fru_records()

        if not self.sel_thread:
            if polling_period:
                self.sel_polling_period = polling_period
            self.sel_thread = threading.Thread(None, self._sel_polling_loop)
            self.sel_thread.start()
        else:
            log.error("SEL polling loop already started")

    @staticmethod
    def _get_sensor_alarm(sdr_entry, status):
        # Considers severity for threshold-based sensors overpassing a
        # threshold
        if sdr_entry.event_reading_type_code == 1 and status & 0x3f != 0:
            return alarm.MINOR_ALARM
        else:
            return alarm.NO_ALARM

    def format_sel_entry(self, sel_entry):
        parts = ['SEL Entry {}'.format(sel_entry.record_id)]
        sdr_entry = None
        dt = datetime.fromtimestamp(sel_entry.timestamp)
        parts.append('Timestamp: {}'.format(dt))

        sensor_id = \
            (sel_entry.sensor_number, (sel_entry.generator_id >> 8) & 3)
        # Adds sensor name if we can find it
        if sensor_id in self._sensor_index:
            sdr_entry = self._sensor_index[sensor_id]
            parts.append('Sensor: {}'.format(
                sdr_entry.device_id_string.decode()))

        parts.append('Sensor number/lun: {}'.format(sensor_id))

        if not sel_entry.event_direction:
            parts.append('Direction: Assertion')
        else:
            parts.append('Direction: Deassertion')

        parts.append('Sensor type: {} Event type: {} Event Data: {}'.format(
            sel_entry.sensor_type, sel_entry.event_type,
            sel_entry.event_data))

        if sel_entry.event_type == 0x6f and sel_entry.sensor_type == 0xf0:
            parts.append('Hotswap Event: Transition to M{}'.format(
                sel_entry.event_data[0] & 15))
        elif sel_entry.event_type == 0x01:
            parts.append('Threshold Event: {}'.format(threshold_offsets_msg[
                sel_entry.event_data[0] & 15]))
            if sdr_entry and len(sel_entry.event_data) >= 3:
                parts.append('Value: {} Threshold: {}'.format(
                    sdr_entry.convert_sensor_raw_to_value(
                        sel_entry.event_data[1]),
                    sdr_entry.convert_sensor_raw_to_value(
                        sel_entry.event_data[2])))

        raw_hex = 'Raw: [{}]'.format(
            ' '.join(['0x%02x' % b for b in sel_entry.data]))
        parts.append(raw_hex)

        return '\n'.join(parts)

    def _poll_sel(self):
        # log sel to standard output when user configured monitor_sel to True
        log.debug('Getting SEL entries')
        with self.ipmi_lock:
            sel_count = self.ipmi.get_sel_entries_count()
            log.debug('SEL number of entries: %d', sel_count)
            if sel_count == 0:
                return
            sel_entry = self.ipmi.get_and_clear_sel_entry(0)
            sel_log.info(self.format_sel_entry(sel_entry))

    def _sel_polling_loop(self):
        reset_timer(SEL_TIMER, self.sel_polling_period)
        while not self._quit_sel_thread:
            self._poll_sel()
            wait_period(SEL_TIMER, self.sel_polling_period)

    def create_manifest(self, output_path):
        create_manifest(self.slots, output_path)

    def _sensor_polling_loop(self):
        log.info('Monitoring %d sensors, period set to %d ms',
                 len(self._to_monitor), self.sensor_polling_period)
        reset_timer(POLLING_TIMER, self.sensor_polling_period)
        while not self._quit_sensor_thread:
            for (sdr_i, record, typ) in self._to_monitor:
                try:
                    with self.ipmi_lock:
                        (raw, status) = self.ipmi.get_sensor_reading(
                            sdr_i.number, sdr_i.owner_lun)
                except Exception as e:
                    log.error('Error requesting %s: %s', sdr_i.name, e)
                if raw is None:  # value is not available
                    log.debug('Value for sensor %s (%d/%d) not available',
                              sdr_i.name, sdr_i.number, sdr_i.owner_lun)
                    continue
                if typ == InfoType.FULL:
                    value = sdr_i.convert_sensor_raw_to_value(raw)
                    severity = self._get_sensor_alarm(sdr_i, status)
                    record.set(value, severity=severity)
                elif typ == InfoType.COMPACT:
                    record.set(raw)
                elif typ == InfoType.HOTSWAP:
                    record.set(hs_states2string.get(status & 0xff, 'Unknown'))

            wait_period(POLLING_TIMER, self.sensor_polling_period)

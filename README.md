# EpicsMonMTCA

EpicsMonMTCA is a python package which allows creating a python soft IOC to
monitor every sensor in a MTCA system.

## How to create a python soft ioc using EpicsMonMTCA

```python
from softioc import softioc, builder, alarm

from epicsmonmtca import EpicsMonMTCA

# Set the PV prefix
builder.SetDeviceName('TS-DI-IPMI-01')

# Pass the MCH's IP
monitor = EpicsMonMTCA("192.168.40.250")

# Start sensor polling loop
monitor.watch_sensors()

# Optionally, monitor SEL, this will get each sel entry, log it and delete it
#monitor.watch_sel()

# Now get the IOC started
builder.LoadDatabase()
softioc.iocInit()

# Leave the iocsh running
softioc.interactive_ioc(globals())
```

That will create a PV for every sensor associated to each card

## Create EDM screens

```bash
# create a manifest file with the list of sensors in each card.
# The passed arguments are: MCH's IP and output path
$ emm-create-manifest  192.168.40.250 sensors.txt

$ mkdir data/

# Creates EDM screens based on manifest path, PV prefix and rack name.
# The last parameter is the output directory
$ emm-create-edm sensors.txt TS-DI-IPMI-01 TS-DI-RACK-01 data

# now, you can start the main screen
$ ./data/start-gui
```

## Create group file

```bash
$ emm-create-grp sensors.txt TS-DI-IPMI-01 pvs.grp
```

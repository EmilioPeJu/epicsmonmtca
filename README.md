# EpicsMonMTCA

EpicsMonMTCA is a python package which allows creating a python soft IOC to
monitor every sensor in a MTCA system.

## How to run the IOC

```bash
# emm-ioc <MCH-IP> <PV-PREFIX>
$ emm-ioc 192.168.1.41 TS-DI-IPMI-06
```

That will create a PV for every sensor associated to each card.

## Create EDM screens

```bash
# create a manifest file with the list of sensors in each card.
# The passed arguments are: MCH's IP and output path
$ emm-create-manifest  192.168.1.41 sensors.txt

$ mkdir data/

# Creates EDM screens based on manifest path, PV prefix and rack name.
# The last parameter is the output directory
$ emm-create-edm sensors.txt TS-DI-IPMI-06 TS-DI-RACK-06 data

# now, you can start the main screen
$ ./data/start-gui
```

## Create group file

```bash
$ emm-create-grp sensors.txt TS-DI-IPMI-01 pvs.grp
```

## How to reduce the sensors considered
Some times the polling loop will be too slow because of having too many
sensors. You can select the sensors considered by creating a manifest, deleting
some sensor names and passing `--manifest-path` to the IOC.
You can create a manifest file in a running IOC with:
```python
monitor.create_manifest('sensors.txt')
```

Then, delete some sensor lines (this lines start with `-`) and run the IOC:
```bash
$ emm-ioc --manifest-path sensors.txt 192.168.1.41 TS-DI-IPMI-06
```

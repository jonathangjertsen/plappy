"""
devices module - Base-level Devices

Classes:
    * Device - a generic Device
    * DeviceCollection(Device) - a Device used to group other Devices
"""
import collections

from plappy.plappyconfig import config
from plappy.io import IO
from plappy.util import unique_key

class Device(object):
    """A generic Device.

        label (str): Used to identify the Device
        ios (dict[str->IO]): IO ports for the Device
        subdevices (dict[str->Device]): Other Devices contained within this one,
            will tick whenever self.tick() is ran
    """

    def __init__(self, label: str):
        """Initialize Device with inp label, an optional dict of IOs and an optional dict of Devices"""
        self.label = label
        self.ios = {}
        self.subdevices = {}

    def __repr__(self) -> str:
        """Representation of the Device"""
        ios = "{" + ", ".join(repr(io) for io in self.ios) + "}"
        subdevices = "{" + ", ".join(repr(sub) for sub in self.subdevices) + "}"
        return f"{type(self).__name__}('{self.label}', ios={ios}, subdevices={subdevices})"

    def __le__(self, devices: 'Device' or tuple) -> 'Device':
        """Allows you to add subdevices: parent <= (child1, child2, ..., childn)"""
        if isinstance(devices, collections.Iterable):
            for device in devices:
                self <= device
        else:
            self.add_subdevice(devices)
        return self

    def __lt__(self, other: 'Device') -> 'Device':
        """< is equivalent to <="""
        return self <= other

    def __or__(self, other: 'Device') -> 'DeviceCollection':
        """Makes (dev1|dev2) a DeviceConnection which can run the two devices in parallel"""
        return DeviceCollection('parallel') <= (self, other)

    def __ror__(self, other: 'Device'):
        """Equivalent to __or__"""
        return self | other

    def add_io(self, io: IO, label: str = None) -> 'Device':
        """Add a new IO port"""
        # Ensure label exists
        if label is None:
            label = io.label

        # Add the IO
        self.ios[unique_key(label, self.ios)] = io

        return self

    def io(self, label: str) -> IO:
        """Return the IO instance referred to by the label"""
        return self.ios[label]

    def add_subdevice(self, subdevice: 'Device', label: str = None) -> 'Device':
        """Add a new subdevice"""
        if label is None:
            label = subdevice.label

        self.subdevices[unique_key(label, self.subdevices)] = subdevice
        return self

    def add_subdevices(self, subdevices: dict) -> 'Device':
        for label in subdevices:
            self.add_subdevice(subdevices[label], label)
        return self

    def subdevice(self, label: str) -> 'Device':
        """Return the Device instance referred to by the label"""
        return self.subdevices[label]

    def connect(self, other: 'IO', label: str) -> 'Device':
        """Connect an own IO to another IO"""
        self.ios[label] -- other
        return self

    def tick(self) -> 'Device':
        # Load from inputs
        for io in self.ios:
            if io.bufstate == config.bufstate.filled:
                io.tick()

        # Do own processing
        self.process()

        # Push from outputs
        for io in self.ios:
            if io.bufstate == config.bufstate.ready_to_push:
                io.tick()

        return self

    def process(self) -> 'Device':
        # Run subdevices
        for subdevice in self.subdevices:
            self.subdevices[subdevice].tick()

        return self

class DeviceCollection(Device):
    """A Device subclass used to group other devices without any further structure"""

    def __or__(self, other: 'Device') -> 'DeviceCollection':
        """If the other type is a DeviceCollection, merge the subdevices. Otherwise, consume the other Device."""
        if isinstance(other, type(self)):
            return self <= other.subdevices
        else:
            return self <= other

    def __ror__(self, other: 'Device') -> 'DeviceCollection':
        """Equivalent to __or__"""
        return self | other

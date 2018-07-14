"""
devices module - Base-level Devices

Classes:
    * Device - a generic Device
    * DeviceCollection(Device) - a Device used to group other Devices
"""
import collections

from plappy.exceptions import ConnectionError
from plappy.plappyconfig import config
from plappy.io import IO, Input, Output
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
        for io in self.ios.values():
            if io.bufstate == config.bufstate.filled:
                io.tick()

        # Do own processing
        self.process()

        # Push from outputs
        for io in self.ios.values():
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


class ContainableDevice(Device):
    def __init__(self, label: str):
        super().__init__(label)
        self.container = None

    def contain(self, other) -> 'ContainableDevice':
        if self.container is None:
            if other.container is None:
                self.container = DeviceCollection(label='container')
            else:
                self.container = other.container
            self.container <= self
        if other.container is None:
            other.container = self.container
            self.container <= other
        return self


class MonoInputDevice(ContainableDevice):
    def __init__(self, label: str):
        super().__init__(label)
        self.input = Input(label=f"{self.label}-input")
        self.ios[self.input.label] = self.input

    def io(self, label: str = None) -> Input:
        """Return the single Output port available"""
        if label is not None and self.input.label != label:
            raise KeyError(
                f"Specified label {label} does not match the {type(self).__name__} input label {self.input.label}"
            )
        return self.input

    def connect(self, other: IO, label: str = None) -> 'MonoInputDevice':
        """Connect the input to another"""
        self.input.connect(other)
        return self

    def __lt__(self, other: 'MonoOutputDevice') -> 'MonoOutputDevice':
        self.input < other.output
        return other

    def __lshift__(self, other: 'MonoOutputDevice') -> 'MonoOutputDevice':
        return self.contain(other) < other

    def __rrshift__(self, other) -> 'MonoInputDevice':
        return other >> self


class MonoOutputDevice(ContainableDevice):
    def __init__(self, label: str):
        super().__init__(label)
        self.output = Output(label=f"{self.label}-output")
        self.ios[self.output.label] = self.output

    def io(self, label: str = None) -> Output:
        """Return the single Output port available"""
        output = self.output
        if label is not None and output.label != label:
            raise KeyError(
                f"Specified label {label} does not match the {type(self).__name__} output label {output.label}"
            )
        return output

    def __gt__(self, other: 'MonoInputDevice') -> 'MonoInputDevice':
        self.output > other.input
        return other

    def __rshift__(self, other: 'MonoInputDevice') -> 'MonoInputDevice':
        return self.contain(other) > other

    def __rlshift__(self, other) -> 'MonoOutputDevice':
        return other << self


class SingleChannelDevice(MonoInputDevice, MonoOutputDevice):
    def io(self, label: str = None) -> Input:
        return self.ios[label]

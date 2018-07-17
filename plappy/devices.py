"""
devices module - Base-level Device

Classes:
    * Device - a generic Device
"""
import collections

from plappy.core import Connectable
from plappy.io import IO
from plappy.plappyconfig import config
from plappy.util import unique_key

DevicePatch = dict

class Device(Connectable):
    """A generic Device.

        label (str): Used to identify the Device
        ios (dict[str->IO]): IO ports for the Device
        subdevices (dict[str->Device]): Other Devices contained within this one,
            will tick whenever self.tick() is ran
    """
    def __init__(self, label: str):
        """Initialize Device with inp label, an optional dict of IOs and an optional dict of Devices"""
        super().__init__(label)
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
            return self
        else:
            self.add_subdevice(devices)
            return devices

    def __or__(self, other: 'Device') -> 'DeviceCollectionMixin':
        """Makes (dev1|dev2) a DeviceConnection which can run the two devices in parallel"""
        from plappy.mixins import DeviceCollectionMixin
        return DeviceCollectionMixin('parallel') <= (self, other)

    def __ror__(self, other: 'Device'):
        """Equivalent to __or__"""
        return self | other

    def patch_helper(self, seen: set):
        seen.add(id(self))

        if not self.subdevices:
            return []

        return [
            {
                'class': type(sub).__name__,
                'label': self.label,
                'ios': tuple(io.patch_helper() for io in sub.ios.values()),
                'subdevices': sub.patch_helper(seen)
            }
            for sub in self.subdevices.values()
            if id(sub) not in seen
        ]

    def make_patch(self, name: str, format: str = 'dict'):
        seen = set()
        patch = DevicePatch(
            version=config.version,
            schema='device-patch',
            name=name,
            tree={
                'class': type(self).__name__,
                'label': self.label,
                'ios': tuple(io.patch_helper() for io in self.ios.values()),
                'subdevices': self.patch_helper(seen)
            }
        )

        if format == 'json':
            import json
            return json.dumps(patch, indent=4)
        else:
            return patch

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

    def connect_io(self, other: 'IO', label: str) -> 'Device':
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

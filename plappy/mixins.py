"""
mixins module - mixin classes for Devices

Classes

    * DeviceCollection(Device) - a Device used to group other Devices
    * ContainerDevice(DeviceCollection) - a concrete version of the DeviceCollectionMixin
    * CollectableDeviceMixin(Device) - a Device that knows about its containing DeviceCollection
    * MonoInputDeviceMixin(CollectableDeviceMixin) - a Device with a single Input, implements the same syntax as Inputs
    * MonoOutputDeviceMixin(CollectableDeviceMixin) - a Device with a single Output, implements the same syntax as Outputs
    * SingleChannelDeviceMixin(MonoInputDeviceMixin, MonoOutputDeviceMixin) - a Device with a single Input and a single Output
    * StereoMixin(Device) - a Device with a left and right version of something

Functions

    * stereo_class(mono_cls, *self_classes) - returns a class (not an instance!) for a stereo version of a Device
"""
from plappy.devices import Device
from plappy.exceptions import ConnectionError
from plappy.io import Input, Output

class DeviceCollectionMixin(Device):
    """A Device subclass used to group other devices without any further structure"""
    def __or__(self, other: 'Device') -> 'DeviceCollectionMixin':
        """If the other type is a DeviceCollectionMixin, merge the subdevices. Otherwise, consume the other Device."""
        if isinstance(other, type(self)):
            return self <= other.subdevices.values()
        else:
            return self <= other

    def __ror__(self, other: 'Device') -> 'DeviceCollectionMixin':
        """Equivalent to __or__"""
        return self | other

class ContainerDevice(DeviceCollectionMixin):
    pass


class CollectableDeviceMixin(Device):
    def __init__(self, label: str):
        super().__init__(label)
        self.superdevice = None

    def collect(self, other) -> 'CollectableDeviceMixin':
        if self.superdevice is None:
            if other.superdevice is None:
                self.superdevice = ContainerDevice(label='container')
            else:
                self.superdevice = other.superdevice
            self.superdevice <= self
        if other.superdevice is None:
            other.superdevice = self.superdevice
            self.superdevice <= other
        return self


class MonoInputDeviceMixin(CollectableDeviceMixin):
    def __init__(self, label: str, bypass=False):
        super().__init__(label)
        self.input = Input(label=f"{self.label}-input")
        self.ios[self.input.label] = self.input
        self.bypass = bypass

    def io(self, label: str = None) -> Input:
        """Return the single Output port available"""
        if label is not None and self.input.label != label:
            raise KeyError(
                f"Specified label {label} does not match the {type(self).__name__} input label {self.input.label}"
            )
        return self.input

    def process(self):
        if self.bypass:
            self.input.clear()
            return self
        return self.process_input(self.input.read())

    def process_input(self, data):
        return self

    def connector(self, **kwargs):
        return self.input

    def __rrshift__(self, other) -> 'MonoInputDeviceMixin':
        return other >> self


class MonoOutputDeviceMixin(CollectableDeviceMixin):
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

    def connector(self, **kwargs):
        return self.output

    def __gt__(self, other):
        self.output > other.input
        return other

    def __rshift__(self, other: 'MonoInputDeviceMixin') -> 'MonoInputDeviceMixin':
        return self.collect(other) > other


class SingleChannelDeviceMixin(MonoInputDeviceMixin, MonoOutputDeviceMixin):
    def io(self, label: str = None) -> Input:
        return self.ios[label]

    def disconnect(self):
        ~self.input
        ~self.output
        return self

    def connector(self, **kwargs):
        if not 'which' in kwargs:
            raise ConnectionError(f"{type(self).__name__}.connector() needs a 'which' argument")
        elif kwargs['which'] == 'in':
            return self.output
        elif kwargs['which'] == 'out':
            return self.input
        else:
            raise ConnectionError(f"{type(self).__name__}.connector() received invalid 'which' argument: {kwargs['which']}")

class StereoMixin(Device):
    def __init__(self, label: str):
        super().__init__(label)
        self.left = None
        self.right = None

def stereo_class(mono_cls: type, *self_classes) -> type:
    class StereoDevice(*self_classes, StereoMixin):
        def __init__(self, label: str, *args, **kwargs):
            super().__init__(label)
            self.left = mono_cls(label, *args, **kwargs)
            self.right = mono_cls(label, *args, **kwargs)
            self <= (self.left, self.right)
    return StereoDevice

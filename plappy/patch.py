"""
patch module - library for reading Device Patches

Functions

    * validate_patch
    * validate_version
    * make_device
    * make_connections
    * parse_patch
"""
import plappy
from plappy.devices import Device, DevicePatch
from plappy.exceptions import InvalidPatchError, IncompatibleVersionError

def validate_patch(patch: DevicePatch, props: tuple) -> None:
    """Raises an InvalidPatchError if the patch properties seem incorrect"""
    for prop, datatype in props:
        if not prop in patch:
            raise InvalidPatchError(f"No '{prop}' in patch")
        if type(prop) is not datatype:
            raise InvalidPatchError(f"'{prop}' has incorrect type")
    for prop in patch:
        if not prop in props:
            raise InvalidPatchError(f"Invalid property '{prop}' in patch")


def validate_version(patch: DevicePatch) -> tuple:
    """Raises an IncompatibleVersionERror if the version is invalid. Returns the version (3-tuple)"""
    patch_version_parts = patch['version'].split('.')
    current_version_parts = plappy.__version__.split('.')
    if len(patch_version_parts) != 3:
        raise IncompatibleVersionError(f"Invalid version '{patch['version']}'")
    if (int(patch_version_parts[0]) > int(current_version_parts[0])):
        raise IncompatibleVersionError(f"Major version '{patch_version_parts[0]}' is later than current version '{current_version_parts[0]}'")
    return patch_version_parts


def make_device(spec: dict, connections_to_make: set = None) -> (Device, set):
    """Makes a Device from a DevicePatch"""
    if connections_to_make is None:
        connections_to_make = set()

    cls = spec['class']
    label = spec['label']
    subdevices = spec['subdevices']
    ios = spec['ios']
    device = cls(label=label)
    for sub_spec in subdevices:
        subdevice, _ = make_device(sub_spec)
        device <= subdevice
    for io_spec in ios:
        io_cls = io_spec['class']
        io_label = io_spec['label']
        io_connections = io_spec['connections']
        io = io_cls(label=io_label)
        for conn_label in io_connections:
            connections_to_make.add(frozenset((io_label, conn_label)))
        device.add_io(io, io_label)
    return device, connections_to_make


def make_connections(device: 'Device', connections: set):
    """Makes connections for a Device after it has been created"""
    pass


def parse_patch(patch: DevicePatch) -> Device:
    """Performs the reading of a DevicePatch and returns a corresponding Device"""
    validate_patch(patch, props=(('version', str), ('schema', str), ('name', str), ('tree', dict)))
    patch_version_parts = validate_version(patch)
    device, connections = make_device(patch)
    make_connections(device, connections)
    return device

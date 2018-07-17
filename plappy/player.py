"""
players - Devices with only inputs

Classes:
    * Player(Device) - a Device with only inputs
    * MonoPlayer(Device) - a Player with a single input. Stereo version: StereoPlayer
    * MonoBuffer(Device) - a Player which buffers its input. Stereo version: StereoBuffer
    * Printer(MonoPlayer) - a Player which prints its input. Stereo version: StereoPlayer
"""
import numpy as np

from plappy.devices import Device
from plappy.mixins import MonoInputDeviceMixin, stereo_class

class Player(Device):
    def __init__(self, label, bypass = False):
        super().__init__(label)
        self.bypass = bypass

class MonoPlayer(Player, MonoInputDeviceMixin):
    pass

StereoPlayer = stereo_class(MonoPlayer, Player)

class MonoBuffer(MonoPlayer):
    def __init__(self, label: str, buffer_size: int, bypass = False):
        super().__init__(label, bypass=bypass)
        self.buffer = np.zeros(buffer_size)
        self.buffer_size = buffer_size
        self.buffer_ptr = 0

    def process_input(self, data) -> 'MonoBuffer':
        data_size = len(data)
        available_data = self.buffer_size - self.buffer_ptr

        if data_size > available_data:
            data = data[:available_data]
            data_size = available_data

        self.buffer[self.buffer_ptr:self.buffer_ptr+data_size] = data

        return self

    def full(self) -> bool:
        return self.buffer_ptr == self.buffer_size - 1

    def read(self) -> np.ndarray:
        buffer = self.buffer
        self.buffer = np.zeros(self.buffer_size)
        self.buffer_ptr = 0
        return buffer

StereoBuffer = stereo_class(MonoBuffer, StereoPlayer)

class MonoPrinter(MonoPlayer):
    """A MonoPlayer which prints its input."""
    def process_input(self, data) -> 'MonoPrinter':
        print(f"{self.label}: {data}")
        return self

StereoPrinter = stereo_class(MonoPrinter, StereoPlayer)

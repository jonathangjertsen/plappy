"""
players - Devices with only inputs

Classes:
    * Player(Device) - a Device with only inputs
    * MonoPlayer(Device) - a Player with a single input
    * Printer(MonoPlayer) - a MonoPlayer which prints its input
"""

from plappy.devices import Device, MonoInputDevice


class Player(Device):
    pass


class Printer(Player, MonoInputDevice):
    """A MonoPlayer which prints its input."""
    def process(self) -> 'Printer':
        print(f"{self.label}: {self.input.read()}")
        return self

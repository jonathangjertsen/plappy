"""
players - Devices with only inputs

Classes:
    * Player(Device) - a Device with only inputs
    * MonoPlayer(Device) - a Player with a single input
    * Printer(MonoPlayer) - a MonoPlayer which prints its input
"""

from plappy.devices import Device
from plappy.io import IO, Input

class Player(Device):
    pass

class MonoPlayer(Player):
    """A Device specialized to "play" its input, for some definition of play."""
    def __init__(self, label: str):
        """Initialize with an Input"""
        super().__init__(label)
        self.input = Input(label=f"{self.label}-output")
        self.ios = { self.input, }

    def io(self, label: str = None) -> Input:
        """Return the single Output port available"""
        if label is not None and self.input.label != label:
            raise KeyError(
                f"Specified label {label} does not match the {type(self).__name__} input label {self.input.label}"
            )
        return self.input

    def connect(self, other: IO, label: str = None) -> 'MonoPlayer':
        """Connect the input to another"""
        self.input.connect(other)
        return self

class Printer(MonoPlayer):
    """A MonoPlayer which prints its input."""

    def process(self) -> 'Printer':
        print(f"{self.label}: {self.input.read()}")
        return self

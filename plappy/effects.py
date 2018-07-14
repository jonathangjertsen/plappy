"""
effects module - Devices which have inputs and output transformed variations of the data

Classes:
    * Effect(Device) - a Device specialized as an effect
    * MultiChannelEffect(Effect) - an Effect with multiple inputs and outputs
    * SingleChannelEffect(Effect) - an Effect with a single input and a single output
    * LinearGain(SingleChannelEffect) - multiplies input by a gain factor (linear)
    * Gain(SingleChannelEffect) - multiplies input by a gain factor (dB scale)
    * Inverter(LinearGain) - a LinearGain where the gain factor is -1
"""
import numpy as np

from plappy.plappyconfig import config
from plappy.devices import Device
from plappy.io import Input, Output
from plappy.samplebuffer import SampleBuffer


class Effect(Device):
    """A Device specialized as an effect (has inputs, outputs a transformed variation of the inputs)"""
    pass


class MultiChannelEffect(Effect):
    """An Effect with any number of Inputs and Outputs"""

    def __init__(self, label: str, num_inputs: int=0, num_outputs: int=0):
        """Initialize with a number of Inputs and a number of Outputs"""
        super().__init__(label)
        self.inputs = []
        for channel_number in range(num_inputs):
            self.inputs.append(Input(label=f"{self.label}-input-{channel_number}"))

        self.outputs = []
        for channel_number in range(num_outputs):
            self.outputs.append(Output(label=f"{self.label}-output-{channel_number}"))

        self.ios = { *self.inputs, *self.outputs }


class SingleChannelEffect(Effect):
    """An Effect with a single Input and a single Output"""

    def __init__(self, label: str):
        """Initialize with an Input and an Output"""
        super().__init__(label)
        self.input = Input(label=f"{self.label}-input")
        self.output = Output(label=f"{self.label}-output")
        self.ios = { self.input, self.output, }

    def to_multi(self) -> MultiChannelEffect:
        """Convert to an equivalent MultiChannelEffect"""
        effect = MultiChannelEffect(self.label, 0, 0)
        effect.inputs.append(self.input)
        effect.outputs.append(self.output)
        return effect

    def process(self) -> 'SingleChannelEffect':
        """Read input, transform it and load the result into the output"""
        data = self.input.read()
        if data is not None:
            self.output.load(
                buffer=SampleBuffer.from_array(
                    array=self.transform(data)
                )
            )
        return self

    def transform(self, data: np.ndarray):
        """Default transformation: do nothing"""
        return data

class LinearGain(SingleChannelEffect):
    """Multiplies the input by a gain factor (linear scale)"""
    def __init__(self, label: str):
        super().__init__(label)

        self.gain = 1

    def transform(self, data: np.ndarray) -> np.ndarray:
        """Multiply data by a constant gain factor (linear scale)"""
        return (data * self.gain).astype(config.buffer_dtype)


class Inverter(LinearGain):
    """A LinearGain with gain = -1"""
    def __init__(self, label: str):
        super().__init__(label)
        self.gain = -1


class Gain(SingleChannelEffect):
    """Multiplies the input by a gain factor (dB scale)"""
    def __init__(self, label: str, db: float=0.0):
        super().__init__(label)

        self.db = db

    def transform(self, data: np.ndarray) -> np.ndarray:
        """Multiply data by a constant gain factor (dB scale)"""
        return (data * 10 ** (self.db / 20)).astype(config.buffer_dtype)

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
from plappy.devices import Device, SingleChannelDevice
from plappy.io import Input, Output
from plappy.samplebuffer import SampleBuffer
from plappy.util import linear, linear_gain


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
            inp = Input(label=f"{self.label}-input-{channel_number}")
            self.inputs.append(inp)
            self.ios[inp.label] = inp

        self.outputs = []
        for channel_number in range(num_outputs):
            outp = Output(label=f"{self.label}-output-{channel_number}")
            self.outputs.append(outp)
            self.ios[outp.label] = outp


class SingleChannelEffect(Effect, SingleChannelDevice):
    """An Effect with a single Input and a single Output"""
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
        return (data * linear_gain(self.db)).astype(config.buffer_dtype)


class ClipDistortion(SingleChannelEffect):
    """Clips the input"""
    def __init__(self, label: str, dbfs: float=0.0):
        super().__init__(label)
        self.dbfs = dbfs

    def transform(self, data: np.ndarray) -> np.ndarray:
        absmax = abs(linear(self.dbfs))
        return np.clip(data, -absmax, absmax)

"""
sources module - Devices specialized to produce output

Classes:
    * Source(Device) - A Device specialized to only produce output
    * MonoSource(Source) - a Source with a single output
    * SilenceSource(MonoSource) - A MonoSource which produces silence
    * DCSource(MonoSource) - A MonoSource which produces a DC value
    * WhiteNoiseSource(MonoSource) - A MonoSource which produces white noise
"""

import numpy as np

from plappy.devices import Device
from plappy.io import IO
from plappy.mixins import MonoOutputDeviceMixin, stereo_class
from plappy.plappyconfig import config
from plappy.samplebuffer import SampleBuffer


class Source(Device):
    pass


class MonoSource(Source, MonoOutputDeviceMixin):
    def connect(self, other: IO, **kwargs) -> 'MonoSource':
        self.output.connect(other, **kwargs)
        return self

    def process(self) -> 'MonoSource':
        self.output.load(self.generate())
        return self

    def generate(self):
        return None
StereoSource = stereo_class(MonoSource, Source)


class SilenceSource(MonoSource):
    """A MonoSource which produces only silence"""
    def generate(self) -> SampleBuffer:
        """Return a zeroed buffer"""
        return SampleBuffer.from_array(
            np.zeros(
                shape=config.buffer_size
            )
        )
StereoSilenceSource = stereo_class(SilenceSource, StereoSource)


class DCSource(MonoSource):
    """A MonoSource which produces a constant max"""
    def __init__(self, label: str, level: int):
        super().__init__(label)
        self.level = level

    def generate(self):
        """Return a DC buffer"""
        return SampleBuffer.from_array(
            np.full(
                shape=config.buffer_size,
                fill_value=self.level
            )
        )
StereoDCSource = stereo_class(DCSource, StereoSource)


class NoiseSource(DCSource):
    """A MonoSource which produces noise"""
    def generate(self):
        """Return a buffer with noise"""
        return SampleBuffer.from_array(
            np.random.randint(
                low=-self.level,
                high=self.level,
                size=config.buffer_size
            )
        )
StereoNoiseSource = stereo_class(NoiseSource, StereoSource)

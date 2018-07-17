from timeit import timeit

from plappy.plappyconfig import config
from plappy.source import NoiseSource
from plappy.player import MonoPrinter
from plappy.effects import Gain, Inverter, ClipDistortion
from plappy.util import linear_max

printers_on = True

# Create devices
source = NoiseSource('source', level=linear_max)
pre_printer = MonoPrinter('pre-printer', bypass=not printers_on)
gain = Gain('gain', db=-6.02)
clip = ClipDistortion('clip', dbfs=-12.0)
inverter = Inverter('inverter')
post_printer = MonoPrinter('post-printer', bypass=not printers_on)

# Connect them up. All devices are single-channel, so we hook them up with these arrows
source >> pre_printer
source >> gain >> clip >> inverter >> post_printer

# Get access to the source's superdevice
superdevice = source.superdevice

# Run one tick (for real applications, a Sequencer should take care of tick management)
timing = timeit('superdevice.tick()', number=int(2 * config.sample_rate / config.buffer_size), globals=globals())
print(f"Sample rate: {config.sample_rate}/s per channel")
print(f"Buffer size: {config.buffer_size} samples per buffer")
print(f"Buffer rate: {int(2 * config.sample_rate / config.buffer_size)} buffers/s per channel")
print(f"Minimum latency: {1000 * config.buffer_size / config.sample_rate:.0f} ms")
print(f"Time taken to process 1 second: {timing:.2f}")

# Make a patch
patch = source.superdevice.make_patch('patch-demo', 'json')
print(patch)

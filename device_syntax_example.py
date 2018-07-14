from plappy.sources import NoiseSource
from plappy.players import Printer
from plappy.effects import Gain, Inverter, ClipDistortion
from plappy.util import linear_max

# Create devices
source = NoiseSource('source', level=linear_max)
pre_printer = Printer('pre-printer')
gain = Gain('gain', db=-6.02)
clip = ClipDistortion('clip', dbfs=-12.0)
inverter = Inverter('inverter')
post_printer = Printer('post-printer')

# Connect them up. All devices are single-channel, so we hook them up with these arrows
source >> pre_printer
source >> gain >> clip >> inverter >> post_printer

# Run one tick (for real applications, a Sequencer should take care of tick management)
source.container.tick()

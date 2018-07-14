from plappy.sources import NoiseSource
from plappy.players import Printer
from plappy.effects import Gain, Inverter

# Create devices
source = NoiseSource('source', level=8192)
pre_printer = Printer('pre-printer')
gain = Gain('gain', db=-6.02)
inverter = Inverter('inverter')
post_printer = Printer('post-printer')

# Connect them up
source.output > gain.input - - pre_printer.input
gain.output > inverter.input
inverter.output > post_printer.input

# Put them together in a box
main = (source | pre_printer | gain | inverter | post_printer)
main.label = 'Main'

# Run one tick (for real applications, a Sequencer should take care of tick management)
main.tick()

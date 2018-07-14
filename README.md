# Plappy - Playground for Audio Processing in Python

Modular audio processing framework for Python. Plappy lets you create `Device`s with `Input`s and 
 `Output`s, and connect them up with an intuitive syntax.
 
## Quickstart
### Inputs and outputs

`Input`s and `Output`s are low-level constructs and require some manual work to push data around.
 There are examples of how to do so in `io_data_pushing.py`,
 but you don't need to think about it unless you are creating custom `Device`s because the `Device` take care of it.
 You do need to know how to connect them (see  `io_connection_syntax.py`).


Here is an example of using `Device`s: we connect a noise source into a gain effect
with a gain of -6.02 dB (~half amplitude) which is then fed into an inverter. We also add a `Printer` before and after the effects
 (a Printer prints its contents to the console when it is received).
 
 ~~~
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
~~~

When we call `tick()`, the source generates some noise which flows through the other devices.
As a result, the post-printer prints data which is halved in volume, then clipped at a quarter of max volume, then inverted:

~~~
pre-printer: [ 15439  -8894   9090   4853 -27590  -6176  22509 -30694  -3873   1192
   8998 -12757 -17934   1746   -632 -19368  21752   1100 -19492   1365
  27210   5705 -21397   9273  -4092  -4057 -24579    723 -11181 -30463
   -113  19587  17538 -23795  -5415  -3900 -15115  25799   9066 -25771
  19642   7049  14637  12243 -22226 -30646  -1138  -8064  26361 -16145
  28395  15851  -1680 -32532   9397   9209  29420  -1020  14751   3208
  26694   4740 -17183   6346]
post-printer: [-7720  4447 -4545 -2426  8230  3088 -8230  8230  1936  -596 -4499  6378
  8230  -873   316  8230 -8230  -550  8230  -682 -8230 -2852  8230 -4636
  2046  2028  8230  -361  5590  8230    56 -8230 -8230  8230  2707  1950
  7558 -8230 -4533  8230 -8230 -3524 -7319 -6121  8230  8230   569  4032
 -8230  8073 -8230 -7926   840  8230 -4698 -4604 -8230   510 -7376 -1604
 -8230 -2370  8230 -3173]
~~~

## Contributing

* Follow PEP8 unless otherwise noted
* Ignore the 80 character rule
* Because of the operator abuse, disable 'statement has no effect' warnings

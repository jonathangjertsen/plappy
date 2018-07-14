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
from plappy.effects import Gain, Inverter

# Create devices
source = NoiseSource('source', level=8192)
pre_printer = Printer('printer-pre')
gain = Gain('gain', db=-6.02)
inverter = Inverter('inverter')
post_printer = Printer('printer-post')

# Connect them up
source.output > gain.input - - pre_printer.input
gain.output > inverter.input
inverter.output > post_printer.input

# Put them together in a box
main = (source | pre_printer | gain | inverter | post_printer)
main.label = 'Main'

# Run one tick (for real applications, a Sequencer should take care of tick management)
main.tick()
~~~

Example result (half volume and inverted)

~~~
pre-printer: [-3913  3599  6204 -7265 -1542  3431  2654  2164  7741  3128  6378  4428
 -1424 -1211 -6915  3560  2804 -6386 -1566  4037 -5636  -478  5359 -6635
 -3637 -6039  2733   694 -4006  2892 -4361 -2693 -2169 -4520  -816 -5806
  3011 -3916  7957 -7121  2841 -6920 -4371   374   939 -3681  5156 -3581
 -6351 -6123 -1117   307 -5293  1146  7149 -2898   974 -3541  2040  -657
 -2523   309 -5558 -3424]
post-printer: [ 1956 -1799 -3102  3632   771 -1715 -1327 -1082 -3870 -1564 -3189 -2214
   712   605  3457 -1780 -1402  3193   783 -2018  2818   239 -2679  3317
  1818  3019 -1366  -347  2003 -1446  2180  1346  1084  2260   408  2903
 -1505  1958 -3978  3560 -1420  3460  2185  -187  -469  1840 -2578  1790
  3175  3061   558  -153  2646  -573 -3574  1449  -487  1770 -1020   328
  1261  -154  2779  1712]
~~~

## Contributing

* Follow PEP8 unless otherwise noted
* Ignore the 80 character rule
* Because of the operator abuse, disable 'statement has no effect' warnings

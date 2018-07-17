import numpy as np

from plappy.plappyconfig import config
from plappy.io import Input, Output
from plappy.source import NoiseSource

# Create Input and Output ports
i = Input('input-1')
i2 = Input('input-2')
o = Output('output-1')

# Connect Inputs to Output
o > (i -- i2)

# The buffers are empty
assert(i.bufstate == config.bufstate.empty)
assert(i2.bufstate == config.bufstate.empty)
assert(o.bufstate == config.bufstate.empty)

# Generate some noise and put it in the buffer
noise_buffer = NoiseSource('temp', level=100).generate()
o.load(noise_buffer)

# Now the input buffer is empty and the output buffer is filled/ready to send
assert(i.bufstate == config.bufstate.empty and i2.bufstate == config.bufstate.empty)
assert(o.bufstate == config.bufstate.ready_to_push)
assert(i.buffer != noise_buffer and i2.buffer != noise_buffer)
assert(o.buffer == noise_buffer)

# Push data from the output to everything that's connected
o.flush()

# Now the input buffer is filled and the output buffer is empty
assert(o.bufstate == config.bufstate.empty)
assert(o.buffer.empty())

assert(i.bufstate == config.bufstate.filled and i2.bufstate == config.bufstate.filled)
assert(i.buffer == noise_buffer and i2.buffer == noise_buffer)
assert(i.buffer.array is i2.buffer.array)

# To disentangle i and i2, one must run prepare_to_modify
i.buffer.prepare_to_modify()

assert(i.buffer == noise_buffer and i2.buffer == noise_buffer)
assert(i.buffer.array is not i2.buffer.array)

# Or just read it
received_array = i.read()
assert(i.buffer.empty())
assert(np.array_equal(received_array, noise_buffer.array))


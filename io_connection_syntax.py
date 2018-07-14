from plappy.exceptions import ConnectionError
from plappy.io import Input, Output

### Creating inputs and outputs

i1 = Input('input-1')
i2 = Input('input-2')
o1 = Output('output-1')
o2 = Output('output-2')

# Here we will connect Input 1 to Output 1 and Input 2 to Output 2.

### Connections with dash or asterix syntax

# Negative sign just returns itself, so we can use as many dashes as we want.
assert(-i1 is i1 and -- i1 is i1)

# The statements below are therefore equivalent
# They are also idempotent: only the first statement has any effect
print("Connecting Input 1 and Output 1")
i1 - o1
i1 -- o1
i1 --- o1
i1 * o1
if i1.connected(o1) and o1.connected(i1):
    print("\t> Connected!")

# Outputs cannot be connected to each other:
try:
    print("Connecting Output 1 and Output 2")
    o1 -- o2
except ConnectionError as ce:
    print(f"\t> {ce}") # Cannot connect two Outputs ('output-1' and 'output-2'), use a SimpleMixer or Mixer

### Connections with arrow syntax

print("Connecting from Output 2 to Input 2 with arrow syntax")
i2 <- o2 # OK, points from Output to Input
o2 > i2 # Also OK
# o2 --> i2 # syntax error in Python :(
if i2.connected(o2) and o2.connected(i2):
    print("\t> Connected!")

try:
    print("Connecting from Input 2 to Output 2 with arrow syntax")
    o2 <- i1
    i1 > o2
except ConnectionError as ce:
    print(f"\t> {ce}") # Arrow (<) must point to an Input, not Output 'output-2'

### Connections are transitive

# We are not allowed to connect Input 1 to Input 2 now, because this would connect Output 1 to Output 2
try:
    print("Connecting Input 1 and Input 2")
    i1 -- i2
except ConnectionError as ce:
    print(f"\t> {ce}") # Cannot connect two Outputs ('output-2' and 'output-1'), use a SimpleMixer or Mixer

# Disconnect Input 2
print("Disconnecting Input 2")
~i2
if i2.disconnected():
    print("\t> Disconnected!")

# Now Input 2 can be connected to Input 1
print("Connecting Input 1 and Input 2")
i1 -- i2
if i1.connected(i2):
    print("\t> Connected!")

# In doing so, we have implicitly connected Input 2 to Output 1 as well
if i2.connected(o1):
    print("\t> Input 2 is also connected to Output 1")

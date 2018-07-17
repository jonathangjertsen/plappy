# Syntax
## IO
### Making connections
Unary `-` returns the same IO.
Binary `-` and `*` connect two IOs and returns the right IO.
The following are equivalent:

* `IO1 * IO2`
* `IO1 - IO2`
* `IO1 -- IO2`, `IO1 --- IO2` etc.
* `IO1.connect(IO2)` or `IO2.connect(IO1)`

### Making connections with specified direction

`>` connects two IOs, but requires that the right IO is an Input.
`<` connects two IOs, but requires that the left IO is an Input.
In either case, the right IO is returned.
The following are equivalent:

* `Output > Input`
* `Input < Output`
* `Input <- Output`, `Input <-- Output` etc.

### Combinations

Since the right IO is returned, many IOs can be connected in one statement:

* `Output > Input1 - Input2`

### Disconnecting

`~` disconnects an IO from whatever it is connected to.
The following are equivalent:

* `~IO`
* `IO.disconnect()`

## Device

### Adding subdevices

`<=` adds the right Device as a subdevice to the left Device and returns the right Device.
`>=` adds the left Device as a subdevice to the right Device and returns the right Device.
The following statements have the same effect, but different return values:

* `Device <= Subdevice` returns `Subdevice`
* `Subdevice >= Device` returns `Device`

The following statements have the same effect, but different return values:

* `Device <= Subdevice <= Subsubdevice`
* `Subsubdevice >= Subdevice >= Device`

#### Adding in parallel

If the right operand to `<=` or the left operand to `>=` is an iterable,
all Devices in the iterable are added as subdevices to the other operand.
The following statements have the same effect:

* `Device <= (Subdevice1, Subdevice2, ..., SubdeviceN)`
* `(Subdevice1, Subdevice2, ..., SubdeviceN) >= Device`

### DeviceCollections

* `DeviceCollectionMixin = (Device1 | Device2 | ... | DeviceN)`
* `DeviceCollectionMixin <= Device`: adds `Device` as subdevice to `DeviceCollectionMixin`
* `DeviceCollection1 <= DeviceCollection2`: adds subdevices of `DeviceCollection2` to `DeviceCollection1`
* `DeviceCollection1 >= DeviceCollection2`: adds subdevices of `DeviceCollection1` to `DeviceCollection2`

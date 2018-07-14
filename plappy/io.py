"""
io module - Low-level Input/Output objects which can be connected

Classes:
    * IO(object) - Generic Input/Output object
    * Input(IO) - IO object which can only receive data
    * Output(IO) - IO object which can only send data
"""
import numpy as np

from plappy.exceptions import ConnectionError, SelfConnectionError
from plappy.plappyconfig import config
from plappy.samplebuffer import SampleBuffer


class IO(object):
    """A generic Input/Output object.

        label (str): Used to identify the IO object
        connections (set): A set of other IO's that it is connected to
        buffer (SampleBuffer): Stores data
        bufstate (int): A flag to indicate the state of the IO
    """

    def __init__(self, label: str):
        """Initialize IO with a label, connections, and an empty buffer."""
        self.label = label
        self.connections = set()
        self.buffer = SampleBuffer()
        self.bufstate = config.bufstate.empty

    def __repr__(self) -> str:
        """Print a useful representation of the IO object"""
        parts = (
            f"{type(self).__name__}('{self.label}', connections = {{",
            ', '.join(f"'{conn.label}'" for conn in self.connections),
            "}, buffer=",
            repr(self.buffer),
            ")"
        )
        return "".join(parts)

    def __str__(self) -> str:
        """Same as __repr__"""
        return repr(self)

    def __neg__(self) -> 'IO':
        """This makes -io the same as io, --io and -- io for a flexible syntax."""
        return self

    def __sub__(self, other: 'IO') -> 'IO':
        """This lets you connect two IOs with io1 - io2 or io1 -- io2"""
        return self.connect(other)

    def __mul__(self, other) -> 'IO':
        """This lets you connect two IOs with io1 * io2"""
        return self - other

    def __invert__(self) -> 'IO':
        """This lets you disconnect an IO with ~io"""
        return self.disconnect()

    def connected(self, io: 'IO') -> bool:
        """Return whether self is connected to io"""
        return io in self.connections

    def disconnected(self) -> bool:
        """Return whether self is completely disconnected"""
        return len(self.connections) == 0

    def connect(self, io: 'IO') -> 'IO':
        """Connect to another IO"""
        # If they are already connected, don't do anything
        if self.connected(io) or io is self:
            return self

        # Check that the two can be connected
        self.connect_check(io)
        io.connect_check(self)

        # Check that all of the connections can be connected to each other
        connection_union = io.connections | self.connections
        for connection in connection_union:
            # Check each connection with every other connection
            for connection_2 in connection_union:
                if connection is not connection_2:
                    connection.connect_check(connection_2)
                    connection_2.connect_check(connection)

            # Check each connection with self and io
            self.connect_check(connection)
            io.connect_check(connection)
            connection.connect_check(self)
            connection.connect_check(io)

        # OK. Copy the connection union, then add io to self and self to io.
        self.connections, io.connections = set(connection_union), set(connection_union)
        self.connections.add(io)
        io.connections.add(self)

        # And add io and self to every other connection
        for connection in connection_union:
            connection.connections.update((self, io))

        # Return self to allow for further connection in the same statement
        return self

    def connect_check(self, io: 'IO') -> None:
        """Raise a ConnectionError if the connection won't work"""
        if io is self:
            raise SelfConnectionError(f"Attempting to connect {type(self).__name__} '{self.label}' to itself")

    def disconnect(self) -> 'IO':
        """Disconnect from whatever it is connected to"""
        if self.disconnected():
            return self

        # Disconnect self from everything else
        for connection in self.connections:
            connection.connections.remove(self)

        # Disconnect everything else from self
        self.connections = set()

        # Return self to allow for further connection in the same statement
        return self

    def load(self, buffer: SampleBuffer or None) -> 'IO':
        """Load the SampleBuffer into the IO"""
        self.buffer.destroy()
        self.buffer = SampleBuffer(other=buffer)
        self.bufstate = config.bufstate.filled
        return self

    def clear(self) -> 'IO':
        """Clear the IO's buffer"""
        self.buffer.destroy()
        self.bufstate = config.bufstate.empty
        return self

    def push(self) -> 'IO':
        """Send content from the IO's buffer to its connections"""
        for connection in self.connections:
            connection.load(self.buffer)
        return self

    def flush(self) -> 'IO':
        """Send content from the IO's buffer to its connections and clear it"""
        return self.push().clear()

    def read(self) -> np.ndarray:
        """Read content from the IO's buffer and clear it"""
        self.buffer.prepare_to_modify()
        contents = self.buffer.array
        self.clear()
        return contents

    def __lt__(self, other: 'IO') -> 'IO':
        """Create a useful warning when trying to connect stuff."""
        raise ConnectionError(f"Arrow (<) must point to an Input, not {type(self).__name__} '{self.label}'")

    def __gt__(self, other: 'IO') -> 'IO':
        """Create a useful warning when trying to connect stuff."""
        raise ConnectionError(f"Arrow (<) must point from an Output, not {type(self).__name__} '{self.label}'")

    def tick(self) -> 'IO':
        """Called by devices, action is implementation dependent"""
        return self


class Input(IO):
    """An Input object is an IO object with additional restrictions and has
    different bufstates after load() and tick()."""

    def __lt__(self, other: IO) -> 'Input':
        """Allows for connections with arrow syntax."""
        return self - other

    def load(self, buffer: SampleBuffer) -> IO:
        """Load buffer, then set bufstate to filled"""
        super().load(buffer)
        self.bufstate = config.bufstate.filled
        return self

    def tick(self) -> IO:
        """Called by devices, sets the bufstate to empty"""
        self.bufstate = config.bufstate.empty
        return self


class Output(IO):
    """An Input object is an IO object with additional restrictions and has
    different bufstates after load() and tick(). When tick() is called, it
    flushes the contents of the buffer."""

    def __gt__(self, other: Input) -> 'Output':
        """Allows for connections with arrow syntax."""
        return self - other

    def load(self, buffer: SampleBuffer or None) -> 'Output':
        """Load buffer, then set bufstate to ready_to_push"""
        super().load(buffer)
        self.bufstate = config.bufstate.ready_to_push
        return self

    def tick(self) -> 'Output':
        """Called by devices, pushes content to connections and clears itself."""
        return self.flush()

    def connect_check(self, io: 'IO') -> None:
        """Prevent an Output from being connected to another Output"""
        super().connect_check(io)

        if isinstance(io, type(self)):
            raise ConnectionError(f"Cannot connect two Outputs ('{self.label}' and '{io.label}'), use a SimpleMixer or Mixer")

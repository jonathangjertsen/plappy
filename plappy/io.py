"""
io module - Low-level Input/Output objects which can be connected

Classes:
    * IO(object) - Generic Input/Output object
    * Input(IO) - IO object which can only receive data
    * Output(IO) - IO object which can only send data
"""
import numpy as np

from plappy.core import Connectable
from plappy.exceptions import ConnectionError, SelfConnectionError
from plappy.plappyconfig import config
from plappy.samplebuffer import SampleBuffer


class IO(Connectable):
    """A generic Input/Output object.

        label (str): Used to identify the IO object
        connections (set): A set of other IO's that it is connected to
        buffer (SampleBuffer): Stores data
        bufstate (int): A flag to indicate the state of the IO
    """

    def __init__(self, label: str):
        """Initialize IO with a label, connections, and an empty buffer."""
        super().__init__(label)
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

    def patch_helper(self):
        return {
            'class': type(self).__name__,
            'label': self.label,
            'connections': tuple(conn.label for conn in self.connections)
        }

    def connected(self, io: 'Connectable') -> bool:
        """Return whether self is connected to io"""
        return super().connected(io) or io in self.connections

    def disconnected(self) -> bool:
        """Return whether self is completely disconnected"""
        return super().disconnected() or len(self.connections) == 0

    def connect(self, conn: 'Connectable', **kwargs) -> 'Connectable':
        """Connect to another IO"""
        if conn.has_connector():
            return self.connect(conn.connector(**kwargs))

        # If they are already connected, don't do anything
        if self.connected(conn) or conn is self:
            return conn

        # Check that the two can be connected
        self.connect_check(conn)
        conn.connect_check(self)

        # Check that all of the connections can be connected to each other
        connection_union = conn.connections | self.connections
        for connection in connection_union:
            # Check each connection with every other connection
            for connection_2 in connection_union:
                if connection is not connection_2:
                    connection.connect_check(connection_2)
                    connection_2.connect_check(connection)

            # Check each connection with self and conn
            self.connect_check(connection)
            conn.connect_check(connection)
            connection.connect_check(self)
            connection.connect_check(conn)

        # OK. Copy the connection union, then add conn to self and self to conn.
        self.connections, conn.connections = set(connection_union), set(connection_union)
        self.connections.add(conn)
        conn.connections.add(self)

        # And add conn and self to every other connection
        for connection in connection_union:
            connection.connections.update((self, conn))

        # Return
        return super().connect(conn, **kwargs)

    def connect_check(self, conn: 'Connectable') -> None:
        """Raise a ConnectionError if the connection won't work"""
        super().connect_check(conn)

        if conn is self:
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
        return super().disconnect()

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

    def tick(self) -> 'IO':
        """Called by devices, action is implementation dependent"""
        return self


class MultiIO(Connectable):
    def __init__(self, label: str, ios: set or None = None):
        super().__init__(label)
        self.ios = ios if ios is not None else set()

    def add_io(self, io: IO) -> 'MultiIO':
        self.ios.add(io)
        return self

    def connect(self, other: 'Connectable', **kwargs):
        for io in self.ios:
            io.connect(other, **kwargs)
        return super().connect(other, **kwargs)

    def onconnect(self, other: 'Connectable', **kwargs):
        for io in self.ios:
            io.connect(other, **kwargs)
        return super().onconnect(other, **kwargs)


class Input(IO):
    """An Input object is an IO object with additional restrictions and has
    different bufstates after load() and tick()."""

    def __gt__(self, other: 'IO') -> 'IO':
        """Create a useful warning when trying to connect stuff."""
        raise ConnectionError(f"Arrow (<) must point from an Output, not {type(self).__name__} '{self.label}'")

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

    def __lt__(self, other: 'IO') -> 'IO':
        """Create a useful warning when trying to connect stuff."""
        raise ConnectionError(f"Arrow (<) must point to an Input, not {type(self).__name__} '{self.label}'")

    def load(self, buffer: SampleBuffer or None) -> 'Output':
        """Load buffer, then set bufstate to ready_to_push"""
        super().load(buffer)
        self.bufstate = config.bufstate.ready_to_push
        return self

    def tick(self) -> 'Output':
        """Called by devices, pushes content to connections and clears itself."""
        return self.flush()

    def connect_check(self, conn: 'IO') -> None:
        """Prevent an Output from being connected to another Output"""
        super().connect_check(conn)

        if isinstance(conn, type(self)):
            raise ConnectionError(
                f"Cannot connect two Outputs ('{self.label}' and '{conn.label}'), use a SimpleMixer or Mixer")

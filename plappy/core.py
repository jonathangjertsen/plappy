class Connectable(object):
    def __init__(self, label: str, *args, **kwargs):
        self.label = label
        self.connections = set()

    def __str__(self) -> str:
        """Same as __repr__"""
        return repr(self)

    def __neg__(self) -> 'Connectable':
        """This makes -self the same as -self, --self, ---self etc."""
        return self

    def __sub__(self, other: 'Connectable') -> 'Connectable':
        """This lets you connect two Connectables with c1 - c2"""
        return self.connect(other)

    def __mul__(self, other: 'Connectable') -> 'Connectable':
        """This lets you connect two Connectables with c1 * c2"""
        return self - other

    def __invert__(self) -> 'Connectable':
        """This lets you disconnect an IO with ~io"""
        return self.disconnect()

    def __lt__(self, other: 'Connectable') -> 'Connectable':
        """Allows for connections with arrow syntax."""
        return self.connect(other, which='in')

    def __gt__(self, other: 'Connectable') -> 'Connectable':
        """Allows for connections with arrow syntax."""
        return self.connect(other, which='out')

    def connect(self, other: 'Connectable', **kwargs):
        """Subclasses should call super() last"""
        if other.has_connector():
            other_connector = other.connector(**kwargs)
        else:
            other_connector = other

        if self.has_connector():
            self_connector = self.connector(**kwargs)
            self_connector.connect(other_connector, **kwargs)
        else:
            self_connector = self

        if other.has_onconnect():
            other_connector.onconnect(self_connector, **kwargs)

        return other

    def disconnect(self):
        if self.has_connector():
            ~(self.connector())
        return self

    def connect_check(self, other: 'Connectable'):
        pass

    def connected(self, other: 'Connectable'):
        return False

    def disconnected(self):
        return False

    def has_connector(self):
        return hasattr(self, 'connector')

    def has_onconnect(self):
        return hasattr(self, 'onconnect')

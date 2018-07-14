"""
samplebuffer module - The main data container used by Plappy

Classes:
    * SampleBuffer(object) - Data container which can be used for copy-on-modification
"""
import numpy as np

class SampleBuffer(object):
    """Wrapper around np.array with manual reference counting used to enable
    efficient transfer of data from IO to IO (data is only copied before
    modification)

        array (np.ndarray): The actual data
        refs (set): The set of all SampleBuffers which refer to self.array
    """

    def __init__(self, other: 'SampleBuffer' or None = None):
        """Initialize with data array and reference set"""
        self.array = None if other is None else other.array
        self.refs = set() if other is None else other.refs
        self.refs.add(self)

    def __repr__(self) -> str:
        """Return an abbreviated view into the array"""
        if self.array is not None:
            array_repr = repr(self.array)
            array_repr = array_repr[:30] + " ... " + array_repr[-30:]
        else:
            array_repr = "None"

        return f"SampleBuffer(id={id(self)}, nrefs={len(self.refs)}, array={array_repr})"

    def __str__(self) -> str:
        """Same as __repr__"""
        return repr(self)

    def __hash__(self) -> int:
        """Used to make a set of refs"""
        return hash(f"SampleBufferId{id(self)}")

    def __eq__(self, other: 'SampleBuffer') -> bool:
        """SampleBuffers are equal in value if they have the same array"""
        return np.array_equal(self.array, other.array)

    def same_ref(self, other: 'SampleBuffer') -> bool:
        """Return whether two SampleBuffers reference the same array"""
        return self.array is other.array

    @classmethod
    def from_array(cls, array: np.ndarray) -> 'SampleBuffer':
        """Return a SampleBuffer with the data from the numpy array"""
        sample_buf = cls()
        sample_buf.array = array
        return sample_buf

    def destroy(self):
        """Make self equivalent to a new SampleBuffer()"""
        self.array = None
        if self in self.refs:
            self.refs.remove(self)
        self.refs = { self, }

    def prepare_to_modify(self) -> 'SampleBuffer':
        """Clone own array and remove references to self from other SampleBuffers"""
        if len(self.refs) > 1:
            temp = np.copy(self.array)
            self.destroy()
            self.array = temp
        return self

    def empty(self) -> bool:
        """Return whether the array is equivalent to a new SampleBuffer()"""
        return self.array is None and len(self.refs) == 1

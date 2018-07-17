"""
exceptions module - Plappy-specific exceptions

Classes:
    * PlappyError(Exception) - any Plappy specific error
    * ConnectionError(PlappyError) - raised when attempting to connect IOs that should not be connected
    * SelfConnectionError(ConnectionError) - raised when attempting to connect to self
"""
class PlappyError(Exception): pass

class ConnectionError(PlappyError): pass
class SelfConnectionError(ConnectionError): pass

class DeviceError(PlappyError): pass

class PatchError(PlappyError): pass
class InvalidPatchError(PatchError): pass
class IncompatibleVersionError(PatchError): pass

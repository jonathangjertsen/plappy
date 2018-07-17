"""
settings module - Subclasses of built-ins with some common accessible attributes
"""
class Setting(object):
    pass

class IntSetting(int, Setting):
    pass

class FloatSetting(float, Setting):
    pass

class ListSetting(list, Setting):
    pass

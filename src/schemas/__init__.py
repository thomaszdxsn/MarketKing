"""
author: thomaszdxsn
"""
import dataclasses
from abc import ABC
from dataclasses import asdict, dataclass, field


class DataClassAbstract(ABC):

    def to_dict(self, dict_factory=dict):
        return asdict(self, dict_factory=dict_factory)


@dataclass
class Params(DataClassAbstract):
    args: tuple = tuple()
    kwargs: dict = field(default_factory=lambda: dict())


def add_slots(cls):
    # source: https://github.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if '__slots__' in cls.__dict__:
        raise TypeError(f'{cls.__name__} already specifies __slots__')

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in dataclasses.fields(cls))
    cls_dict['__slots__'] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop('__dict__', None)
    # And finally create the class.
    qualname = getattr(cls, '__qualname__', None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls


def FloatField():
    pass

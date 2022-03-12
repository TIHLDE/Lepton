from __future__ import absolute_import, unicode_literals

import enum


class DeconstructableEnum(enum.Enum):
    """
    Enums that have a Django migration compatible ``deconstruct()`` method.
    """
    def deconstruct(self):
        return ('.'.join([type(self).__module__, type(self).__name__]),
                (self.value,), {})


class PrettyEnum(enum.Enum):
    """
    Enums with a nice str representation::

        class MyEnum(PrettyEnum):
            foo = "Foo"
            bar = "Bar"
            baz = "Baz"

    The Enum value is automatically generated, numbering from 1 upwards, using
    the AutoNumber receipe from https://docs.python.org/3.4/library/enum.html
    """

    def __new__(cls, name, *args):
        # Still go for auto-numbered things
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, name):
        self.verbose_name = name

    def __str__(self):
        return str(self.verbose_name)


class ChoiceEnum(PrettyEnum, DeconstructableEnum):
    """
    Enums that work nicely with an EnumChoiceField
    """
    pass

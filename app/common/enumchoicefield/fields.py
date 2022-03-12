from __future__ import absolute_import, unicode_literals

from django.db.models.fields import Field

from .forms import EnumField


class EnumChoiceField(Field):
    """
    A field that generates choices from an ``enum.Enum``.

    The ``EnumChoiceField`` extends ``Field``, and the chosen enum value is
    stored in the database using the Enums ``name`` attributes. This keeps the
    database representation stable when adding and removing enum values.

    A ``max_length`` is automatically generated from the Enum ``name``
    attributes. If you add a new, longer Enum value, or remove the longest Enum
    value, the generated ``max_length`` will change. To prevent this, you can
    supply a ``max_length`` as normal, and this will be used instead.

    If a default choice is supplied, the Enum must have a ``deconstruct``
    method. If your Enum inherits from ``DeconstructableEnum``, this will be
    handled for you.

    The display value for the Enums is taken from the ``str`` representation
    of each value. By default this is something like ``MyEnum.foo``, which is
    not very user friendly. ``PrettyEnum`` makes defining a better ``str``
    representation easy.

    ``enumchoicefield.enum.ChoiceEnum`` combines both ``DeconstructableEnum``
    and ``PrettyEnum`` into a class that works very nicely with an
    ``EnumChoiceField``.
    """

    empty_strings_allowed = False

    def __init__(self, enum_class, *args, **kwargs):
        self.enum = enum_class
        kwargs.setdefault('max_length', max(
            len(item.name) for item in enum_class))
        super(EnumChoiceField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        Convert a string from the database into an Enum value
        """
        if value is None:
            return value
        return self.enum[value]

    def to_python(self, value):
        """
        Convert a string from a form into an Enum value.
        """
        if value is None:
            return value
        if isinstance(value, self.enum):
            return value
        return self.enum[value]

    def get_prep_value(self, value):
        """
        Convert an Enum value into a string for the database
        """
        if value is None:
            return None
        if isinstance(value, self.enum):
            return value.name
        raise ValueError("Unknown value {value:r} of type {cls}".format(
            value=value, cls=type(value)))

    def deconstruct(self):
        name, path, args, kwargs = super(EnumChoiceField, self).deconstruct()
        kwargs['enum_class'] = self.enum
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'form_class': EnumField,
            'enum': self.enum,
        }
        defaults.update(kwargs)
        out = super(EnumChoiceField, self).formfield(**defaults)
        return out

    def get_internal_type(self):
        return "CharField"

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return '' if value is None else value.name

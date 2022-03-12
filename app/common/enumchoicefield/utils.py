from __future__ import absolute_import, unicode_literals

from django.db.models import Case, IntegerField, When


def order_enum(field, members):
    """
    Make an annotation value that can be used to sort by an enum field.

    ``field``
        The name of an EnumChoiceField.

    ``members``
        An iterable of Enum members in the order to sort by.

    Use like:

    .. code-block:: python

        desired_order = [MyEnum.bar, MyEnum.baz, MyEnum.foo]
        ChoiceModel.objects\\
            .annotate(my_order=order_enum('choice', desired_order))\\
            .order_by('my_order')

    As Enums are iterable, ``members`` can be the Enum itself
    if the default ordering is desired:

    .. code-block:: python

        ChoiceModel.objects\\
            .annotate(my_order=order_enum('choice', MyEnum))\\
            .order_by('my_order')

    Any enum members not present in the list of members
    will be sorted to the end of the results.

    """
    members = list(members)

    return Case(
        *(When(**{field: member, 'then': i})
          for i, member in enumerate(members)),
        default=len(members),
        output_field=IntegerField())

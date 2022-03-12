from django.contrib.admin.filters import ChoicesFieldListFilter
from django.utils.translation import gettext_lazy as _


class EnumListFilter(ChoicesFieldListFilter):
    """
    A FieldListFilter for use in Django admin in combination with an
    :class:`~enumchoicefield.fields.EnumChoiceField`. Use like:

    .. code-block:: python

        class FooModelAdmin(ModelAdmin):
            list_filter = [
                ('enum_field', EnumListFilter),
            ]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enum = self.field.enum
        self.used_parameters = {
            k: self.enum[v] for k, v in self.used_parameters.items()}

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All'),
        }
        for member in self.enum:
            yield {
                'selected': (member.name) == self.lookup_val,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: member.name}),
                'display': str(member),
            }

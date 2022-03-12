import django
from django.core.exceptions import ValidationError
from django.forms.fields import Field
from django.forms.utils import flatatt
from django.forms.widgets import Widget
from django.utils.encoding import force_str
from django.utils.html import format_html, mark_safe
from django.utils.translation import gettext_lazy as _


class EnumSelect(Widget):
    allow_multiple_selected = False

    def __init__(self, members=None, attrs=None):
        super(EnumSelect, self).__init__(attrs)
        self.members = members

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        else:
            attrs = attrs.copy()

        attrs['name'] = name
        if django.VERSION >= (1, 11):
            final_attrs = self.build_attrs(self.attrs, attrs)
        else:
            final_attrs = self.build_attrs(attrs)
        output = [format_html('<select{}>', flatatt(final_attrs))]
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def render_options(self, selected_choices):
        selected_choices = set(map(force_str, selected_choices))
        options = []
        if not self.is_required:
            options.append(self.render_option(selected_choices, None))
        options.extend(self.render_option(selected_choices, value)
                       for value in self.members)
        return '\n'.join(options)

    def render_option(self, selected_choices, option):
        if option is None:
            option_value = ''
            option_label = '---------'
        else:
            option_value = option.name
            option_label = force_str(option)

        attrs = {'value': option_value}
        if option_value in selected_choices:
            attrs['selected'] = True
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        return format_html('<option{}>{}</option>',
                           flatatt(attrs),
                           option_label)


class EnumField(Field):
    widget = EnumSelect
    members = []
    empty_value = None

    default_error_messages = {
        'invalid_choice': _('Select a valid choice. %(value)s is not one of '
                            'the available choices.'),
    }

    def __init__(self, enum, members=None, widget=None, **kwargs):
        self.enum = enum

        if members is None:
            members = list(enum)
        else:
            members = list(members)

        if widget is None:
            widget = self.widget
        if isinstance(widget, type):
            widget = widget(members)

        self.members = members

        super(EnumField, self).__init__(widget=widget, **kwargs)

    def prepare_value(self, value):
        if value in self.empty_values:
            return self.empty_value
        if isinstance(value, str):
            return value
        return value.name

    def to_python(self, value):
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value

        try:
            member = self.enum[value]
        except KeyError:
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        if member not in self.members:
            raise ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        return member

    def _get_members(self):
        return list(self._members)

    def _set_members(self, members):
        self._members = list(members)
        self.widget.members = self._members

    members = property(_get_members, _set_members)

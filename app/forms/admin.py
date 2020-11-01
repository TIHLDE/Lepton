from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from app.forms import models

# admin.site.register(models.Form)
# admin.site.register(models.EventForm)
admin.site.register(models.Field)
admin.site.register(models.Option)
admin.site.register(models.Submission)
admin.site.register(models.Answer)


class OptionInline(admin.TabularInline):
    model = models.Option


class FieldInline(admin.TabularInline):
    model = models.Field
    inlines = (OptionInline,)


# @admin.register(models.Form)
# class FormAdmin(admin.ModelAdmin):
#     inlines = (FieldInline,)

class FormChildAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    base_model = models.Form  # Optional, explicitly set here.


@admin.register(models.EventForm)
class EventFormAdmin(FormChildAdmin):
    base_model = models.EventForm
    show_in_index = True  # makes child model admin visible in main admin site
    inlines = (FieldInline,)


@admin.register(models.Form)
class FormAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = models.Form
    child_models = (models.EventForm,)
    list_filter = (PolymorphicChildModelFilter,)
    inlines = (FieldInline,)


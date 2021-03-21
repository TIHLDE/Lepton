from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from app.content import models

admin.site.register(models.Event)
admin.site.register(models.News)
admin.site.register(models.Warning)
admin.site.register(models.Category)
admin.site.register(models.JobPost)
admin.site.register(models.Priority)
admin.site.register(models.Notification)
admin.site.register(models.Cheatsheet)
admin.site.register(models.Badge)
admin.site.register(models.UserBadge)
admin.site.register(models.Page)
admin.site.register(models.ShortLink)
admin.site.register(models.Strike)


def admin_delete_registration(modeladmin, request, queryset):
    for registration in queryset:
        registration.admin_unregister()


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "is_on_wait", "has_attended")
    # Enables checks bypassing from the 'Action' dropdown in Registration overview
    actions = [
        admin_delete_registration,
    ]


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "first_name", "last_name", "user_class", "user_study")
    search_fields = ("user_id", "first_name", "last_name", "user_class", "user_study")


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"

    list_filter = ["user", "content_type", "action_flag"]

    search_fields = ["object_repr", "change_message"]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "object_link",
        "action_flag",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse(
                    "admin:%s_%s_change" % (ct.app_label, ct.model),
                    args=[obj.object_id],
                ),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"

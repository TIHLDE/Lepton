from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from app.content import models

admin.site.register(models.Event)
admin.site.register(models.News)
admin.site.register(models.Category)
admin.site.register(models.Priority)
admin.site.register(models.Notification)
admin.site.register(models.Cheatsheet)
admin.site.register(models.Badge)
admin.site.register(models.UserBadge)
admin.site.register(models.Page)
admin.site.register(models.ShortLink)


@admin.register(models.Strike)
class StrikeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "event",
        "description",
        "strike_size",
    )
    raw_id_fields = (
        "user",
        "event",
        "creator",
    )
    search_fields = (
        "user__user_id",
        "event__title",
        "user__first_name",
        "user__last_name",
    )


def admin_delete_registration(modeladmin, request, queryset):
    for registration in queryset:
        registration.admin_unregister()


@admin.register(models.Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "is_on_wait", "has_attended")
    search_fields = (
        "user__user_id",
        "event__title",
        "user__first_name",
        "user__last_name",
    )
    # Enables checks bypassing from the 'Action' dropdown in Registration overview
    actions = [
        admin_delete_registration,
    ]


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "first_name", "last_name", "user_class", "user_study")
    search_fields = ("user_id", "first_name", "last_name", "user_class", "user_study")


class StrikesOverview(models.User):
    class Meta:
        verbose_name_plural = "Strikes Overview"
        proxy = True


@admin.register(StrikesOverview)
class StrikesOverviewAdmin(UserAdmin):
    list_display = (
        "user_id",
        "first_name",
        "last_name",
        "active_strikes",
    )

    def active_strikes(self, obj):
        return obj.number_of_strikes

    def get_actions(self, request):
        """Disallow bulk modifications/deletions of users through this panel."""
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        active_strikes = models.Strike.objects.active()
        return qs.filter(strikes__in=active_strikes).distinct()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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

from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from app.common.enums import GroupType
from app.content import models
from app.group.models.membership import Membership

admin.site.register(models.News)
admin.site.register(models.Category)
admin.site.register(models.PriorityPool)
admin.site.register(models.Cheatsheet)
admin.site.register(models.Page)
admin.site.register(models.ShortLink)
admin.site.register(models.Toddel)


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
    readonly_fields = ("created_at", "updated_at")
    list_filter = (
        "is_on_wait",
        "has_attended",
        "event",
        "user",
    )
    # Enables checks bypassing from the 'Action' dropdown in Registration overview
    actions = [
        admin_delete_registration,
    ]


class SlackConnectedListFilter(admin.SimpleListFilter):
    """Filters users checking if they have connected to their Slack-user"""

    title = "har tilkoblet Slack-bruker"
    parameter_name = "slack_connected"

    def lookups(self, *args, **kwargs):
        return (
            ("true", "Ja"),
            ("false", "Nei"),
        )

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.exclude(slack_user_id__exact="")
        if self.value() == "false":
            return queryset.filter(slack_user_id__exact="")


class AffiliatedStudyListFilter(admin.SimpleListFilter):
    """Filters users checking if they're connected to a study"""

    title = "har studie-medlemskap"
    parameter_name = "affiliated_study"

    def lookups(self, *args, **kwargs):
        return (
            ("true", "Ja"),
            ("false", "Nei"),
        )

    def queryset(self, request, queryset):
        connected_query = Exists(
            Membership.objects.filter(
                user__user_id=OuterRef("pk"), group__type=GroupType.STUDY
            )
        )
        if self.value() == "true":
            return queryset.filter(connected_query)
        if self.value() == "false":
            return queryset.filter(~connected_query)


class AffiliatedStudyyearListFilter(admin.SimpleListFilter):
    """Filters users checking if they're connected to a studyyear"""

    title = "har studieår-medlemskap"
    parameter_name = "affiliated_studyyear"

    def lookups(self, *args, **kwargs):
        return (
            ("true", "Ja"),
            ("false", "Nei"),
        )

    def queryset(self, request, queryset):
        connected_query = Exists(
            Membership.objects.filter(
                user__user_id=OuterRef("pk"), group__type=GroupType.STUDYYEAR
            )
        )
        if self.value() == "true":
            return queryset.filter(connected_query)
        if self.value() == "false":
            return queryset.filter(~connected_query)


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "first_name", "last_name")
    search_fields = ("user_id", "first_name", "last_name")

    list_filter = (
        "gender",
        "public_event_registrations",
        AffiliatedStudyListFilter,
        AffiliatedStudyyearListFilter,
        SlackConnectedListFilter,
    )


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "location", "category", "organizer")
    search_fields = (
        "title",
        "description",
        "location",
    )

    list_filter = (
        "sign_up",
        "start_date",
        "category",
        "organizer",
    )


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
    actions = None

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
        if "admin/logentry" in request.path:
            return False
        return True

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


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


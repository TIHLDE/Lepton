from django.contrib import admin

from app.group import models

admin.site.register(models.Group)
admin.site.register(models.Law)


@admin.register(models.Fine)
class FineAdmin(admin.ModelAdmin):
    list_filter = (
        "payed",
        "approved",
        "group",
        "user",
    )


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_filter = (
        "membership_type",
        "group",
        "user",
    )

    search_fields = [
        "user__first_name",
        "user__last_name"
    ]


@admin.register(models.MembershipHistory)
class MembershipHistoryAdmin(admin.ModelAdmin):
    list_filter = (
        "membership_type",
        "group",
        "user",
    )

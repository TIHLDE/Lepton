from django.contrib import admin

from app.badge import models


@admin.register(models.UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge")
    search_fields = (
        "user__user_id",
        "user__first_name",
        "user__last_name",
        "badge__title",
        "badge__description",
        "badge__badge_category__name",
    )
    list_filter = (
        "user__user_study",
        "user__user_class",
        "user__is_staff",
        "user__is_active",
        "badge__badge_category",
    )


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "badge_category")
    search_fields = (
        "title",
        "description",
        "badge_category__name",
    )
    list_filter = ("badge_category",)


admin.site.register(models.BadgeCategory)

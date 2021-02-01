from django.contrib import admin

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

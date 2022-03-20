from django.contrib import admin

from app.communication.models import (
    Mail,
    Notification,
    UserNotificationSetting,
    Warning,
)


class MailAdmin(admin.ModelAdmin):
    list_filter = (
        "sent",
        "users__user_id",
        "eta",
    )


class UserNotificationSettingAdmin(admin.ModelAdmin):
    list_filter = (
        "email",
        "website",
        "slack",
        "notification_type",
        "user",
    )


admin.site.register(Mail, MailAdmin)
admin.site.register(Notification)
admin.site.register(UserNotificationSetting, UserNotificationSettingAdmin)
admin.site.register(Warning)

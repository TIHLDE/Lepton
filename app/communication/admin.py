from django.contrib import admin

from app.communication.models import Banner, Mail, Notification, Warning


class MailAdmin(admin.ModelAdmin):
    list_filter = (
        "sent",
        "users__user_id",
        "eta",
    )


admin.site.register(Mail, MailAdmin)
admin.site.register(Notification)
admin.site.register(Warning)
admin.site.register(Banner)

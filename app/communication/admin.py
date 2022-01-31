from django.contrib import admin

from app.communication.models.mail import Mail


class MailAdmin(admin.ModelAdmin):
    list_filter = (
        "sent",
        "users__user_id",
        "eta",
    )


admin.site.register(Mail, MailAdmin)

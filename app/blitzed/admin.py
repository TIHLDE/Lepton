from django.contrib import admin

from app.blitzed.models.session import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass

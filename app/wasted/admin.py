from django.contrib import admin

from app.wasted.models.session import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass

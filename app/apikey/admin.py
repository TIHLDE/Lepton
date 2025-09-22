from django.contrib import admin

from app.apikey.models.key import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "is_active")
    search_fields = ("title", "description", "key")
    list_filter = ("is_active",)

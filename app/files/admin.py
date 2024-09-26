from django.contrib import admin

from app.files import models

admin.site.register(models.Gallery)

@admin.register(models.Gallery)
class FineAdmin(admin.ModelAdmin):
    list_filter = (
        ""
    )
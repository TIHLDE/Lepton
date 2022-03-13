from django.contrib import admin

from app.emoji import models


@admin.register(models.CustomEmoji)
class CustomEmojiAdmin(admin.ModelAdmin):
    fields = ("img", "short_names")
    pass


@admin.register(models.CustomShortName)
class CustomShortNameAdmin(admin.ModelAdmin):
    pass

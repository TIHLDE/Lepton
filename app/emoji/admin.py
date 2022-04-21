from django.contrib import admin

from app.emoji import models
from app.emoji.models.custom_short_name import CustomShortName


class InlineCustomShortNameAdmin(admin.TabularInline):
    model = CustomShortName
    pass


@admin.register(models.CustomEmoji)
class CustomEmojiAdmin(admin.ModelAdmin):
    fields = ("img",)
    inlines = [InlineCustomShortNameAdmin]
    pass


@admin.register(models.CustomShortName)
class CustomShortNameAdmin(admin.ModelAdmin):
    pass

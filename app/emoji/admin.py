from django.contrib import admin

from app.emoji.models.custom_emoji import CustomEmoji
from app.emoji.models.custom_short_name import CustomShortName
from app.emoji.models.reaction import Reaction


class InlineCustomShortNameAdmin(admin.TabularInline):
    model = CustomShortName


@admin.register(CustomEmoji)
class CustomEmojiAdmin(admin.ModelAdmin):
    fields = ("img",)
    inlines = [InlineCustomShortNameAdmin]


@admin.register(CustomShortName)
class CustomShortNameAdmin(admin.ModelAdmin):
    pass


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    pass

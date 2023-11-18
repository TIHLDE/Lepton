from django.contrib import admin

from app.emoji.models.reaction import Reaction


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    pass

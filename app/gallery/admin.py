from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from app.gallery.models.picture import Album, Picture


class PictureInline(admin.TabularInline):
    model = Picture

@admin.register(Album)
class AlbumAdmin(ModelAdmin):
    base_model = Album
    inlines = (
        PictureInline,
    )

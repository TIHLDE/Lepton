from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from app.gallery.models.picture import Picture


@admin.register(Picture)
class PictureAdmin(ModelAdmin):
    base_model = Picture

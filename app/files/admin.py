from django.contrib import admin

from app.files import models

admin.site.register(models.UserGallery)
admin.site.register(models.File)

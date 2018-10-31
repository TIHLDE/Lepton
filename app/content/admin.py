from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Event)
admin.site.register(models.EventList)
admin.site.register(models.News)
admin.site.register(models.Poster)

admin.site.register(models.Image)
admin.site.register(models.ImageGallery)

admin.site.register(models.Grid)
admin.site.register(models.ManualGrid)
admin.site.register(models.ManualGridItem)
admin.site.register(models.RecentFirstGrid)
admin.site.register(models.Warning)
admin.site.register(models.Category)
admin.site.register(models.JobPost)
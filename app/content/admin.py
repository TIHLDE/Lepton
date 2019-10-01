from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Event)
admin.site.register(models.News)

admin.site.register(models.Warning)
admin.site.register(models.Category)
admin.site.register(models.JobPost)
admin.site.register(models.User)
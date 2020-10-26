from django.contrib import admin

from app.forms import models
# Register your models here.
admin.site.register(models.Form)
admin.site.register(models.EventForm)
admin.site.register(models.Field)
admin.site.register(models.Option)
admin.site.register(models.Submission)
admin.site.register(models.Answer)

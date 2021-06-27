from django.contrib import admin

from app.ctf import models

admin.site.register(models.Event)
admin.site.register(models.Challenge)
admin.site.register(models.Submission)

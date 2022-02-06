from django.contrib import admin

from app.badge import models



admin.site.register(models.Badge)
admin.site.register(models.UserBadge)
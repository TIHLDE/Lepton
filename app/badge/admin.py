from django.contrib import admin

from app.badge import models

admin.site.register(models.BadgeCategory)
admin.site.register(models.UserBadge)
admin.site.register(models.Badge)

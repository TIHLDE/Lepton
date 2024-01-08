from django.contrib import admin
from .models import DataDistributions


# Register your models here.
class DataDistributionsAdmin(admin.ModelAdmin):
    pass


admin.site.register(DataDistributions, DataDistributionsAdmin)

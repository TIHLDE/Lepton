from django.contrib import admin

from app.career.models.job_post import JobPost
from app.career.models.weekly_business import WeeklyBusiness

admin.site.register(JobPost)
admin.site.register(WeeklyBusiness)

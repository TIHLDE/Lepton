from django.contrib import admin

from app.codex.models.registration import CourseRegistration
from app.codex.models.course import Course


admin.site.register(Course)
admin.site.register(CourseRegistration)
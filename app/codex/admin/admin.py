from django.contrib import admin

from app.codex.models.course import Course
from app.codex.models.registration import CourseRegistration

admin.site.register(Course)
admin.site.register(CourseRegistration)

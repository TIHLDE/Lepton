from django.contrib import admin

from app.codex.models.event import CodexEvent
from app.codex.models.registration import CodexEventRegistration

admin.site.register(CodexEvent)
admin.site.register(CodexEventRegistration)

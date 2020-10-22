import uuid

from django.db import models
from enumchoicefield import EnumChoiceField

from app.content.models.event import Event
from app.util.models import BaseModel
from app.forms.enums import FormType, FormFieldType


class Form(BaseModel):

    form_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    type = EnumChoiceField(FormType, default=FormType.GENERAL)

    class Meta:
        abstract = True


class EventForm(Form):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="forms")
    type = EnumChoiceField([FormType.SURVEY, FormType.EVALUATION], default=FormType.SURVEY)

    class Meta:
        unique_together = (("event", "type"), )
        verbose_name = "Event form"
        verbose_name_plural = "Event forms"


class Field(models.Model):

    form_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    title = models.CharField(max_length=200)
    type = EnumChoiceField(FormFieldType, default=FormType.GENERAL)
    required = models.BooleanField(default=False)



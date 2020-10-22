from django.db import models

from enumchoicefield import EnumChoiceField

from app.util.models import BaseModel


class Form(BaseModel):

    title = models.CharField(max_length=200)
    user_study = EnumChoiceField(FormType, default=FormType.DEFAULT)


    class Meta:
        abstract = True

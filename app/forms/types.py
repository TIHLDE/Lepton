import graphene
from graphene_django import DjangoObjectType

from app.content.types import EventType
from app.forms.models import EventForm, Field, Form


class FieldType(DjangoObjectType):
    class Meta:
        model = Field
        fields = "__all__"


class FormInterface(graphene.Interface):

    id = graphene.UUID()
    title = graphene.String()


class FormType(DjangoObjectType):
    class Meta:
        model = Form
        interfaces = (FormInterface,)

    fields = graphene.List(FieldType)

    def resolve_fields(self, info, **kwargs):
        return self.fields


class EventFormType(DjangoObjectType):
    class Meta:
        model = EventForm
        fields = ("id", "title", "type", "fields")
        interfaces = (FormInterface,)

    fields = graphene.List(FieldType)
    event = graphene.Field(EventType)

    def resolve_event(self, info, **kwargs):
        return self.event

    def resolve_fields(self, info, **kwargs):
        return self.fields


class FormUnionType(graphene.Union):
    class Meta:
        types = [FormType, EventFormType]

    @classmethod
    def resolve_type(cls, instance, info):
        print("INSTANCE: ", isinstance(instance, EventForm))

        if isinstance(instance, EventForm):
            return EventFormType

        elif isinstance(instance, Form):
            return FormType

        return None

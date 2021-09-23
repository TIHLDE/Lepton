import graphene
from graphene_django import DjangoObjectType

from app.content.types import EventType
from app.forms.models import EventForm, Form


class FormInterface(graphene.Interface):

    id = graphene.UUID()
    title = graphene.String()


class FormType(DjangoObjectType):
    class Meta:
        model = Form
        interfaces = (FormInterface,)


class EventFormType(DjangoObjectType):
    class Meta:
        model = EventForm
        fields = ("id", "title", "type")
        interfaces = (FormInterface,)

    event = graphene.Field(EventType)

    def resolve_event(self, info, **kwargs):
        return self.event


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

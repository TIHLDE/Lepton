import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.forms import models


class FormFactory(DjangoModelFactory):
    class Meta:
        model = models.Form

    title = factory.Sequence(lambda n: f"Form {n}")


class EventFormFactory(FormFactory):
    class Meta:
        model = models.EventForm

    event = factory.SubFactory(EventFactory)


class FieldFactory(DjangoModelFactory):
    class Meta:
        model = models.Field

    title = factory.Sequence(lambda n: f"Field {n}")
    form = factory.SubFactory(FormFactory)


class OptionFactory(DjangoModelFactory):
    class Meta:
        model = models.Option

    title = factory.Sequence(lambda n: f"Option {n}")
    field = factory.SubFactory(FieldFactory)


class SubmissionFactory(DjangoModelFactory):
    class Meta:
        model = models.Submission

    form = factory.SubFactory(FormFactory)
    user = factory.SubFactory(UserFactory)


class Answer(DjangoModelFactory):
    class Meta:
        model = models.Answer

    submission = factory.SubFactory(SubmissionFactory)
    field = factory.SubFactory(FieldFactory)

    @factory.post_generation
    def selected_options(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for option in extracted:
                self.selected_options.add(option)

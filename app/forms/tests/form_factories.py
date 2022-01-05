import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.forms import models
from app.group.factories import GroupFactory


class FormFactory(DjangoModelFactory):
    class Meta:
        model = models.Form

    title = factory.Sequence(lambda n: f"Form {n}")
    fields = factory.RelatedFactory(
        "app.forms.tests.form_factories.FieldFactory", factory_related_name="form"
    )


class EventFormFactory(FormFactory):
    class Meta:
        model = models.EventForm

    event = factory.SubFactory(EventFactory)


class GroupFormFactory(FormFactory):
    class Meta:
        model = models.GroupForm

    group = factory.SubFactory(GroupFactory)
    can_submit_multiple = True
    is_open_for_submissions = True
    only_for_group_members = False


class FieldFactory(DjangoModelFactory):
    class Meta:
        model = models.Field

    title = factory.Sequence(lambda n: f"Field {n}")
    options = factory.RelatedFactory(
        "app.forms.tests.form_factories.OptionFactory", factory_related_name="field"
    )


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


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = models.Answer

    submission = factory.SubFactory(SubmissionFactory)
    field = factory.SubFactory(FieldFactory)

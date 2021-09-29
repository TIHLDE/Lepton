from django.conf import settings

from celery import shared_task
from sentry_sdk import capture_exception

from app.content.models.registration import Registration
from app.content.models.strike import create_strike
from app.util.mail_creator import MailCreator
from app.util.notifier import Notify
from app.util.utils import datetime_format


@shared_task
def event_sign_off_deadline_schedular(*args, **kwargs):
    from app.content.models import Event

    try:
        event = Event.objects.get(
            sign_off_deadline_schedular_id=event_sign_off_deadline_schedular.request.id
        )
        registrations = Registration.objects.filter(
            event__pk=event.id, is_on_wait=False
        )
        users = (registration.user for registration in registrations)
        description = f"Dette er en påminnelse om at avmeldingsfristen for {event.title} er imorgen. Dersom du ikke kan møte ber vi deg om å melde deg av arrangementet slik at andre kan få plassen din. Dersom du ikke melder deg av innen fristen vil du få en prikk for å ikke møte opp."
        Notify(users, f"Påminnelse om avmeldingsfrist for {event.title}").send_email(
            MailCreator("Påminnelse om avmeldingsfrist")
            .add_paragraph("Hei!")
            .add_paragraph(description)
            .add_event_button(event.id)
            .generate_string(),
            send_async=False,
        ).send_notification(description=description, link=event.website_url)
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)


@shared_task
def event_end_schedular(*args, **kwargs):
    from app.content.models import Event

    try:
        event = Event.objects.get(end_date_schedular_id=event_end_schedular.request.id)
        for registration in Registration.objects.filter(
            event__pk=event.id, has_attended=False
        ):
            create_strike("NO_SHOW", registration.user, registration.event)

        if event.evaluation:
            registrations = Registration.objects.filter(
                event__pk=event.id, has_attended=True
            )
            users = (registration.user for registration in registrations)
            description = [
                f"Vi i TIHLDE setter stor pris på at du tar deg tid til å svare på denne korte undersøkelsen angående {event.title} den {datetime_format(event.start_date)}",
                "Undersøkelsen tar ca 1 minutt å svare på, og er til stor hjelp for fremtidige arrangementer. Takk på forhånd!",
                "PS: Du kan ikke melde deg på flere arrangementer gjennom TIHLDE.org før du har svart på denne undersøkelsen. Du kan alltid finne alle dine ubesvarte spørreskjemaer i profilen din.",
            ]
            Notify(users, f"Evaluering av {event.title}").send_email(
                MailCreator(f"Evaluering av {event.title}")
                .add_paragraph("Hei!")
                .add_paragraph(description[0])
                .add_paragraph(description[1])
                .add_paragraph(description[2])
                .add_button(
                    "Åpne undersøkelsen",
                    f"{settings.WEBSITE_URL}{event.evaluation.website_url}",
                )
                .generate_string(),
                send_async=False,
            ).send_notification(
                description=" \n".join(description), link=event.evaluation.website_url
            )
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)

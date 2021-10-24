from django.conf import settings

from celery import shared_task
from sentry_sdk import capture_exception

from app.content.models.strike import create_strike
from app.util.mail_creator import MailCreator
from app.util.notifier import Notify
from app.util.utils import datetime_format


@shared_task
def event_sign_off_deadline_schedular(*args, **kwargs):
    from app.content.models import Event, User

    try:
        event = Event.objects.get(
            sign_off_deadline_schedular_id=event_sign_off_deadline_schedular.request.id
        )

        users_not_on_wait = User.objects.filter(
            registrations__event=event, registrations__is_on_wait=False
        )
        description_not_on_wait = f"Dette er en påminnelse om at avmeldingsfristen for {event.title} er imorgen. Dersom du ikke kan møte ber vi deg om å melde deg av arrangementet slik at andre kan få plassen din."
        if event.can_cause_strikes:
            description_not_on_wait += " Du kan melde deg av etter avmeldingsfristen og helt frem til 2 timer før arrangementsstart, men du vil da få 1 prikk. Dersom du ikke møter opp vil du få 2 prikker."
        Notify(
            users_not_on_wait, f"Påminnelse om avmeldingsfrist for {event.title}"
        ).send_email(
            MailCreator("Påminnelse om avmeldingsfrist")
            .add_paragraph("Hei!")
            .add_paragraph(description_not_on_wait)
            .add_event_button(event.id)
            .generate_string(),
            send_async=False,
        ).send_notification(
            description=description_not_on_wait, link=event.website_url
        )

        users_on_wait = User.objects.filter(
            registrations__event=event, registrations__is_on_wait=True
        )
        description_on_wait = f"Dette er en påminnelse om at avmeldingsfristen for {event.title} er imorgen. Det forventes at du som står på venteliste kan møte opp dersom det blir en ledig plass. Dette gjelder helt frem til 2 timer før arrangementets starttid. Det er ditt ansvar å melde deg av ventelisten, hvis det ikke passer allikevel."
        Notify(
            users_on_wait, f"Påminnelse om avmeldingsfrist for {event.title}"
        ).send_email(
            MailCreator("Påminnelse om avmeldingsfrist")
            .add_paragraph("Hei!")
            .add_paragraph(description_on_wait)
            .add_event_button(event.id)
            .generate_string(),
            send_async=False,
        ).send_notification(
            description=description_on_wait, link=event.website_url
        )
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)


@shared_task
def event_end_schedular(*args, **kwargs):
    from app.content.models import Event, User

    try:
        event = Event.objects.get(end_date_schedular_id=event_end_schedular.request.id)

        if event.can_cause_strikes:
            for registration in event.registrations.filter(
                has_attended=False, is_on_wait=False
            ):
                create_strike("NO_SHOW", registration.user, registration.event)

        if event.evaluation:
            users = User.objects.filter(
                registrations__event=event, registrations__has_attended=True
            )
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

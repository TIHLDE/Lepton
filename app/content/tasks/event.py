from datetime import timedelta

from django.conf import settings

from sentry_sdk import capture_exception

from app.celery import app
from app.common.enums import AdminGroup
from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.communication.slack import Slack
from app.constants import (
    SLACK_ARRANGEMENTER_CHANNEL_ID,
    SLACK_BEDPRES_OG_KURS_CHANNEL_ID,
)
from app.content.models.strike import create_strike
from app.util.tasks import BaseTask
from app.util.utils import datetime_format, midnight, now


@app.task(bind=True, base=BaseTask)
def run_sign_off_deadline_reminder(self, *_args, **_kwargs):
    from app.content.models.event import Event

    try:
        events = Event.objects.filter(
            runned_sign_off_deadline_reminder=False,
            sign_up=True,
            closed=False,
            sign_off_deadline__lt=midnight(now() + timedelta(days=2)),
        )

        for event in events:
            __sign_off_deadline_reminder(event)

        self.logger.info(
            f'Runned "run_sign_off_deadline_reminder" for {events.count()} events'
        )
    except Exception as e:
        capture_exception(e)


@app.task(bind=True, base=BaseTask)
def run_post_event_actions(self, *_args, **_kwargs):
    from app.content.models.event import Event

    try:
        events = Event.objects.filter(
            runned_post_event_actions=False,
            sign_up=True,
            closed=False,
            end_date__lt=midnight(now()),
        )

        for event in events:
            __post_event_actions(event)

        self.logger.info(f'Runned "run_post_event_actions" for {events.count()} events')
    except Exception as e:
        capture_exception(e)


@app.task(bind=True, base=BaseTask)
def run_sign_up_start_notifier(self, *_args, **_kwargs):
    from app.content.models.event import Event

    try:
        events = Event.objects.filter(
            runned_sign_up_start_notifier=False,
            sign_up=True,
            closed=False,
            start_registration_at__lt=now(),
        )

        for event in events:
            __sign_up_start_notifier(event)

        self.logger.info(
            f'Runned "run_sign_up_start_notifier" for {events.count()} events'
        )
    except Exception as e:
        capture_exception(e)


def __sign_off_deadline_reminder(event, *_args, **_kwargs):
    from app.content.models import User

    users_not_on_wait = User.objects.filter(
        registrations__event=event, registrations__is_on_wait=False
    )
    title = f'Påminnelse om avmeldingsfrist for "{event.title}"'
    if users_not_on_wait.exists():
        description_not_on_wait = f"Dette er en påminnelse om at avmeldingsfristen for {event.title} er imorgen. Dersom du ikke kan møte ber vi deg om å melde deg av arrangementet slik at andre kan få plassen din."
        if event.can_cause_strikes:
            description_not_on_wait += " Du kan melde deg av etter avmeldingsfristen og helt frem til 2 timer før arrangementsstart, men du vil da få 1 prikk. Dersom du ikke møter opp vil du få 2 prikker."
        Notify(
            users_not_on_wait,
            title,
            UserNotificationSettingType.EVENT_SIGN_OFF_DEADLINE,
        ).add_paragraph(description_not_on_wait).add_event_link(event.id).send()

    users_on_wait = User.objects.filter(
        registrations__event=event, registrations__is_on_wait=True
    )
    if users_on_wait.exists():
        Notify(
            users_on_wait,
            title,
            UserNotificationSettingType.EVENT_SIGN_OFF_DEADLINE,
        ).add_paragraph(
            f"Dette er en påminnelse om at avmeldingsfristen for {event.title} er imorgen. Det forventes at du som står på venteliste kan møte opp dersom det blir en ledig plass. Dette gjelder helt frem til 2 timer før arrangementets starttid. Det er ditt ansvar å melde deg av ventelisten, hvis det ikke passer allikevel."
        ).add_event_link(
            event.id
        ).send()

    event.runned_sign_off_deadline_reminder = True
    event.save(update_fields=["runned_sign_off_deadline_reminder"])


def __post_event_actions(event, *_args, **_kwargs):
    from app.content.models import User

    if event.can_cause_strikes:
        for registration in event.registrations.filter(
            has_attended=False, is_on_wait=False
        ):
            create_strike("NO_SHOW", registration.user, registration.event)

    if event.evaluation:
        users = User.objects.filter(
            registrations__event=event, registrations__has_attended=True
        )
        Notify(
            users,
            f'Evaluering av "{event.title}"',
            UserNotificationSettingType.EVENT_EVALUATION,
        ).add_paragraph(
            f"Vi i TIHLDE setter stor pris på at du tar deg tid til å svare på denne korte undersøkelsen angående {event.title} den {datetime_format(event.start_date)}"
        ).add_paragraph(
            "Undersøkelsen tar ca. ett minutt å svare på, og er til stor hjelp for fremtidige arrangementer. Takk på forhånd!"
        ).add_paragraph(
            "PS: Du kan ikke melde deg på flere arrangementer gjennom TIHLDE.org før du har svart på denne undersøkelsen. Du kan alltid finne alle dine ubesvarte spørreskjemaer i profilen din."
        ).add_link(
            "Åpne undersøkelsen",
            event.evaluation.website_url,
        ).send()

    event.runned_post_event_actions = True
    event.save(update_fields=["runned_post_event_actions"])


def __sign_up_start_notifier(event, *_args, **_kwargs):
    description = f'Påmelding til "{event.title}" har nå åpnet! 🏃 Arrangementet starter {datetime_format(event.start_date)} og har {event.limit} plasser. Påmeldingen er åpen frem til {datetime_format(event.end_registration_at)}, men husk at det kan bli fullt før det. ⏲️'

    CHANNEL_ID = (
        SLACK_BEDPRES_OG_KURS_CHANNEL_ID
        if event.organizer
        and str(event.organizer.slug).lower() == str(AdminGroup.NOK).lower()
        else SLACK_ARRANGEMENTER_CHANNEL_ID
    )

    slack = (
        Slack(fallback_text=f'Påmelding til "{event.title}" har nå åpnet!')
        .add_header(event.title)
        .add_paragraph(
            f"{description}\n\n<{settings.WEBSITE_URL}{event.website_url}|*Se arrangementet her og meld deg på nå!*>"
        )
    )
    if event.image:
        slack.add_image(event.image, event.image_alt or event.title)
    slack.send(CHANNEL_ID)

    Notify(
        event.favorite_users.all(),
        f'Påmelding til "{event.title}" har nå åpnet!',
        UserNotificationSettingType.EVENT_SIGN_UP_START,
    ).add_paragraph(description).add_event_link(event.id).send()

    event.runned_sign_up_start_notifier = True
    event.save(update_fields=["runned_sign_up_start_notifier"])

from dataclasses import dataclass

from app.communication.notifier import send_html_email
from app.constants import MAIL_NOK
from app.util.mail_creator import MailCreator


class EventGiftCardAmountMismatchError(ValueError):
    message = "Antall pdf'er må tilsvare antall deltakere."


@dataclass
class EmailMessage:
    email: str
    attachment: str
    sent: bool = False


def send_gift_cards_by_email(event, files, dispatcher):
    _validate_participants_and_files_counts(event, files)
    email_messages = _map_participants_to_attachments(event, files)
    results = _generate_and_send_mails(email_messages, event)
    _send_results_to_dispatcher(results, dispatcher)


def _validate_participants_and_files_counts(event, files):
    more_files_than_participants = len(files) < event.get_has_attended().count()
    if more_files_than_participants or not len(files):
        raise EventGiftCardAmountMismatchError


def _map_participants_to_attachments(event, files):
    participant_emails = event.get_has_attended().values_list("user__email", flat=True)
    email_recipients_with_attachments = list(
        map(lambda m: EmailMessage(m[0], m[1]), zip(participant_emails, files),)
    )
    return email_recipients_with_attachments


def _generate_and_send_mails(email_messages, event):
    subject = f"Ditt gavekort fra {event.title}"
    html = (
        MailCreator(subject)
        .add_paragraph(f"Her er ditt gavekort fra {event.title}.")
        .add_paragraph(
            f"Ta kontakt med NoK på {MAIL_NOK} hvis du mener det har oppstått en feil."
        )
        .generate_string()
    )

    for message in email_messages:
        is_success = send_mail(html, message, subject)
        message.sent = is_success

    return email_messages


def send_mail(html, message, subject):
    is_success = send_html_email(
        to_mails=[message.email],
        html=html,
        subject=subject,
        attachments=[
            (
                message.attachment.name,
                message.attachment.read(),
                message.attachment.content_type,
            )
        ],
    )
    return is_success


def _send_results_to_dispatcher(results, dispatcher):
    subject = "Oversikt over gavekortfordeling"

    results_formatted = "\n".join(
        map(
            lambda result: f"{result.email} - {result.attachment.name} - {__format_email_status(result.sent)}\n",
            results,
        )
    )

    html = (
        MailCreator(subject)
        .add_paragraph(
            f"Her er oversikten over utsendte gavekort (totalt {len(results)}):\n"
        )
        .add_paragraph("Navn - Gavekort/fil - Status")
        .add_paragraph(results_formatted)
        .generate_string()
    )

    is_success = send_html_email(
        to_mails=[dispatcher.email], html=html, subject=subject
    )

    return is_success


def __format_email_status(is_sent):
    return "Sendt" if is_sent else "Ikke sendt"

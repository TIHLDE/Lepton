from django.conf import settings
from django.template.loader import render_to_string


class MailCreator:
    def __init__(self, title: str):
        """
        title: str -> Title of the mail
        """
        self.title = title
        self.content = []

    def add_paragraph(self, text: str):
        """
        Add a paragraph with text

        text: str -> Paragraph to be added to the mail
        """
        self.content.append({"type": "paragraph", "text": text})
        return self

    def add_button(self, text: str, link: str):
        """
        Add a button with a link

        text: str -> Text displayed on button
        link: str -> Link directed to on button click
        """
        self.content.append(
            {
                "type": "button",
                "text": text,
                "link": link,
            }
        )
        return self

    def add_event_button(self, event_id: int):
        """
        Add a button which links to an event

        event_id: -> Id of event which you want a link to
        """
        return self.add_button(
            "Åpne arrangement", f"{settings.WEBSITE_URL}/arrangementer/{event_id}/"
        )

    def generate_string(self):
        """
        Generate a string which can be sent in the email
        """
        return render_to_string(
            "mail_creator.html",
            context={
                "content": self.content,
                "title": self.title,
            },
        )

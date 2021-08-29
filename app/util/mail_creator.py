from django.template.loader import render_to_string


class MailCreator:
    def __init__(self, title):
        """
        title: str -> Title of the mail
        """
        self.title = title.upper()
        self.paragraphs = []
        self.button = None

    def add_paragraph(self, text):
        """
        text: str -> Paragraph to be added to the mail
        """
        self.paragraphs.append(text)
        return self

    def add_button(self, text, link):
        """
        text: str -> Text displayed on button
        link: str -> Link directed to on button click
        """
        self.button = {
            "text": text,
            "link": link,
        }
        return self

    def add_event_button(self, event_id):
        return self.add_button(
            "Se arrangement", f"https://tihlde.org/arrangementer/{event_id}/"
        )

    def generate_string(self):
        """
        Generate a string which can be sent in the email
        """
        return render_to_string(
            "mail_creator.html",
            context={
                "paragraphs": self.paragraphs,
                "button": self.button,
                "title": self.title,
            },
        )

import os

from django.conf import settings

from sentry_sdk import capture_exception
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.common.enums import EnvironmentOptions


class Slack:
    def __init__(self, fallback_text: str):
        """
        fallback_text: Text which is displayed in case the unit doesn't support blocks or in notifications
        """
        self.fallback_text = fallback_text
        self.blocks = []

    def add_header(self, header: str):
        """
        Add a header
        """
        self.blocks.append(
            {
                "type": "header",
                "text": {"type": "plain_text", "text": header, "emoji": True},
            }
        )
        return self

    def add_paragraph(self, text: str):
        """
        Add a markdown section. Must be formatted with Slack's custom markdown format
        """
        self.blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": text}}
        )
        return self

    def add_link(self, text: str, link: str):
        """
        Add a link
        """
        self.blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<{link}|*{text}*>"},
            }
        )
        return self

    def add_event_link(self, event_id: int):
        """
        Add a link to a given event
        """
        return self.add_link(
            "Åpne arrangement", f"{settings.WEBSITE_URL}/arrangementer/{event_id}/"
        )

    def add_image(self, image_url: str, image_alt: str):
        """
        Add a large image
        """
        self.blocks.append(
            {"type": "image", "image_url": image_url, "alt_text": image_alt}
        )
        return self

    def send(self, channel_id: str):
        """
        Send the built blocks to the given channel_id. The channel must be public.
        Does only send if the current environment is production.
        """
        SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if not SLACK_BOT_TOKEN or settings.ENVIRONMENT != EnvironmentOptions.PRODUCTION:
            return

        client = WebClient(token=SLACK_BOT_TOKEN)

        try:
            client.chat_postMessage(
                channel=channel_id, text=self.fallback_text, blocks=self.blocks
            )

        except SlackApiError as e:
            capture_exception(e)


def get_slack_user_id(code: str):
    SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID")
    SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET")

    if not SLACK_CLIENT_ID or not SLACK_CLIENT_SECRET:
        return ""

    token_response = WebClient().openid_connect_token(
        client_id=SLACK_CLIENT_ID, client_secret=SLACK_CLIENT_SECRET, code=code
    )

    user_token = token_response.get("access_token")
    user_info_response = WebClient(token=user_token).openid_connect_userInfo()
    return user_info_response.get("https://slack.com/user_id")

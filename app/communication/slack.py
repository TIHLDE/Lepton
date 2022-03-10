import os

from django.conf import settings

from sentry_sdk import capture_exception
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.common.enums import EnvironmentOptions


class Slack:
    def __init__(self, channel_id: str, fallback_text: str):
        """
        channel_id: Id of channel to send to. Must be public
        fallback_text: Text which is displayed in case the unit doesn't support blocks or in notifications
        """
        self.channel_id = channel_id
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

    def add_markdwn(self, text: str):
        """
        Add a markdown section. Must be formatted with Slack's custom markdown format
        """
        self.blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": text}}
        )
        return self

    def add_image(self, image_url: str, image_alt: str):
        """
        Add a large image
        """
        self.blocks.append(
            {"type": "image", "image_url": image_url, "alt_text": image_alt}
        )
        return self

    def send(self):
        SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        if not SLACK_BOT_TOKEN or settings.ENVIRONMENT != EnvironmentOptions.PRODUCTION:
            return

        client = WebClient(token=SLACK_BOT_TOKEN)

        try:
            client.chat_postMessage(
                channel=self.channel_id, text=self.fallback_text, blocks=self.blocks
            )

        except SlackApiError as e:
            capture_exception(e)

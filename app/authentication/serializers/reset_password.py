import os

from django.contrib.auth.forms import PasswordResetForm
from rest_framework import serializers

from sentry_sdk import capture_exception

from app.settings import DOMAIN


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        try:
            self.reset_form = self.password_reset_form_class(data=self.initial_data)
            if not self.reset_form.is_valid():
                raise serializers.ValidationError(self.reset_form.errors)
        except Exception as validate_email_fail:
            capture_exception(validate_email_fail)
            raise
        return value

    def save(self):
        try:
            request = self.context.get("request")
            # Set some values to trigger the send_email method.
            opts = {
                "use_https": request.is_secure(),
                "from_email": os.environ.get("EMAIL_USER") or None,
                "request": request,
                "extra_email_context": {"domain": DOMAIN},
                "html_email_template_name": "passwordResetEmail.html",
                "subject_template_name": "password_reset_subject.txt",
            }

            self.reset_form.save(**opts)

        except Exception as save_fail:
            capture_exception(save_fail)
            raise

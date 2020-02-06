from rest_framework import serializers
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class PasswordResetFormCustom():
    def get_users(self, obj):
        user = User.objects.get(user_id=obj.user_id)
        if user:
            return user
        msg = _('"{email}" was not found in our system.')
        raise ValidationError({'email': msg.format(email=email)})

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'madslun@ntnu.no'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


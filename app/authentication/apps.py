from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    name = 'app.authentication'

    def ready(self):
        # Add the set_user_groups signal receiver to user creation.
        import app.authentication.signals
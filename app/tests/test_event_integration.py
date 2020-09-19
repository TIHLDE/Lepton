from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, force_authenticate

from app.content.models import Event
from app.content.views import EventViewSet
from app.content.factories import EventFactory, UserFactory

EVENT_POST_BODY = {
    "title": "Test PRIORITIES on creation",
    "location": "Trondheim",
    "description": "",
    "sign_up": True,
    "priority": None,
    "category": None,
    "limit": "1",
    "closed": False,
    "image": "",
    "image_alt": "",
    "start_date": "2019-11-11T00:00",
    "end_date": "2019-11-11T01:00"
}


class EventViewTest(TestCase):
    def setUp(self):
        self.api_factory = APIRequestFactory()

        self.dev_user = UserFactory(user_id='dev', password='123', first_name='member', last_name='user')
        self.dev_user.groups.add(Group.objects.create(name='DevKom'))

        created_token = self.api_factory.post(f'/make/',
                                              data={'user_id': self.dev_user.user_id},
                                              format='json')
        self.token = Token.objects.get(user_id=self.dev_user.user_id)

        self.event = EventFactory()

    def test_create_event_with_registration_priorities(self):
        """ Test that an event is successfully created with priorities """
        EVENT_POST_BODY["registration_priorities"] = [
            {
                "user_class": 1,
                "user_study": 1
            },
            {
                "user_class": 2,
                "user_study": 1
            }
        ]

        data = EVENT_POST_BODY
        request = self.api_factory.post(f"/events/",
                                        data=data,
                                        format="json",
                                        HTTP_X_CSRF_TOKEN=self.token.key)

        force_authenticate(request, user=self.dev_user)
        response = EventViewSet.as_view({"post": "create"})(request) \
            .render()

        self.assertEqual(response.status_code, 201)

        event = Event.objects.get(title=EVENT_POST_BODY["title"])
        self.assertTrue(event.registration_priorities.all().exists())

    def test_update_event_as_admin(self):
        """ Test that an event is successfully updated by an admin user """
        updated_title = "test-update"
        data = {
            "title": updated_title
        }

        request = self.api_factory.put(f"/events/{self.event.pk}/",
                                       data=data,
                                       format="json",
                                       HTTP_X_CSRF_TOKEN=self.token.key)

        force_authenticate(request, user=self.dev_user)
        response = EventViewSet.as_view({"put": "update"})(request=request, pk=self.event.pk) \
            .render()

        self.event.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.event.title, updated_title)

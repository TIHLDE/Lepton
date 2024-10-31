from django.conf import settings
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status

from django_ical.views import ICalFeed
from icalendar import vCalAddress, vText

from app.content.models import User


class UserCalendarEvents(ICalFeed):
    """API endpoint to get a ICalendar with an user's events"""

    product_id = f"-//{settings.WEBSITE_URL}//UserEvents"
    timezone = f"{settings.TIME_ZONE}"
    file_name = "events.ics"

    def __call__(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        self.user = get_object_or_404(User, user_id=user_id)
        if not self.user.public_event_registrations:
            return JsonResponse(
                {
                    "detail": "Denne brukeren har skrudd av offentlig deling av påmeldinger til arrangementer. "
                    "Du kan derfor ikke hente ut brukerens arrangementer som .ics-fil"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super(UserCalendarEvents, self).__call__(request, *args, **kwargs)

    def items(self):
        return self.user.registrations.all()

    def item_guid(self, item):
        return f"{item.event.id}@{settings.WEBSITE_URL}"

    def item_title(self, item):
        return f"{'[Venteliste] ' if item.is_on_wait else ''}{item.event.title}"

    def item_description(self, item):
        return item.event.description

    def item_start_datetime(self, item):
        return item.event.start_date

    def item_end_datetime(self, item):
        return item.event.end_date

    def item_location(self, item):
        return item.event.location

    def item_organizer(self, item):
        if item.event.organizer and item.event.organizer.contact_email:
            organizer = vCalAddress(f"MAILTO:{item.event.organizer.contact_email}")
            organizer.params["cn"] = vText(item.event.organizer.name)
            return organizer
        return None

    def item_status(self, item):
        if item.event.closed:
            return "CANCELLED"
        if item.is_on_wait:
            return "TENTATIVE"
        return "CONFIRMED"

    def item_link(self, item):
        return f"{settings.WEBSITE_URL}{item.event.website_url}"

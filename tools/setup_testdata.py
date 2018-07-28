#!/usr/bin/env python3

# Sets up the database from a grid.json file.
# Run these functions using the django shell

from app.content.models import News, Poster, Event, EventList

import json

def reset_contents():
    for t in (News, Poster, Event, EventList):
        for n in t.objects.all():
            n.delete()


def load_data(path):
    json_data = None
    with open(path) as file:
        json_data = json.load(file)

    if not json_data:
        return None

    for children in json_data['children']:
        d = None
        data = children['data']

        if children['type'] == 'eventlist':
            d = EventList()
            d.name = children['data']['name']
            d.width = children['width']
            d.height = children['height']
            d.order = children['order']
            print('Created eventlist {}: {}'.format(children['data']['name'], d))
            d.save()

            for event in children['data']['events']:
                e = Event()
                for key, value in event.items():
                    if key not in ('id', 'eventlist'):
                        setattr(e, key, value)
                e.eventlist = d
                print('Created event {}: {}'.format(event['title'], e))
                e.save()


        else:
            if children['type'] == 'poster':
                d = Poster()
            elif children['type'] == 'news':
                d = News()

            d.width = children['width']
            d.height = children['height']
            d.order = children['order']

            for key, value in children['data'].items():
                setattr(d, key, value)
            print('Created: {}'.format(d))
            d.save()

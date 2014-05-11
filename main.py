#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import os
import webapp2
import jinja2

from bizit import bizitParser
from srazyinfo import srazyinfoParser
from google.appengine.ext import ndb
from google.appengine.api import users
from event import Event
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

class MainHandler(webapp2.RequestHandler):
    template_values = {}

    def get(self):
        user = users.get_current_user()

        eventlist = self.request.get('eventlist', "event")

        #ndb.AND(Event.date != None, Event.date > datetime.now().date())
        q = Event.query(ancestor=ndb.Key("events", eventlist), filters=Event.date != None).order(Event.date)
        events = q.fetch(15)

        self.template_values['events'] = events

        if user:
            self.template_values['user'] = user.nickname()
        else:
            self.redirect(users.create_login_url(self.request.uri))

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(self.template_values))

class CrawlHandler(webapp2.RedirectHandler):
    def get(self):
        events = []
        bizit = bizitParser()
        events = bizit.structuredEvents
        srazyinfo = srazyinfoParser()
        events = events + srazyinfo.structuredEvents

        self.response.write(events)

        for e in events:
            eventlist = self.request.get('eventlist', "event")
            event = Event(parent=ndb.Key("events", eventlist))

            q = Event.query(filters=e['url'] == Event.url, ancestor=ndb.Key("events", eventlist))

            eventFound = q.fetch(1)
            if(len(eventFound) == 0):
                event.url = e['url']
                event.title = e['title']
                event.img = e['img']
                event.place = e['place']
                event.text = e['text']
                event.source = e['source']
                if e['date'] is not None:
                    event.date = e['date']
                event.put()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/crawl', CrawlHandler)
], debug=True)

__author__ = 'tivvit'

from google.appengine.ext import ndb


class Event(ndb.Model):
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    img = ndb.StringProperty()
    place = ndb.StringProperty()
    text = ndb.StringProperty(indexed=False)
    source = ndb.StringProperty()
    date = ndb.DateProperty()
    inserted = ndb.DateTimeProperty(auto_now_add=True)
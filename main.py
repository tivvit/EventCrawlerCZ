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
import os
import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        url = "http://google.com"
        result = urlfetch.fetch(url)
        if result.status_code == 200:
            content = self.getEncodedContent(result)


        soup = BeautifulSoup(content)

        if user:
            template_values = {
                'user': user.nickname(),
                'loaded': content,
                'links': soup.findAll('a')
            }
        else:
            self.redirect(users.create_login_url(self.request.uri))


        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def getEncodedContent(self, result):
        '''
            bleh
        '''
        content_type = result.headers['Content-Type'] # figure out what you just fetched
        ctype, charset = content_type.split(';')
        encoding = charset[len(' charset='):] # get the encoding
        return result.content.decode(encoding) # now you have unicode

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)

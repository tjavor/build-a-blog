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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(Handler):
    def render_front(self, title="", art="", error=""):
        #arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC ")
        self.render("newpost.html", title=title, art=art, error=error) #deleted: (arts=arts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()
            art_id = str(a.key().id())
            self.redirect("/blog/" + art_id)
        else:
            error = "we need both a title and some artwork"
            self.render_front(title, art, error)

class MainHandler(Handler):
    def get(self, title="", art="", error=""):
        recently_submitted_arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 5")
        #t = jinja_env.get_template("front.html")
        #content = ""
        #for art in recently_submitted_arts:
        #    content += art.title + ", "
        #content = t.render(arts = recently_submitted_arts)
        self.render("front.html", title = title, art = art, error = error, arts = recently_submitted_arts)
        #self.response.write(content)

class Redirect(webapp2.RequestHandler):
    def get(self):
        self.redirect("blog")

class ViewPostHandler(Handler):
    def get(self, id):
        art = Art.get_by_id(int(id))
        if art:
            self.render("blog.html", art = art)
        else:
            error = "No post with that ID"
            self.render("blog.html", art = "", error = error)


app = webapp2.WSGIApplication([
    ('/', Redirect),
    ('/blog', MainHandler),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

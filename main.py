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


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch
from django.utils import simplejson



import utils
import models


class MainHandler(webapp.RequestHandler):
  def get(self):
	users = models.User.all().order('-tweetcount')
	template_values = {
		"users": users
	}
	utils.render_template(self, "views/home.html", template_values)


class PersonHandler(webapp.RequestHandler):
  def get(self, uid):
	users = models.User.all().order('-tweetcount')
	user = models.User.get_by_key_name("u_" + uid)
	tweets = models.Tweet.get(user.tweetlist)
	details = utils.get_user_details(user)
	template_values = {
		"users": users,
		"user": user,
		"tweets": tweets,
		"details": details
	}
	utils.render_template(self, "views/person.html", template_values)



class LiveHandler(webapp.RequestHandler):
	def get(self, mode):
		tweets = models.Tweet.all().order('-created_at').fetch(10)
		template_values = {
			"tweets": tweets,
			"searchterm": self.request.get("q")
		}
		if mode == "panel":
			utils.render_template(self, "views/panel.html", template_values)
		else:
			utils.render_template(self, "views/live.html", template_values)


class SearchHandler(webapp.RequestHandler):
  def get(self):
	tweets = models.Tweet.all().search(self.request.get("q")).order('-created_at').fetch(1000)
	template_values = {
		"tweets": tweets,
		"searchterm": self.request.get("q")
	}
	utils.render_template(self, "views/search.html", template_values)




class FeedHandler(webapp.RequestHandler):
	def get(self):
		if not self.request.get("page"):
			page = "1"
		else:
			page = self.request.get("page")
		url = "http://backtweets.com/search.json?q=www.dn.se&key=0d3f7e0f7874396cf456&itemsperpage=10&since_id=9436805794&page=" + page
		result = urlfetch.fetch(url)
		if result.status_code == 200:
			json = simplejson.loads(result.content)
			try:
				if len(json['tweets']) > 0:
					for rawtweet in json['tweets']:
						tweet = utils.process_tweet(rawtweet)
						self.response.out.write(tweet.text)
					taskqueue.add(url='/scrape/feed', params={"page":str(int(page) + 1)}, method='GET')
			except:
				self.response.out.write("oops")
	



def main():
	application = webapp.WSGIApplication([
			('/', MainHandler),
			('/search', SearchHandler),
			('/live()', LiveHandler),
			('/live/(panel)', LiveHandler),
			('/person/(.*)', PersonHandler),
			('/scrape/feed', FeedHandler)
	], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
  main()

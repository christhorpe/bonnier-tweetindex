from google.appengine.ext import db
from google.appengine.ext import search


class User(db.Model):
	name = db.StringProperty()
	uid = db.StringProperty()
	tweetcount = db.IntegerProperty(default=0)
	tweetlist = db.StringListProperty()


class Tweet(search.SearchableModel):
	url = db.StringProperty()
	text = db.TextProperty()
	uid = db.StringProperty()
	created_at = db.DateTimeProperty()
	user = db.ReferenceProperty(User)


class Page(db.Model):
	url = db.StringProperty()
	tweetcount = db.IntegerProperty(default=0)
	tweetlist = db.StringListProperty()
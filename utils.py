import os
import datetime
import yql

from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import models




def render_template(self, end_point, template_values):
	path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
	response = template.render(path, template_values)
	self.response.out.write(response)



def convert_twitter_datetime(theirdatetime):
	thisdatetime = datetime.datetime(int(theirdatetime[0:4]), int(theirdatetime[5:7]), int(theirdatetime[8:10]), int(theirdatetime[11:13]), int(theirdatetime[14:16]), int(theirdatetime[17:19]))
	return thisdatetime


def get_user_details(user):
	details = memcache.get("t_" + user.name)
	if not details:
		query = "select class, content from html where url = \"http://twitter.com/%s\" and (xpath=\"//div[@id='profile']//span\" or xpath=\"//li[@id='profile_tab']//span\")" % user.name
		y = yql.Public()
		yqlresponse = y.execute(query)
		details = yqlresponse['query']['results']['span']
		memcache.add("t_" + user.uid, details, 1000)
	return details


def get_max_tweet():
	tweet = models.Tweet.all().order('-uid').get()
	if tweet:
		return tweet.uid
	else:
		return "1"



def process_tweet(rawtweet):
	user_name = rawtweet['tweet_from_user']
	user_uid = rawtweet['tweet_from_user_id']
	user = models.User.get_or_insert("u_" + str(user_uid), name=user_name, uid=str(user_uid), tweetlist=[])		
	tweet_text = rawtweet['tweet_text']
	tmp1 = tweet_text.split("href=\"")
	tmpbit = tmp1[1]
	tmp2 = tmpbit.split("\">")
	tweet_link = tmp2[0].replace("?utm_source=twitterfeed&utm_medium=twitter", "")
	page = models.Page.get_or_insert(tweet_link, url=tweet_link, tweetlist=[])		
	tweet_uid = rawtweet['tweet_id']
	tweet_created = rawtweet['tweet_created_at']
	tweet = models.Tweet.get_or_insert("t_" + str(tweet_uid), text=tweet_text, uid=str(tweet_uid), created_at=convert_twitter_datetime(tweet_created), user=user)	
	if str(tweet.key()) not in user.tweetlist:
		user.tweetcount += 1
		user.tweetlist.append(str(tweet.key()))
		user.put()
	if str(tweet.key()) not in page.tweetlist:
		page.tweetcount += 1
		page.tweetlist.append(str(tweet.key()))
		page.put()
	return tweet	


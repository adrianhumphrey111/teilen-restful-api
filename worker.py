'''
Created on Oct 23, 2017

@author: adrianhumphrey
'''

from google.appengine.ext import ndb
from models import User, Comment, Post, Like, Location, Trip
import webapp2

from notificationManager import Notification


class LikeMediaPostHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key'))
        post_key = str(self.request.get('post_key'))
        Like(user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key)).put()
        
class UnLikeMediaPostHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key'))
        post_key = str(self.request.get('post_key'))
        Like.delete_like(post_key=post_key, user_key=user_key)
    
        
class CommentPostHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key'))
        post_key = str(self.request.get('post_key'))
        comment_text = str(self.request.get('comment'))
        comment = Comment(user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key), text=comment_text).put()
        
class AddFriendHandler(webapp2.RequestHandler):
    def post(self):
        User.add_friend( user_url_key=str(self.request.get('user_key')), friend_url_key=str(self.request.get('friend_key')))
        
        
class RequestFriendHandler(webapp2.RequestHandler):
    def post(self):
        User.request_friend( user_url_key=str(self.request.get('user_key')), friend_url_key=str(self.request.get('friend_key')))

class NotificationHandler(webapp2.RequestHandler):
    def post(self):
        to_key = str(self.request.get('to_key'))
        from_key = str(self.request.get('from_key'))
        type = str(self.request.get('type'))

        #Depending on the type of notification will it be a data notification or not
        result = Notification(type=type, to_user_key=to_key, from_user_key=from_key).send()

        #Do somthing with this result
        print result


        
app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/unlikePost', UnLikeMediaPostHandler),
    ('/tasks/commentPost', CommentPostHandler)
    ('/tasks/addFriend', AddFriendHandler),
    ('/tasks/handleNotification', NotificationHandler),
    ('/tasks/requestFriend', RequestFriendHandler)
], debug=True)
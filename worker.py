'''
Created on Oct 23, 2017

@author: adrianhumphrey
'''

from google.appengine.ext import ndb
from models import User, Comment, Post, Like, Location, Trip, Notification
import webapp2

from notificationManager import FBNotification


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
        
class DenyFriendHandler(webapp2.RequestHandler):
    def post(self):
        User.deny_request( user_url_key=str(self.request.get('user_key')), friend_url_key=str(self.request.get('friend_key')))
        
        
class RemoveRequestHandler(webapp2.RequestHandler):
    def post(self):
        User.remove_friend_request( user_url_key=str(self.request.get('user_key')), friend_url_key=str(self.request.get('friend_key')))
    
class RequestFriendHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key') )
        friend_key = str(self.request.get('friend_key') )
        User.request_friend( user_url_key=user_key, friend_url_key=friend_key)
        
        #Send notification
        fb_notification = FBNotification(type='friend_request', 
                                             to_user_key=friend_key,
                                             trip_key=None,
                                             from_user_key=user_key)
            
        fb_notification.send()
        
        #Create notification and add it to the friends list of notifications
        notification = Notification()
        notification.type = "friend_request"
        notification.from_user_key = user_key
        notification.to_user_key = friend_key
        notification.message = fb_notification.createMessage()
        
        user = ndb.Key(urlsafe=user_key).get( use_cache=False, use_memcache=False )
        user.notifications.append( notification )
        user.put()
        
class RemoveFriendHanlder(webapp2.RequestHandler):
    def post(self):
        User.remove_friend( user_url_key=str(self.request.get('user_key')), friend_url_key=str(self.request.get('friend_key')))

class NotificationHandler(webapp2.RequestHandler):
    def post(self):
        to_key = str(self.request.get('to_key'))
        from_key = str(self.request.get('from_key'))
        type = str(self.request.get('type'))

        #Depending on the type of notification will it be a data notification or not
        result = FBNotification(type=type, to_user_key=to_key, from_user_key=from_key).send()

        #Do somthing with this result
        print result


        
app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/unlikePost', UnLikeMediaPostHandler),
    ('/tasks/commentPost', CommentPostHandler),
    ('/tasks/denyRequest', DenyFriendHandler),
    ('/tasks/addFriend', AddFriendHandler),
    ('/tasks/removeFriend', RemoveFriendHanlder),
    ('/tasks/removeRequest', RemoveRequestHandler),
    ('/tasks/handleNotification', NotificationHandler),
    ('/tasks/requestFriend', RequestFriendHandler)
], debug=True)
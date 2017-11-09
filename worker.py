'''
Created on Oct 23, 2017

@author: adrianhumphrey
'''

from google.appengine.ext import ndb
from models import User, Comment, Post, Like, Location, Trip
import webapp2


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
        

class CreatePostHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        
        '''Start Address'''
        start_address1 = params['trip[startAddress][address1]']
        start_address2 = params['trip[startAddress][address2]']
        start_address_state = params['trip[startAddress][state]']
        start_address_city = params['trip[startAddress][city]']
        #start_address_zip_code = params['trip[startAddress][zipCode]']
        
        '''End Address'''
        end_address1 = params['trip[endAddress][address1]']
        end_address2 = params['trip[endAddress][address2]']
        end_address_state = params['trip[endAddress][state]']
        end_address_city = params['trip[endAddress][city]']
        end_address_zip_code = params['trip[endAddress][zipCode]']
        
        trip_time = params['trip[time]']
        trip_eta = params['trip[eta]']
        post_text = params['trip[post_text]']
        user_key = params['user_key']
        posted_by = params['trip[posted_by]']
        
        #Create Start Location 
        start_location = Location(address1=start_address1, address2=start_address2, city=start_address_city, state=start_address_state)
        
        #Create End Location
        end_location = Location(address1=end_address1, address2=end_address2, city=end_address_city, state=end_address_state)
        
        #Create the Trip to be associated with the post
        trip_key = Trip(start_location=start_location, end_location=end_location).put()

        post = Post.create_post(user_key=user_key, text=post_text, trip_key=trip_key)
        self.response.write('This is the response from creating post')
        
class CreateUserHandler(webapp2.RequestHandler):
    def post(self): 
        first_name=str(self.request.get('first_name'))
        last_name=str(self.request.get('last_name'))
        email=str(self.request.get('email'))
        user = User.create_new_user(first_name=first_name, last_name=last_name, email=email)
        print 'User successfully added and the id is => ' + str(user.id())
        
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
        
        
        
app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/unlikePost', UnLikeMediaPostHandler),
    ('/tasks/commentPost', CommentPostHandler),
    ('/tasks/createPost', CreatePostHandler),
    ('/tasks/createUser', CreateUserHandler),
    ('/tasks/addFriend', AddFriendHandler),
    ('/tasks/requestFriend', RequestFriendHandler)
], debug=True)
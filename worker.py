'''
Created on Oct 23, 2017

@author: adrianhumphrey
'''

from google.appengine.ext import ndb
from models import User, Comment, Post, Like
import webapp2


class LikeMediaPostHandler(webapp2.RequestHandler):
    def post(self):
        user_id = int(self.request.get('user_id'))
        post_id = int(self.request.get('post_id'))

        # This task should run at most once per second because of the datastore
        # transaction write throughput.
        def likeMediaPost(user_id, post_id):
            like = Like(user_id=user_id, post_id=post_id)
            Post.add_like(like) #like object will contain media id and user id
            
        likeMediaPost(user_id=user_id, post_id=post_id)
 
class CreatePostHandler(webapp2.RequestHandler):
    def post(self):
        user_id=int(self.request.get('user_id'))
        post_text=str(self.request.get('post_text'))
        
        post = Post.create_post(user_id=user_id, text=post_text)
        print 'User successfully added and the id is => ' + str(post.id())
        
class CreateUserHandler(webapp2.RequestHandler):
    def post(self): 
        first_name=str(self.request.get('first_name'))
        last_name=str(self.request.get('last_name'))
        email=str(self.request.get('email'))

        user = User.create_new_user(first_name=first_name, last_name=last_name, email=email)
        print 'User successfully added and the id is => ' + str(user.id())
    


app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/createPost', CreatePostHandler),
    ('/tasks/createUser', CreateUserHandler)
], debug=True)
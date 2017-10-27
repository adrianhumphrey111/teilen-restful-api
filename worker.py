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
        def likePost(user_id, post_id):
            like = Like(user_id=user_id, post_id=post_id)
            Post.add_like(like) #like object will contain media id and user id
            
        likePost(user_id=user_id, post_id=post_id)
 
class CreatePostHandler(webapp2.RequestHandler):
    def post(self):
        user_id=int(self.request.get('user_id'))
        post_text=str(self.request.get('post_text'))
        post = Post.create_post(user_id=user_id, text=post_text)
        print 'User successfully added and the id is => ' + str(post.id())
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
        user_id = int(self.request.get('user_id'))
        post_id = int(self.request.get('post_id'))
        comment_text = str(self.request.get('comment'))
        
        def commentPost(user_id, post_id, comment):
            comment = Comment(user_id=user_id, post_id=post_id, text=comment_text, likes=[])
            Post.add_comment(comment)
            
        commentPost(user_id=user_id, post_id=post_id, comment=comment_text )

class AddFriendHandler(webapp2.RequestHandler):
    def post(self):
        User.add_friend( key=ndb.Key( 'User', int(self.request.get('user_id'))), friend_id=int(self.request.get('friend_id')))
        
        
class RequestFriendHandler(webapp2.RequestHandler):
    def post(self):
        User.request_friend(key=ndb.Key( 'User', int(self.request.get('user_id'))), friend_key=ndb.Key( 'User', int(self.request.get('friend_id'))))
        
        
        
app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/commentPost', CommentPostHandler),
    ('/tasks/createPost', CreatePostHandler),
    ('/tasks/createUser', CreateUserHandler),
    ('/tasks/addFriend', AddFriendHandler),
    ('/tasks/requestFriend', RequestFriendHandler)
], debug=True)
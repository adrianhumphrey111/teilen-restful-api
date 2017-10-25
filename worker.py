'''
Created on Oct 23, 2017

@author: adrianhumphrey
'''

from google.appengine.ext import ndb
from models import User, Comment, HashTag, MediaPost, Like
import webapp2


COUNTER_KEY = 'default counter'


class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)


class LikeMediaPostHandler(webapp2.RequestHandler):
    def post(self):
        user_id = int(self.request.get('user_id'))
        media_post_id = int(self.request.get('media_post_id'))

        # This task should run at most once per second because of the datastore
        # transaction write throughput.
        def likeMediaPost(user_id, media_post_id):
            like = Like(user_id=user_id, media_post_id=media_post_id)
            MediaPost.add_like(like) #like object will contain media id and user id
            

        likeMediaPost(user_id, media_post_id)
 
class CreatePostHandler(webapp2.RequestHandler):
    def post(self):   
        media_post_id=int(self.request.get('media_post_id'))
        user_id=int(self.request.get('user_id'))
        post_text=str(self.request.get('post_text'))
        
        # This task should run at most once per second because of the datastore
        # transaction write throughput.
        @ndb.transactional
        def create_new_media_post(user_id, media_post_id, post_text):
            #Create a new post
            post = MediaPost(media_post_id=media_post_id,
                             user_id=user_id,
                             post_text=post_text,
                             likes=[],
                             comments=[],
                             )
            post.put()
            print 'The post was successfully addedd'
            
        create_new_media_post(user_id, media_post_id, post_text)
        
class CreateUserHandler(webapp2.RequestHandler):
    def post(self): 
        first_name=str(self.request.get('first_name'))
        last_name=str(self.request.get('last_name'))
        email=str(self.request.get('email'))
        
        def create_new_user(user_id, first_name, last_name, email):
            #Create a new post
            user = User(user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        email=email)
            print 'This is the user id' + str(user.key.id())
            user.put()
            

            
            
        '''Give the user a unique id'''
        user_id=245452435
        create_new_user(user_id=user_id, first_name=first_name, last_name=last_name, email=email)
    


app = webapp2.WSGIApplication([
    ('/tasks/likePost', LikeMediaPostHandler),
    ('/tasks/createPost', CreatePostHandler),
    ('/tasks/createUser', CreateUserHandler)
], debug=True)
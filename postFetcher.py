'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import Post, User, Comment
from google.appengine.ext import ndb


class PostFetcher:
    def __init__(self, user_key):
        self.key = ndb.Key(urlsafe=user_key)
        self.user_id = self.key.id()
        self.user = self.key.get()
        self.posts = []
        self.users = []
        self.add_friends()
        self.addAllPosts()
    
    def add_friends(self):
        self.users.append( self.user ) #add the user, self, to the post to fetch
        print self.user
        if hasattr(self.user, 'friend_ids'): #the user has atleast one friend
            print 'This user has friends'
            for friend_id in self.user.friend_ids:
                self.users.append( ndb.Key('User', friend_id).get() )
        else:
            print 'This user does not have friends'
            
    def addAllPosts(self):
        for user in self.users:
            for post in User.retrieve_all_post( user.key ):
                post['comments'] = self.get_post_comments(post_key=post['post_key'])
                self.posts.append( post )
                
    def get_post_comments(self, post_key):
        comments = []
        key = ndb.Key(urlsafe=post_key)
        for comment in Comment.query(Comment.post_key == key ).fetch():
            post_key_urlsafe = comment.post_key.urlsafe()
            user_key_urlsafe = comment.user_key.urlsafe()
            comment = comment.to_dict()
            comment['user'] = User.user_for_app(key.get().user_key.get().to_dict())
            comment['post_key'] = post_key_urlsafe
            comment['user_key'] = user_key_urlsafe
            comments.append( comment  )
        return comments
        
    def get_all_posts(self):
        return self.posts
    
    
        
    

'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import Post, User, Comment
from google.appengine.ext import ndb
from dateManager import DateManager


class PostFetcher:
    def __init__(self, user_key):
        self.key = ndb.Key(urlsafe=user_key)
        self.user_id = ndb.Key(urlsafe=user_key).id()
        self.user = ndb.Key(urlsafe=user_key).get()
        self.posts = []
        self.users = []
        self.user_posts = []
        self.add_friends()
        self.addAllPosts()
    
    def add_friends(self):
        self.users.append( self.user ) #add the user, self, to the post to fetch
        if hasattr(self.user, 'friend_ids'): #the user has atleast one friend
            print 'This user has friends'
            for friend_id in self.user.friend_ids:
                self.users.append( ndb.Key('User', friend_id).get() )
            
    def addAllPosts(self):
        for user in self.users:
            for post in User.retrieve_all_post( user.key ):
                key = ndb.Key(urlsafe=post['post_key'])
                post['comments'] = Comment.getCommentsForPost(post_key=key )
                self.posts.append( post )

    def get_all_user_posts(self):
        for post in User.retrieve_all_post( self.key ):
            key = ndb.Key(urlsafe=post['post_key'])
            post['comments'] = Comment.getCommentsForPost( post_key=key )
            self.user_posts.append( post )
        return self.user_posts
    
    def get_all_posts(self):
        return self.posts
        
    

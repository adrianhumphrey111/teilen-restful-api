'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import Post, User
from google.appengine.ext import ndb


class PostFetcher:
    def __init__(self, user_id):
        self.key = ndb.Key('User', user_id)
        self.user = self.key.get()
        self.posts = []
        self.users = []
        self.add_friends()
        self.addAllPosts()
    
    def add_friends(self):
        self.users.append( self.user ) #add the user, self, to the post to fetch
        if hasattr(self.user, 'friends_ids'): #the user has atleast one friend
            for friend_id in self.user.friend_ids:
                self.users.append( ndb.Key('User', friend_id).get() )
            
    def addAllPosts(self):
        for user in self.users:
            self.posts.append( User.retrieve_all_post(self.key) )
        print 'Final feed => ' + str(self.posts)
        
    def get_all_posts(self):
        return self.posts
        
    

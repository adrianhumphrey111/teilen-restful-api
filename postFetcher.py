'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import Post, User, Comment
from google.appengine.ext import ndb
from dateManager import DateManager
from datetime import datetime


class PostFetcher:
    def __init__(self, user_key):
        self.key = ndb.Key(urlsafe=user_key)
        self.user_id = ndb.Key(urlsafe=user_key).id()
        self.user = ndb.Key(urlsafe=user_key).get()
        self.posts = []
        self.users = []
        self.user_posts = []
        self.sortedPosts = []
        self.add_friends()
        self.addAllPosts()
        self.sortPost()
        self.configurePostForJson()
    
    def sortPost(self):
        self.sortedPosts = sorted( self.posts, key=lambda x: x.created_at, reverse=True)
        self.posts.sort(key=lambda r: r.created_at)
    
    def configurePostForJson(self):
        for post in self.sortedPosts:
            user_key = post.user_key.urlsafe()
            trip_key = post.trip_key.urlsafe()
            trip = post.trip_key.get()
            tz = post.time_zone
            
            '''Configure Trip'''
            return_time = DateManager(tz=tz, created_at=trip.eta).eta_time()
            post.trip.eta = return_time
            
            post = post.to_dict()
            post['created_at'] = post['time_stamp']
            post['user_key'] = user_key
            post['trip_key'] = trip_key

    
    def add_friends(self):
        self.users.append( self.user ) #add the user, self, to the post to fetch
        if hasattr(self.user, 'friend_ids'): #the user has atleast one friend
            print 'This user has friends'
            for friend_id in self.user.friend_ids:
                self.users.append( ndb.Key('User', friend_id).get() )
            
            
    def addAllPosts(self):
        for user in self.users:
            is_friend = self.user.is_friend( friend_key=user.key )
            for post in User.retrieve_all_post( user.key ):
                key = ndb.Key(urlsafe=post.post_key)
                #post['comments'] = Comment.getCommentsForPost(post_key=key )
                #post['user']['is_friend'] = is_friend
                post.comments = Comment.getCommentsForPost(post_key=key )
                post.user.is_friend = is_friend
                self.posts.append( post )

    def get_all_user_posts(self):
        for post in User.retrieve_all_post( self.key ):
            key = ndb.Key(urlsafe=post.post_key)
            post.comments = Comment.getCommentsForPost( post_key=key )
            tz = post.time_zone
            
            '''Configure Trip'''
            return_time = DateManager(tz=tz, created_at=post.trip.eta).eta_time()
            post.trip.eta = return_time
            self.user_posts.append( post )
        return self.user_posts
    
    def get_all_posts(self):
        return self.sortedPosts
        
    

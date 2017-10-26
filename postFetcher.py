'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import User

class PostFetcher:
    def __init__(self, key):
        self.key = key
        self.queryUser()
        self.post = self.grabPostFromFriends()
    
    def queryUser(self):
        self.user = self.key.get()
    

'''
Created on Oct 25, 2017

@author: adrianhumphrey
'''

from models import User

class PostFetcher:
    def __init__(self, user_id):
        self.user_id = user_id
        self.queryUser()
        self.post = self.grabPostFromFriends()
    
    def queryUser(self):
        q = User.query(User.user_id == self.user_id)
        for user in q:
            self.user = user
    

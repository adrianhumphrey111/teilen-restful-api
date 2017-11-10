#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.ext import ndb
import google
from google.appengine.api import taskqueue
from models import Post, User, Comment, Location, Trip
from postFetcher import PostFetcher
import json
import datetime

def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    if isinstance(x, google.appengine.ext.ndb.key.Key):
        return str(x)
    raise TypeError("Unknown type")

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
        
class LoginHandler(webapp2.RequestHandler):
    def post(self):
        self.response.write('You have been logged in')
        
class SearchHandler(webapp2.RequestHandler):
    def post(self):
        self.response.write('Currently scrapping web for information on your goal')
        
class LikePostTaskHandler(webapp2.RequestHandler):
    def post(self):
        task = taskqueue.add(
            url='/tasks/likePost',
            target='worker',
            params={'user_key': str(self.request.get('user_key')),
                    'post_key': str(self.request.get('post_key'))})
        
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class UnLikePostTaskHandler(webapp2.RequestHandler):
    def post(self):
        task = taskqueue.add(
            url='/tasks/unlikePost',
            target='worker',
            params={'user_key': str(self.request.get('user_key')),
                    'post_key': str(self.request.get('post_key'))})
        
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
        
class CreateMediaPostTaskHandler(webapp2.RequestHandler):
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
        post_key = Post.create_post(user_key=user_key, text=post_text, trip_key=trip_key)
        
        #SEnd Response
        self.response.headers['Content-Type'] = 'application/json' 
        obj = {'post_key': post_key,
               'trip_key': trip_key}
        self.response.write(json.dumps(obj , default=json_handler) )
        
class FetchFeedHandler(webapp2.RequestHandler):
    def get(self):
        #return a fetch object with all posts and appropriate things needed for the app to populate
        feed = PostFetcher(user_key=str(self.request.get('user_key')))
        posts = feed.get_all_posts()
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps([post for post in posts], default=json_handler))
        
class FetchUserFeedHandler(webapp2.RequestHandler):
    def get(self):
        #return a fetch object with all posts and appropriate things needed for the app to populate
        feed = PostFetcher(user_key=str(self.request.get('user_key')))
        posts = feed.get_all_user_posts()
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps([post for post in posts], default=json_handler))  
        
class UpdateUserHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.get('update_dict')
        user_key = self.request.get('user_key')
        obj = json.loads(params)
        obj.user_key = user_key
        User.updateUser(self, params)
        self.response.out.write("Updated User")
    

class CreateUserTasksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to create User to the task queue
        task = taskqueue.add(
            url='/tasks/createUser',
            target='worker',
            params={'first_name': str(self.request.get('first_name')),
                    'last_name': str(self.request.get('last_name')),
                    'email': str(self.request.get('email'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class CommentPostTasksHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key'))
        post_key = str(self.request.get('post_key'))
        comment_text = str(self.request.get('comment'))
        urlsafe_comment_key = Comment(user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key), text=comment_text).put().urlsafe()
        comment = ndb.Key(urlsafe=urlsafe_comment_key).get()
        user_key_urlsafe = comment.user_key.urlsafe()
        post_key_urlsafe = comment.post_key.urlsafe()
        comment = comment.to_dict()
        comment['user_key'] = user_key_urlsafe
        comment['post_key'] = post_key_urlsafe
        comment['comment_key'] = urlsafe_comment_key
        
        #Should be a response to the user that says, they have liked the post
        obj = {'comment': comment}
        self.response.write(json.dumps(obj , default=json_handler) )
        
class DeletePostHandler(webapp2.RequestHandler):
    def post(self):
        Post.delete_post(str(self.request.get('post_key')))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write('Post successfully deleted')
        
class AddFriendTasksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/addFriend',
            target='worker',
            params={'friend_key': str(self.request.get('friend_key')),
                    'user_key': str(self.request.get('user_key'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class RequestFriendTaksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/requestFriend',
            target='worker',
            params={'user_key': str(self.request.get('user_key')),
                    'friend_key': str(self.request.get('friend_key'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))

class UnfriendHanlder(webapp2.RequestHandler):
    def post(self):
        pass

class RemoveRequestHandler(webapp2.RequestHandler):
    def post(self):
        
        pass
        
        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api/login', LoginHandler),
    ('/api/search', SearchHandler),
    ('/api/likePost', LikePostTaskHandler),
    ('/api/unlikePost', UnLikePostTaskHandler),
    ('/api/commentPost', CommentPostTasksHandler),
    ('/api/createPost', CreateMediaPostTaskHandler),
    ('/api/fetchFeed', FetchFeedHandler),
    ('/api/fetchUserFeed', FetchUserFeedHandler),
    ('/api/createUser', CreateUserTasksHandler),
    ('/api/updateUser', UpdateUserHandler),
    ('/api/deletePost', DeletePostHandler),
    ('/api/addFriend', AddFriendTasksHandler),
    ('/api/requestFriend', RequestFriendTaksHandler),
    ('/api/unfriend', UnfriendHanlder),
    ('/api/removeRequest', RemoveRequestHandler)
], debug=True)

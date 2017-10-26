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
from google.appengine.api import taskqueue
import ast

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
            params={'user_id': str(self.request.get('user_id')),
                    'post_id': str(self.request.get('post_id'))})
        
        #Should be a response to the user that says, they have liked the post
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class CreateMediaPostTaskHandler(webapp2.RequestHandler):
    def post(self):
        
        task = taskqueue.add(
            url='/tasks/createPost',
            target='worker',
            params={'user_id': str(self.request.get('user_id')),
                    'post_text': str(self.request.get('post_text'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class FetchPostsHandler(webapp2.RequestHandler):
    def get(self):
        pass
    
class UpdateUserHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.get('update_dict')
        
        #Add this task to create User to the task queue
        task = taskqueue.add(
            url='/tasks/updateUser',
            target='worker',
            params=params)
        #Should be a response to the user that says, they have liked the post
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
    
    
    
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
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class CommentPostTasksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to create User to the task queue
        task = taskqueue.add(
            url='/tasks/commentPost',
            target='worker',
            params={'user_id': str(self.request.get('user_id')),
                    'post_id': str(self.request.get('post_id')),
                    'comment': str(self.request.get('comment'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api/login', LoginHandler),
    ('/api/search', SearchHandler),
    ('/api/likePost', LikePostTaskHandler),
    ('/api/commentPost', CommentPostTasksHandler),
    ('/api/createPost', CreateMediaPostTaskHandler),
    ('/api/fetchPost', FetchPostsHandler),
    ('/api/createUser', CreateUserTasksHandler),
    ('/api/updateUser', UpdateUserHandler),
    
    
], debug=True)

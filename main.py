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
from models import Post, User, Comment, Location, Trip, Transaction, TripRequest, Notification
from postFetcher import PostFetcher
import json
import datetime
import hashlib, uuid
from payment import Payment
from notificationManager import FBNotification
from dateManager import DateManager
import stripe
import config
import mammoth

stripe.api_key = config.stripe_api_key_secret

def json_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    if isinstance(x, google.appengine.ext.ndb.key.Key):
        return str(x)
    print 'The type is =>'
    print x
    raise TypeError("Unknown type")

def chargeRider(user, trip):    
    customer_id = user.customer_id
    amount = trip.rate_per_seat
    
    '''Create a Transaction'''
    transaction = Transaction()
    transaction.user_charged_key = user.key
    #transaction.driver_debited_key = driver.key
    transaction.status = 'initiated'
    transaction_key = transaction.put()
    
    '''Save Transaction to User model'''
    user.transaction_keys.append( transaction_key.urlsafe() )
    user.put()
    
    '''Charge the Rider'''
    success, resp = Payment().chargeRider(amount=amount, customer_id=customer_id, transaction_key=transaction_key)
    
    return success, resp

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('lkjlkj')
        
class LoginHandler(webapp2.RequestHandler):
    def get(self):
        params = self.request.params
        email = params['email']
        password = params['password']
        
        #Set Header
        self.response.headers['Content-Type'] = 'application/json' 
        
        '''Retrieve user by email'''
        users = User.query( User.email == email ).fetch()
        if len( users ) > 0:
            for user in users:
                '''Hash the password'''
                salt = user.salt
                hashed_password = hashlib.sha512(password + salt).hexdigest()
                if user.hashed_password == hashed_password:
                    '''This is a matching password and user is authenticated'''
                    #Send Response
                    stripe_account_id = user.stripe_account_id
                    user_key = user.key.urlsafe()
                    user = user.to_dict()
                    user['user_key'] = user_key
                    user['stripe_account_id'] = stripe_account_id
                    obj = {'result': True,
                           'user' : user}
                    self.response.write(json.dumps(obj , default=json_handler) )
                else:
                    obj = {'result': False,
                           'error': 'Wrong Password'}
                    self.response.write(json.dumps(obj , default=json_handler) )
        else:
            obj = {'result': False,
                   'error': 'No matching Email'}
            self.response.write(json.dumps(obj , default=json_handler) )     
            
        
class SearchHandler(webapp2.RequestHandler):
    def post(self):
        q_str = self.request.get('q')
        
        #Search by username only
        users = User.query( User.user_name == q_str ).fetch()
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps([user.to_dict() for user in users], default=json_handler))
        
        
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
        #end_address_zip_code = params['trip[endAddress][zipCode]']
        
        '''Trip information'''
        time_chosen = params['trip[chosen_time]']
        trip_eta = params['trip[eta]']
        posted_by = params['trip[posted_by]']
        time_zone = params['time_zone']

        '''Driver Post Properties'''
        seats = None
        rate = None
        radius = None

        if posted_by == "driver":
            seats = int( params['trip[seats_available]'] )
            rate = int( params['trip[rate_per_seat]'] )
            radius = int( params['trip[radius]'] )
        
        '''Post information'''
        post_text = params['trip[post_text]']
        
        '''User information'''
        user_key = params['user_key']
        user = ndb.Key(urlsafe=user_key).get( use_cache=False, use_memcache=False )
        count = user.numberOfPost + 1
        user.numberOfPost = count
        user.put()
        
        #Create Start Location 
        start_location = Location(address1=start_address1, address2=start_address2, city=start_address_city, state=start_address_state)
        
        #Create End Location
        end_location = Location(address1=end_address1, address2=end_address2, city=end_address_city, state=end_address_state)
        
        #Create the Trip to be associated with the post
        trip_key = Trip.create_trip(start_location=start_location, 
                                    end_location=end_location, 
                                    posted_by=posted_by, 
                                    posted_by_key=user_key, 
                                    seats_available=seats, 
                                    rate_per_seat=rate, 
                                    radius=radius,
                                    eta = trip_eta,
                                    time_chosen=time_chosen)
        post_key = Post.create_post(user_key=user_key, text=post_text, trip_key=trip_key, time_zone=time_zone)
        
        #SEnd Response
        self.response.headers['Content-Type'] = 'application/json' 
        obj = {'post_key': post_key,
               'trip_key': trip_key}
        self.response.write(json.dumps(obj , default=json_handler) )
        
class FetchFeedHandler(webapp2.RequestHandler):
    def get(self):
        if ( self.request.get('user_key') == None or self.request.get('user_key') == None ):
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps([], default=json_handler))
        else:
            #return a fetch object with all posts and appropriate things needed for the app to populate
            feed = PostFetcher(user_key=str(self.request.get('user_key')))
            posts = feed.get_all_posts()
            for post in posts:
                print post
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps([post.to_dict() for post in posts], default=json_handler))
        
class FetchUserFeedHandler(webapp2.RequestHandler):
    def get(self):
        #return a fetch object with all posts and appropriate things needed for the app to populate
        user_key = str( self.request.get('user_key') )
        user = ndb.Key( urlsafe=user_key ).get( use_cache=False, use_memcache=False )

        
        feed = PostFetcher(user_key= user_key )
        posts = feed.get_all_user_posts()
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps([post.to_dict() for post in posts], default=json_handler))  
        
class UpdateUserHandler(webapp2.RequestHandler):
    def post(self):
        user_key = self.request.get('user_key')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        email = self.request.get('email')
        
        user = ndb.Key(urlsafe=user_key).get(  use_cache=False, use_memcache=False )
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.put()
        
        obj = {}
        obj['success'] = True
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write("Updated User")
    

class CreateUserTasksHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        print 'Params => ' + str(params)
        '''Create User'''
        first_name = params['user[first_name]']
        last_name = params['user[last_name]']
        email = params['user[email]']
        facebook_id = params['user[facebook_id]']
        profile_pic_url = params['user[profile_pic_url]']
        password = params['user[password]']
        not_token = params['user[notification_token]']
        

        '''Create a stripe account for this user'''
        new_stripe_user = Payment(first_name=first_name, last_name=last_name, email=email)
        stripe_customer_id = new_stripe_user.createCustomer()
        stripe_account_id = new_stripe_user.createUser()
        
        '''Hash The password'''
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        
        '''Check if this user already exist through facebook or email''' 
        '''TODO CHANGE FACEBOOK ID SO IT IS NOT '' SO IT CAN BE COMPARED'''
        users = []
        if facebook_id == '':
            '''This user signed up with their email.'''
            users = User.query( User.email == email ).fetch()
        else:
            '''This user signed up with facebook.'''
            users = User.query( User.facebook_id == facebook_id ).fetch()
        user_key = ''
        returned_user = None
        for user in users:
            print user
            returned_user = user
        if len( users ) == 0:
            '''Save User to the databases'''
            user_key = User.create_new_user(first_name=first_name, 
                                            last_name=last_name, 
                                            email=email, 
                                            profile_pic_url=profile_pic_url, 
                                            facebook_id=facebook_id,
                                            hashed_password=hashed_password,
                                            salt=salt,
                                            stripe_account_id=stripe_account_id,
                                            customer_id=stripe_customer_id,
                                            notification_token=not_token)
            user_key = user_key.urlsafe()
        else:
            user_key = returned_user.key.urlsafe()
        
        
        obj = {'user_key' : user_key,
               'stripe_account_id': stripe_account_id,
               'customer_id': stripe_customer_id}
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(obj , default=json_handler) )

        
class CommentPostTasksHandler(webapp2.RequestHandler):
    def post(self):
        user_key = str(self.request.get('user_key'))
        post_key = str(self.request.get('post_key'))
        comment_text = self.request.get('comment')
        urlsafe_comment_key = Comment(user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key), text=comment_text).put().urlsafe()
        comment = ndb.Key(urlsafe=urlsafe_comment_key).get()
        user_key_urlsafe = comment.user_key.urlsafe()
        post_key_urlsafe = comment.post_key.urlsafe()
        post = comment.post_key.get()
        created_at_final = DateManager(tz=post.time_zone, created_at=post.created_at).final_time
        comment = comment.to_dict()
        comment['user_key'] = user_key_urlsafe
        comment['post_key'] = post_key_urlsafe
        comment['comment_key'] = urlsafe_comment_key
        comment['created_at'] = created_at_final
        
        #Should be a response to the user that says, they have liked the post
        obj = {'comment': comment}
        self.response.write(json.dumps(obj , default=json_handler) )
        
class DeletePostHandler(webapp2.RequestHandler):
    def post(self):
        Post.delete_post(str(self.request.get('post_key')))
        obj = {}
        obj['success'] = True
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write( json.dumps(obj , default=json_handler) )
        
class DeleteAccountHandler(webapp2.RequestHandler):
    def post(self):
        User.delete_user(str(self.request.get('user_key')))
        obj = {}
        obj['success'] = True
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write( json.dumps(obj , default=json_handler) )

class DenyFriendTasksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/denyRequest',
            target='worker',
            params={'friend_key': str(self.request.get('friend_key')),
                    'user_key': str(self.request.get('user_key'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
        
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
        user_key = str(self.request.get('user_key') )
        friend_key = str(self.request.get('friend_key') )
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/requestFriend',
            target='worker',
            params={'user_key': user_key,
                    'friend_key': friend_key
                             })
        

        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class RemoveFriendTaksHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/removeFriend',
            target='worker',
            params={'user_key': str(self.request.get('user_key')),
                    'friend_key': str(self.request.get('friend_key'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        

class RemoveRequestHandler(webapp2.RequestHandler):
    def post(self):
        #Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/removeRequest',
            target='worker',
            params={'user_key': str(self.request.get('user_key')),
                    'friend_key': str(self.request.get('friend_key'))
                             })
        #Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
    
class CreateStripeUser(webapp2.RequestHandler):
    def post(self):
        user = Payment(email="adrianhumphrey374@gmail.com")
        pass
    
class DeleteStripeUser(webapp2.RequestHandler):
    def post(self):
        user = Payment(email="adrian@questornow.com")
        pass
    
class StripeTempKeyHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        customer_id = params['customer_id']
        api_version = params['api_version']
       
        stripe.api_key = config.stripe_api_key_secret
        key = stripe.EphemeralKey.create(customer=customer_id, api_version=api_version)
        
        #Return json key
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(key , default=json_handler) )

class NotificationTaskHandler(webapp2.RequestHandler):
    def post(self):
        # Add this task to add friend to list of friends
        task = taskqueue.add(
            url='/tasks/handleNotification',
            target='worker',
            params={'to_key': str(self.request.get('to_key')),
                    'from_key': str(self.request.get('from_key')),
                    'type' : str(self.request.get('type'))
                    })
        # Should be a response to the user that says, they have liked the post
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(
            'Task {} enqueued, ETA {}.'.format(task.name, task.eta))
        
class UpdateTokenHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params

        user_key = params['user_key']
        token = params['token']

        user = ndb.Key(urlsafe=user_key).get()
        user.notification_token = token
        user.put()

        obj = { 'status' : 'Token Updated'}
        self.response.status_int = 200
        self.response.write(json.dumps(obj, default=json_handler))
        
class GetTripHandler(webapp2.RequestHandler):
    def get(self):
        params = self.request.params
        trip_key = params['trip_key']
        trip = ndb.Key(urlsafe=trip_key).get( use_cache=False, use_memcache=False ).to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(trip, default=json_handler))
        
class ReserveSeatHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        user_key = params['user_key']
        post_key = params['post_key']
        user = ndb.Key(urlsafe=user_key).get(use_cache=False, use_memcache=False)
        post = ndb.Key(urlsafe=post_key).get(use_cache=False, use_memcache=False) #The post changes often
        trip = post.trip_key.get(use_cache=False, use_memcache=False)
        driver = ndb.Key(urlsafe=trip.posted_by_key).get()
        
        obj = {}
        #Check if this user has already requested this seat
        if user_key not in trip.requests and trip.seats_available > 0:
            
            #Add this request to the user sending the request, 4 max
            tripRequest = TripRequest()
            tripRequest.user_key = ndb.Key(urlsafe=user_key)
            tripRequest.status = "None"
            tripRequest_key = tripRequest.put()
            user.trip_requests.append( tripRequest_key.urlsafe() ) #expected string
            
            
            #Add this request to the drivers request
            trip.requests.append(user_key)
            trip.put()
            
            #Create notification and add it to the drivers list of notifications
            notification = Notification()
            notification.type = "seat_request"
            notification.from_user_key = user_key
            notification.to_user_key = trip.posted_by_key
            notification.trip_key = post.trip_key.urlsafe()
            
            
            #Send notification to the drivers phone to accept the request, he should also in the notifications
            fb_notification = FBNotification(type=notification.type, 
                                             to_user_key=notification.to_user_key,
                                             trip_key=post.trip_key,
                                             from_user_key=notification.from_user_key)
            
            resp = fb_notification.send()
            print 'notification response'
            print resp
            
            #Add notification to the user
            notification.message = fb_notification.createMessage()
            user.notifications.append( notification )
            
            #Decrement request left
            count = user.requests_left
            count = count - 1
            user.requests_left = count
            
            #Save user
            user.put()
            
            #Send the response
            obj['success'] = True
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(obj, default=json_handler))
        else:
            obj['success'] = False
            obj['error_message'] = 'ride already requested'
            
            #Tell the user that you have already requested this ride, we will let you know the drivers response
            if trip.seats_available == 0:
                obj['error_message'] == 'no seats available'
                
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(obj, default=json_handler))
        
class FetchNotificationsHandler(webapp2.RequestHandler):
    def get(self):
        params = self.request.params
        user_key = params['user_key']
        user = ndb.Key(urlsafe=user_key).get(use_cache=False, use_memcache=False)
        notifications = user.notifications
        return_notifications = []
        if not notifications:
            #the list is empty
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps([], default=json_handler))

        else:
            #The notification list is not empty
            for notif in notifications:
                key = notif.created_at
                user_key = ndb.Key(urlsafe=notif.from_user_key)
                user = user_key.get(use_cache=False, use_memcache=False)
                user = user.to_dict()
                notif = notif.to_dict()
                notif['user'] = User.user_for_app( user )
                notif['user']['user_key'] = user_key.urlsafe()
                notif['key'] = key
                return_notifications.append(notif)
            
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps([notification for notification in return_notifications], default=json_handler))
            
class AcceptRiderHanlder(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        user_key = params['user_key']
        rider_key = params['rider_key']
        trip_key = params['trip_key']
        
        #Get users
        user = ndb.Key(urlsafe=user_key).get(use_cache=False, use_memcache=False)
        rider = ndb.Key(urlsafe=rider_key).get(use_cache=False, use_memcache=False)
        trip = ndb.Key(urlsafe=trip_key).get()

        # Charge the rider only if they have not been charged for the ride
        if rider_key not in trip.passenger_keys:
            success, resp = chargeRider(user=rider, trip=trip) #Only do the following if the charge was successful
            if success :
            
                # Add this user to the array of users riding on this trip
                trip.passenger_keys.append( rider_key )
                
                # Decrement the seats available
                count = trip.seats_available
                count = count + 1
                trip.seats_available = count 
                
                # Reset the riders number of available request
                rider.request_left = 4
                
                # Remove the riders key from the notification array from the driver
                if user_key in trip.requests:
                    trip.requests.remove( user_key )
    
                
                #On success notify the rider that the driver has accepted the rider and you have been charged and reciept sent to your email.
                fb_notification = FBNotification(type='driver_accepted_reservation', 
                                                     to_user_key=rider_key,
                                                     trip_key=ndb.Key(urlsafe=trip_key),
                                                     from_user_key=user_key)
                fb_notification.send()
                
                #Save trip, user, rider, notification
                user.put()
                rider.put()
                trip.put()
                
                obj = {}
                obj['resp'] = resp
                obj['success'] = True
                self.response.headers['Content-Type'] = 'application/json'  
                self.response.out.write(json.dumps(obj, default=json_handler))
            else:
                obj = {}
                obj['resp'] = resp
                obj['success'] = True
                self.response.headers['Content-Type'] = 'application/json'  
                self.response.out.write(json.dumps(obj, default=json_handler))
        else:
            obj = {}
            obj['resp'] = 'User Already in the ride, do not charge'
            obj['success'] = False
            self.response.headers['Content-Type'] = 'application/json'  
            self.response.out.write(json.dumps(obj, default=json_handler))   
            
class DenyRiderHandler(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        user_key = params['user_key']
        rider_key = params['rider_key']
        trip_key = params['trip_key']
        
        #Get users
        user = ndb.Key(urlsafe=user_key).get(use_cache=False, use_memcache=False)
        rider = ndb.Key(urlsafe=rider_key).get(use_cache=False, use_memcache=False)
        trip = ndb.Key(urlsafe=trip_key).get()
        
        #Since the driver has denied the riders, request, just send them the notification and remove their key from the trips notifications
        notification = FBNotification(type="driver_denied_reservation",
                                      to_user_key=rider_key,
                                      trip_key=ndb.Key(urlsafe=trip_key),
                                      from_user_key=user_key)
        notification.send()
        
        #remove the users key from the trips request
        if rider_key in trip.requests:
            trip.requests.remove( rider_key )
            
        obj = {}
        obj['success'] = True
        self.response.headers['Content-Type'] = 'application/json'  
        self.response.out.write(json.dumps(obj, default=json_handler))  
        
class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        INDEX_HTML = open('privacy.html').read()
        self.response.out.write(INDEX_HTML)

class TermsHandler(webapp2.RequestHandler):
    def get(self):
        INDEX_HTML = open('terms.html').read()
        self.response.out.write(INDEX_HTML)
        

app = webapp2.WSGIApplication([
    ('/api/', MainHandler),
    ('/api/login', LoginHandler),
    ('/api/search', SearchHandler),
    ('/api/likePost', LikePostTaskHandler),
    ('/api/getTrip', GetTripHandler),
    ('/api/reserveSeat', ReserveSeatHandler),
    ('/api/unlikePost', UnLikePostTaskHandler),
    ('/api/acceptRider', AcceptRiderHanlder),
    ('/api/denyRider', DenyRiderHandler),
    ('/api/fetchNotifications', FetchNotificationsHandler),
    ('/api/commentPost', CommentPostTasksHandler),
    ('/api/createPost', CreateMediaPostTaskHandler),
    ('/api/fetchFeed', FetchFeedHandler),
    ('/api/fetchUserFeed', FetchUserFeedHandler),
    ('/api/handleNotification', NotificationTaskHandler),
    ('/api/createUser', CreateUserTasksHandler),
    ('/api/updateNotificationToken', UpdateTokenHandler),
    ('/api/ephemeral_keys', StripeTempKeyHandler),
    ('/api/updateUser', UpdateUserHandler),
    ('/api/deletePost', DeletePostHandler),
    ('/api/deleteAccount', DeleteAccountHandler),
    ('/api/createStripeUser', CreateStripeUser),
    ('/api/addFriend', AddFriendTasksHandler),
    ('/api/denyFriend', DenyFriendTasksHandler),
    ('/api/requestFriend', RequestFriendTaksHandler),
    ('/api/removeFriend', RemoveFriendTaksHandler),
    ('/api/removeRequest', RemoveRequestHandler),
    ('/api/privacy-policy', PrivacyHandler),
    ('/api/terms-of-service', TermsHandler)
   
], debug=True)

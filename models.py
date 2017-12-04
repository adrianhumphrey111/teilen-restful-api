from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.ext.ndb import msgprop
from google.appengine.ext.db import IntegerProperty
from dateManager import DateManager
from __builtin__ import classmethod
from datetime import datetime


class Location(ndb.Model):
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    country = ndb.StringProperty()
    address1 = ndb.StringProperty()
    address2 = ndb.StringProperty()
    
class Car(ndb.Model):
    model = ndb.StringProperty()
    year = ndb.IntegerProperty()
    make = ndb.StringProperty()
    miles_per_gallon = ndb.FloatProperty()
    num_of_trips = ndb.IntegerProperty()
    num_of_seats = ndb.IntegerProperty()
    
class UserStatus(ndb.Model):
    NOT_LOOKING = "Currently Not Looking."
    DRIVING = "Currently Driving To Destination"
    RIDING = "Currently On The Way To Destination"
    LOOKING_RIDE = "Currently Looking For a Ride"
    LOOKING_PASSENGERS = "Currently Looking For Passengers."

class TripStatus(ndb.Model):
    IN_PROGRESS = "Trip Currently In Progress"
    LOOKING = "Looking For Passengers"
    BOOKED = "Trip Not Started But Full"
    COMPLETED = "Trip Has Been Completed"
    
class Trip(ndb.Expando):
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty()
    start_location = ndb.StructuredProperty( Location )
    end_location = ndb.StructuredProperty( Location )
    #driver_key = ndb.IntegerProperty() is now posted_by
    passenger_keys = ndb.StringProperty(repeated=True)
    wait_list = ndb.StringProperty(repeated=True)
    seats_available = ndb.IntegerProperty()
    requests = ndb.StringProperty(repeated=True) #List of strings of users that have submitted a request
    status = ndb.StructuredProperty(TripStatus)
    radius = ndb.IntegerProperty()
    chosen_time = ndb.StringProperty() #Either arrival or departure
    eta = ndb.DateTimeProperty()
    rate_per_seat = ndb.IntegerProperty() #in USD
    posted_by = ndb.StringProperty() #driver or rider
    posted_by_key = ndb.StringProperty() #the key for the user that actually posted the ride

    @classmethod
    def create_trip(cls, start_location=None, end_location=None, posted_by="", posted_by_key="", seats_available=0, rate_per_seat=0, radius=0, eta="", time_chosen=""):
        trip = Trip()
        trip.posted_by_key = posted_by_key
        trip.start_location = start_location
        trip.end_location = end_location
        trip.posted_by = posted_by
        trip.tripStatus = TripStatus.LOOKING
        trip.seats_available = seats_available
        trip.rate_per_seat = rate_per_seat
        trip.requests = []
        trip.radius = radius
        '''Convert to date'''
        trip.eta = datetime.strptime(eta, "%Y-%m-%d %H:%M:%S")
        trip.time_chosen = time_chosen
        trip_key = trip.put()

        return trip_key
    
    
class Notification(ndb.Model):
    type = ndb.StringProperty()
    message = ndb.StringProperty()
    from_user_key = ndb.StringProperty()
    to_user_key = ndb.StringProperty()
    trip_key = ndb.StringProperty()
    status = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    
    

class User(ndb.Expando):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    full_name = ndb.StringProperty()
    email = ndb.StringProperty()
    user_name = ndb.StringProperty()
    school = ndb.StringProperty()
    salt = ndb.StringProperty()
    hashed_password = ndb.StringProperty()
    requests_left = ndb.IntegerProperty()
    '''This account id is for drivers to be paid out'''
    stripe_account_id = ndb.StringProperty()
    customer_id = ndb.StringProperty()
    notification_token = ndb.StringProperty()
    location = ndb.StructuredProperty(Location)
    facebook_id = ndb.StringProperty()
    car = ndb.StructuredProperty(Car)
    status = ndb.StructuredProperty(UserStatus)
    profile_pic_url = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    current_trip = ndb.StructuredProperty(Trip)
    planned_trip_ids = ndb.IntegerProperty(repeated=True)
    transaction_keys = ndb.StringProperty(repeated=True)
    completed_trip_ids = ndb.IntegerProperty(repeated=True)
    trip_requests = ndb.StringProperty(repeated=True) #list of keys for requests
    numberOfCompletedTrips = ndb.IntegerProperty()
    numberOfPost = ndb.IntegerProperty()
    numberOfFriends = ndb.IntegerProperty()
    rating = ndb.FloatProperty()
    post_ids = ndb.IntegerProperty(repeated=True) #one to many relationship 
    friend_ids = ndb.IntegerProperty(repeated=True)
    friend_request_ids = ndb.IntegerProperty(repeated=True)
    requested_friend_ids = ndb.IntegerProperty(repeated=True)
    notifications = ndb.StructuredProperty(Notification, repeated=True)
    
    @classmethod
    def create_new_user(self, first_name, last_name, email, profile_pic_url, facebook_id, hashed_password, salt, stripe_account_id, customer_id, notification_token):
        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.full_name = first_name + ' ' + last_name
        user.email = email
        user.facebook_id = facebook_id
        user.profile_pic_url = profile_pic_url
        user.hashed_password = hashed_password
        user.notification_token = notification_token
        user.stripe_account_id = stripe_account_id
        user.customer_id=customer_id
        user.salt = salt
        user.friend_ids = []
        user.post_ids = []
        user.reviews = []
        user.transaction_keys = []
        user.requests_left = 4
        user.rating = 5
        user.numberOfPost = 0
        user.numberOfFriends = 0
        user.numberOfCompletedTrips = 0
        user.completed_trip_ids = []
        user.planned_trip_ids = []
        user.friend_request_ids = []
        user.requested_friend_ids = []
        user.current_trip_id = None
        return user.put()
    
    @classmethod
    def updateUser(self, **kwargs):
        print str( kwargs )
        '''for key in kwargs:
            print key
            print kwargs[key]
            #update any value that is in kwargs
            setattr(user, key, kwargs[key])
        return user.put()'''
    
    def is_friend(self, friend_key):
        status = None
        if ( friend_key.id() in self.friend_ids ):
            status = "friend"
        elif ( friend_key.id() in self.requested_friend_ids ):
            status = "requested"
        else:
            status = "notFriend"
        return status
    
    @classmethod
    def retrieve_all_post(self, key):
        posts = []
        print key
        for post in Post.query(Post.user_key == key).order(-Post.created_at).fetch(use_cache=False, use_memcache=False):
            post_key = post.key.urlsafe()
            user_key = post.user_key.urlsafe()
            user = post.user_key.get( use_cache=False, use_memcache=False )
            like_count = Post.get_like_count( post_key )
            user_liked = Post.check_user_liked( user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key) )
            comment_count = Post.get_comment_count( post_key )
            created_at_final = DateManager(tz=post.time_zone, created_at=post.created_at).final_time
            trip = None
            if post.trip_key.get() != None:
                trip = post.trip_key.get(use_cache=False, use_memcache=False).to_dict()
                print trip
            else:
                trip = ""
                '''
            post=post.to_dict()
            post.pop('user_key', None)
            post['user'] = self.user_for_app( key.get().to_dict() )
            post['post_key'] = post_key
            post['user']['user_key'] = user_key
            post['like_count'] = like_count
            post['comment_count'] = comment_count
            post['user_liked'] = user_liked
            post['created_at'] = created_at_final
            post['trip'] = trip'''
            post.user = self.user_for_app( key.get().to_dict() )
            post.user.user_key = user_key
            post.post_key = post_key
            #post.user_key = user_key
            post.like_count = like_count
            post.comment_count = comment_count
            post.user_liked = user_liked
            post.time_stamp = created_at_final
            post.testthefuckisgoingon = 124243
            post.trip = trip
            posts.append( post )
        return posts

    @classmethod
    def add_friend(cls, user_url_key, friend_url_key):
        user, user_key, friend, friend_key = cls.user_and_friend(user_url_key=user_url_key, friend_url_key=friend_url_key)
        if user_key.id() not in friend.friend_ids:
            friend.friend_ids.append( user_key.id() )
            count = friend.numberOfFriends + 1
            friend.numberOfFriends = count
            if friend.key.id() in user.friend_request_ids:
                user.friend_request_ids.remove( friend.key.id() )
                friend.requested_friend_ids.remove( user.key.id() )
        if friend_key.id() not in user.friend_ids:
            user.friend_ids.append( friend_key.id() )
            count = user.numberOfFriends + 1
            user.numberOfFriends = count
        
        friend.put()
        user.put()
        
    @classmethod
    def deny_request(cls, user_url_key, friend_url_key):
        user, user_key, friend, friend_key = cls.user_and_friend(user_url_key=user_url_key, friend_url_key=friend_url_key)
        if friend.key.id() in user.friend_request_ids:
            user.friend_request_ids.remove( friend.key.id() )
            friend.requested_friend_ids.remove( user.key.id() )
        friend.put()
        user.put()
    
    @classmethod
    def request_friend(cls, user_url_key, friend_url_key):
        user, user_key, friend, friend_key = cls.user_and_friend(user_url_key=user_url_key, friend_url_key=friend_url_key)
        if user_key.id() not in friend.requested_friend_ids:
            friend.requested_friend_ids.append( user_key.id() )
        if friend_key.id() not in user.friend_request_ids:
            user.friend_request_ids.append( friend_key.id() )
        friend.put()
        user.put()
    
    @classmethod
    def remove_friend(cls, user_url_key, friend_url_key):
        user, user_key, friend, friend_key = cls.user_and_friend(user_url_key=user_url_key, friend_url_key=friend_url_key)
        if friend_key.id() in user.friend_ids:
            user.friend_ids.remove( friend_key.id())
        if user_key.id() in friend.friend_ids:
            friend.friend_ids.remove( user_key.id() )
        friend.put()
        user.put()
        
    @classmethod
    def user_and_friend(cls, user_url_key, friend_url_key):
        user_key = ndb.Key(urlsafe=user_url_key)
        user = user_key.get()
        friend_key = ndb.Key(urlsafe=friend_url_key)
        friend = friend_key.get()
        return user, user_key, friend, friend_key

    
    @classmethod
    def remove_friend_request(cls, user_url_key, friend_url_key):
        user_key = ndb.Key(urlsafe=user_url_key)
        user = user_key.get()
        friend_key = ndb.Key(urlsafe=friend_url_key)
        friend = friend_key.get()
        if friend_key.id() in user.friend_ids:
            user.friend_ids.remove( friend_key.id())
        if user_key.id() in friend.friend_ids:
            friend.friend_ids.remove( user_key.id() )
        friend.put()
        user.put()
    
    @classmethod
    def user_for_app(cls, user):
        #method will strip everything from user object that does not need to be returned
        user.pop('email', None)
        user.pop('billing_info', None)
        user.pop('post_ids', None)
        user.pop('stripe_account_id', None)
        user.pop('friend_ids', None)
        user.pop('friend_request_ids', None)
        user.pop('requested_friend_ids', None)
        user.pop('notifications', None)
        user.pop('hashed_password', None)
        user.pop('transaction_keys', None)
        user.pop('salt', None)
        return user
    
    @classmethod
    def delete_user(cls, user_key):
        key = ndb.Key(urlsafe=user_key)
        key.delete()
    
        
class Post(ndb.Expando):
    user_key = ndb.KeyProperty(kind=User)
    user = ndb.StructuredProperty(User)
    text = ndb.StringProperty()
    type = ndb.StringProperty()
    trip_key = ndb.KeyProperty(kind=Trip)
    user_liked = ndb.BooleanProperty()
    time_zone = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True) 
    
    
    @classmethod
    def create_post(cls, user_key, text, trip_key, time_zone):
        user_key = ndb.Key(urlsafe=user_key)
        post = Post(user_key=user_key, text=text)
        post.trip_key = trip_key
        post.time_zone = time_zone
        post.likeCount = 0
        post.commentCount = 0
        post_key = post.put()
        
        return post_key
    
    @classmethod
    def check_user_liked(cls, user_key, post_key):
        if len( Like.query(ndb.AND(Like.post_key == post_key, Like.user_key == user_key)).fetch() ) > 0:
            return True
        else:
            return False
    
    @classmethod
    def get_like_count(cls, post_key):
        #Query all likes associated with post
        return len( Like.query(Like.post_key == ndb.Key(urlsafe=post_key) ).fetch() )
    
    @classmethod
    def get_comment_count(cls, post_key):
        #Query all likes associated with post
        return len( Comment.query(Comment.post_key == ndb.Key(urlsafe=post_key) ).fetch() )

    @classmethod
    def delete_post(cls, post_key):
        key = ndb.Key(urlsafe=post_key)
        key.delete()
        
        
class Comment(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)
    text = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def getCommentsForPost(cls, post_key):
        post = post_key.get()
        tz = post.time_zone
        comments = []
        for comment in cls.query(cls.post_key == post_key ).order(cls.created_at).fetch():
            post_key_urlsafe = comment.post_key.urlsafe()
            user_key_urlsafe = comment.user_key.urlsafe()
            created_at_final = DateManager(tz=tz, created_at=comment.created_at).final_time
            comment = comment.to_dict()
            comment['user'] = User.user_for_app( post.user_key.get().to_dict() )
            comment['user']['user_key'] = post.user_key.urlsafe()
            comment['post_key'] = post_key_urlsafe
            comment['user_key'] = user_key_urlsafe
            comment['created_at'] = created_at_final
            comments.append( comment  )
        return comments
    
    @classmethod
    def delete_comment(cls, comment_id):
        key = ndb.Key('Comment', comment_id)
        key.delete()
    
class Like(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)
    comment_key = ndb.KeyProperty(kind=Comment)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def delete_like(cls, post_key, user_key):
        post_key = ndb.Key(urlsafe=post_key)
        user_key = ndb.Key(urlsafe=user_key)
        for like in Like.query(ndb.AND(Like.post_key == post_key, Like.user_key == user_key)).fetch():
            like.key.delete()
    
    
class Rating(ndb.Model):
    rating = ndb.IntegerProperty()

class Review(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    text = ndb.StringProperty()
    rating = ndb.StructuredProperty(Rating)
    
class Transaction(ndb.Model):
    user_charged_key = ndb.KeyProperty(kind=User)
    driver_debited_key = ndb.KeyProperty(kind=User)
    trip_key = ndb.KeyProperty(kind=Trip)
    time_initiated = ndb.DateTimeProperty(auto_now_add=True)
    time_completed = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    '''In Cents'''
    amount_charged = ndb.IntegerProperty() 
        

class TripType(ndb.Model):
    LONG = 'Long'
    MEDIUM = 'Medium'
    SHORT = 'Short'

    
class TripRequest(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    status = ndb.StringProperty()
    
    
    
    
    
    


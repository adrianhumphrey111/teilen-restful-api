from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.ext.ndb import msgprop
from google.appengine.ext.db import IntegerProperty


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
    
class Trip(ndb.Model):
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty()
    start_location = ndb.StructuredProperty( Location )
    end_location = ndb.StructuredProperty( Location )
    driver_key = ndb.IntegerProperty()
    passenger_ids = ndb.IntegerProperty(repeated=True)
    seats = ndb.IntegerProperty()
    seats_avialble = ndb.IntegerProperty()
    status = ndb.StructuredProperty(TripStatus)
    rate_per_seat = ndb.IntegerProperty() #in USD

class User(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    school = ndb.StringProperty()
    salt = ndb.StringProperty()
    hashed_password = ndb.StringProperty()
    stripe_account_id = ndb.StringProperty()
    customer_id = ndb.StringProperty()
    location = ndb.StructuredProperty(Location)
    facebook_id = ndb.StringProperty()
    car = ndb.StructuredProperty(Car)
    status = ndb.StructuredProperty(UserStatus)
    billing_info = ndb.StringProperty()
    profile_pic_url = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    current_trip_id = ndb.StructuredProperty(Trip)
    planned_trip_ids = ndb.IntegerProperty(repeated=True)
    completed_trip_ids = ndb.IntegerProperty(repeated=True)
    numberOfCompletedTrips = ndb.IntegerProperty()
    rating = ndb.FloatProperty()
    post_ids = ndb.IntegerProperty(repeated=True) #one to many relationship 
    friend_ids = ndb.IntegerProperty(repeated=True)
    friend_request_ids = ndb.IntegerProperty(repeated=True)
    requested_friend_ids = ndb.IntegerProperty(repeated=True)
    
    @classmethod
    def create_new_user(self, first_name, last_name, email, profile_pic_url, facebook_id, hashed_password, salt, stripe_account_id, customer_id):
        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.facebook_id = facebook_id
        user.profile_pic_url = profile_pic_url
        user.hashed_password = hashed_password
        user.stripe_account_id = stripe_account_id
        user.customer_id=customer_id
        user.salt = salt
        user.friend_ids = []
        user.post_ids = []
        user.reviews = []
        user.rating = 5
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
    
    @classmethod
    def retrieve_all_post(self, key):
        posts = []
        print key
        for post in Post.query(Post.user_key == key).fetch():
            post_key = post.key.urlsafe()
            user_key = post.user_key.urlsafe()
            like_count = Post.get_like_count( post_key )
            user_liked = Post.check_user_liked( user_key=ndb.Key(urlsafe=user_key), post_key=ndb.Key(urlsafe=post_key) )
            comment_count = Post.get_comment_count( post_key )
            trip = None
            if post.trip_key.get() != None:
                trip = post.trip_key.get().to_dict()
            else:
                trip = ""
            post=post.to_dict()
            post.pop('user_key', None)
            post['user'] = self.user_for_app( key.get().to_dict() )
            post['post_key'] = post_key
            post['user']['user_key'] = user_key
            post['like_count'] = like_count
            post['comment_count'] = comment_count
            post['user_liked'] = user_liked
            post['trip'] = trip
            posts.append( post )
        return posts

    @classmethod
    def add_friend(cls, user_url_key, friend_url_key):
        user, user_key, friend, friend_key = cls.user_and_friend(user_url_key=user_url_key, friend_url_key=friend_url_key)
        if user_key.id() not in friend.friend_ids:
            friend.friend_ids.append( user_key.id() )
        if friend_key.id() not in user.friend_ids:
            user.friend_ids.append( friend_key.id() )
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
        return user
    
        
class Post(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    user = ndb.StructuredProperty(User)
    text = ndb.StringProperty()
    trip_key = ndb.KeyProperty(kind=Trip)
    likeCount = ndb.IntegerProperty()
    commentCount = ndb.IntegerProperty()
    user_liked = ndb.BooleanProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True) 
    
    @classmethod
    def create_post(cls, user_key, text, trip_key):
        user_key = ndb.Key(urlsafe=user_key)
        post = Post(user_key=user_key, text=text)
        post.trip_key = trip_key
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
        

class TripType(ndb.Model):
    LONG = 'Long'
    MEDIUM = 'Medium'
    SHORT = 'Short'



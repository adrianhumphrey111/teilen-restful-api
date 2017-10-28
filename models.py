from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.ext.ndb import msgprop


class Location(ndb.Model):
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    country = ndb.StringProperty()
    
class Car(ndb.Model):
    model = ndb.StringProperty()
    year = ndb.IntegerProperty()
    make = ndb.StringProperty()
    miles_per_gallon = ndb.IntegerProperty()
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
    start_location = ndb.StringProperty()
    end_location = ndb.StringProperty()
    driver_id = ndb.IntegerProperty()
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
    location = ndb.StructuredProperty(Location)
    car = ndb.StructuredProperty(Car)
    status = ndb.StructuredProperty(UserStatus)
    billing_info = ndb.StringProperty()
    profile_pic_url = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    current_trip_id = ndb.StructuredProperty(Trip)
    planned_trip_ids = ndb.IntegerProperty(repeated=True)
    completed_trip_ids = ndb.IntegerProperty(repeated=True)
    rating = ndb.FloatProperty()
    post_ids = ndb.IntegerProperty(repeated=True) #one to many relationship 
    friend_ids = ndb.IntegerProperty(repeated=True)
    friend_request_ids = ndb.IntegerProperty(repeated=True)
    requested_friend_ids = ndb.IntegerProperty(repeated=True)
    
    @classmethod
    def create_new_user(self, **kwargs):
        user = User()
        for key in kwargs:
            #update any value that is in kwargs
            setattr(user, key, kwargs[key])
        user.friend_ids = []
        user.post_ids = []
        user.reviews = []
        user.rating = 5
        user.completed_trip_ids = []
        user.planned_trip_ids = []
        user.friend_request_ids = []
        user.requested_friend_ids = []
        user.current_trip_id = None
        
        return user.put()
    
    @classmethod
    def updateUser(self, key, **kwargs):
        user = key.get()
        for key in kwargs:
            #update any value that is in kwargs
            setattr(user, key, kwargs[key])
        return user.put()
    
    @classmethod
    def retrieve_all_post(self, key):
        posts = []
        for post in Post.query(Post.user_key == key).fetch():
            post_key = post.key.urlsafe()
            user_id = post.user_key.id()
            post=post.to_dict()
            post.pop('user_key', None)
            post['user'] = self.user_for_app( key.get().to_dict() )
            post['post_key'] = post_key
            post['user']['user_id'] = user_id
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
        user.pop('friend_ids', None)
        user.pop('friend_request_ids', None)
        user.pop('requested_friend_ids', None)
        return user
    
        
class Post(ndb.Model):
    user_key = ndb.KeyProperty(kind=User)
    user = ndb.StructuredProperty(User)
    text = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True) 
    
    @classmethod
    def create_post(cls, user_key, text):
        user_key = ndb.Key(urlsafe=user_key)
        post = Post(user_key=user_key, text=text).put()
        return post

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



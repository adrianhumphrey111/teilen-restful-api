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


class Like(ndb.Model):
    user_id = ndb.IntegerProperty()
    post_id = ndb.IntegerProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)

class Comment(ndb.Model):
    user_id = ndb.IntegerProperty()
    post_id = ndb.IntegerProperty()
    text = ndb.StringProperty()
    likes = ndb.StructuredProperty(Like, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    

class Post(ndb.Model):
    user_id = ndb.IntegerProperty()
    text = ndb.StringProperty()
    likes = ndb.StructuredProperty(Like, repeated=True)
    comment_ids = ndb.IntegerProperty(repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True) 
    
    @classmethod
    def create_post(cls, user_id, text, likes=[], comment_ids=[]):
        post = Post(user_id=user_id, text=text, likes=likes, comment_ids=comment_ids)
        user = ndb.Key('User', user_id).get()
        key = post.put()
        user.post_ids.append( key.id() )
        return user.put()
    
    @classmethod
    def add_like(cls, like):
        post = Post.get_by_id(like.post_id)
        post.likes.append(like)
        like.put()
        return post.put()
    
    @classmethod
    def add_comment(cls, comment):
        post = Post.get_by_id(comment.post_id)
        key = comment.put()
        post.comment_ids.append( key.id() )
        return post.put()
    
    @classmethod
    def delete_post(cls, post_id):
        key = ndb.Key('Post', post_id)
        key.delete()
    
class Rating(ndb.Model):
    rating = ndb.IntegerProperty()

class Review(ndb.Model):
    user_id = ndb.IntegerProperty()
    text = ndb.StringProperty()
    rating = ndb.StructuredProperty(Rating)
    
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
    reviews = ndb.StructuredProperty(Review, repeated=True)
    post_ids = ndb.IntegerProperty(repeated=True)
    friend_ids = ndb.IntegerProperty(repeated=True)
    friend_request_ids = ndb.IntegerProperty()
    requested_friend_ids = ndb.IntegerProperty()
    
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
        user = key.get()
        posts = []
        if hasattr(user, 'post_ids'): #the user has atleast one friend
            for post_id in user.post_ids:
                posts.append( ndb.Key( 'Post', post_id).get().to_dict() )
        return posts
    
    @classmethod
    def add_friend(cls, key, friend_id):
        user = key.get()
        user.friend_ids.append( friend_id )
        return user.put()
    
    @classmethod
    def request_friend(cls, key, friend_key):
        user = key.get()
        friend = friend_key.get()
        user.requested_friend_ids.append( friend_key.id() )
        friend.friend_request_ids.append( key.id() )
        friend.put()
        return user.put()
        
        

class TripType(ndb.Model):
    LONG = 'Long'
    MEDIUM = 'Medium'
    SHORT = 'Short'



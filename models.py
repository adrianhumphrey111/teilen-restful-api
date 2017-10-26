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
    
class UserStatus(messages.Enum):
    NOT_LOOKING = "Currently Not Looking."
    DRIVING = "Currently Driving To Destination"
    RIDING = "Currently On The Way To Destination"
    LOOKING_RIDE = "Currently Looking For a Ride"
    LOOKING_PASSENGERS = "Currently Looking For Passengers."

class TripStatus(messages.Enum):
    IN_PROGRESS = "Trip Currently In Progress"
    LOOKING = "Looking For Passengers"
    BOOKED = "Trip Not Started But Full"
    COMPLETED = "Trip Has Been Completed"


class Like(ndb.Model):
    user_id = ndb.IntegerProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)

class Comment(ndb.Model):
    user_id = ndb.IntegerProperty()
    text = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    likes = ndb.StructuredProperty(Like, repeated=True)

class Post(ndb.Model):
    user_id = ndb.IntegerProperty()
    text = ndb.StringProperty()
    likes = ndb.StructuredProperty(Like, repeated=True)
    comments = ndb.StructuredProperty(Comment, repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True) 
    
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
    status = msgprop.EnumProperty(TripStatus, required=True)
    rate_per_seat = ndb.IntegerProperty() #in USD

class User(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    emai = ndb.StringProperty()
    school = ndb.StringProperty()
    location = ndb.StructuredProperty(Location)
    car = ndb.StructuredProperty(Car)
    status = msgprop.EnumProperty(UserStatus, required=True)
    billing_info = ndb.StringProperty()
    profile_pic_url = ndb.StringProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    current_trip = ndb.StructuredProperty(Trip)
    planned_trips = ndb.StructuredProperty(Trip, repeated=True)
    completed_trips = ndb.StructuredProperty(Trip, repeated=True)
    rating = ndb.FloatProperty()
    reviews = ndb.StructuredProperty(Review, repeated=True)
    posts = ndb.StructuredProperty(Post, repeated=True)

class TripType(messages.Enum):
    LONG = 'Long'
    MEDIUM = 'Medium'
    SHORT = 'Short'



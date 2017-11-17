from google.appengine.ext import ndb
from models import User
import config

# Send to single device.
from pyfcm import FCMNotification

push_service = FCMNotification(api_key=config.fire_base_api_key)

class Notification:

    def __init__(self, type, to_user_key, from_user_key, data=False, multiple=False):
        self.type = type
        self.data = data
        self.multiple = multiple
        self.to_user_key = to_user_key
        self.from_userLey = from_user_key
        self.to_user = None
        self.from_user = None
        self.to_token = ""
        self.from_token = ""

        #Message
        self.messageTitle = "Tielen Ride Share"
        # Create the message to be sent to the user
        self.messageBody = self.createMessage()

        #Grab Users from databae
        self.grabUsers()

    def grabUsers(self):

        #From User
        self.from_user = ndb.Key(urlsafe=self.from_user_key).get()
        self.from_token = self.from_user.notification_token

        #To User
        self.to_user = ndb.Key(urlsafe=self.to_user_key).get()
        self.to_token = self.to_user.notification_token


    def createMessage(self):
        if self.data:
            #This is a notification that is sent to the user that contains data
            pass
        else:
            #This is a regualr notification, dictionary for the messages
            return {
                'friend_request': self.from_user.first_name + " has sent you a friend request.",
                'group_request': self.from_user.first_name + " has requested to be apart of your group.", #All notifications should take the user to the notification tab
                'friend_request_approved': self.from_user.first_name + " has approved your friend request.",
                'group_request_approved': self.from_user.first_name + " has approved your group request.",
                'like': self.from_user.first_name + " has liked your post",
                'comment': self.from_user.first_name + " has commented on your post.",
                'seat_request': self.from_user.first_name + " has requested to reserve a seat for your current trip.",
                'canceled_seat_request': self.from_user.first_name + " has canceled their request to reserve a seat on your current trip.",
                'driver_canceled': self.from_user.first_name + " has canceled the trip you have reserved to be apart of.",
                'driver_accepted_reservation': self.from_user.first_name + " has accepted you reservation request.",
                'rider_joined': self.from_user.first_name + " has joined the ride with you.",
                'rider_canceled': self.from_user.first_name + " has canceled and is no longer riding with you.",
                'driver_started_trip': self.from_user.first_name + " has started the trip and is on the way.",
                'driver_is_3_away': self.from_user.first_name + " is 3 minutes away. Please be ready to go!",
                'new_message': self.from_user.first_name + " has sent you a new message."
            }.get(self.type, "You have a new notification.")


    #Send the notification to the users phone single device
    def send(self):
        if self.multiple:
            return None
        else:
            return push_service.notify_single_device(registration_id=self.to_token,
                                                     message_title=self.messageTitle,
                                                     message_body=self.messageBody)



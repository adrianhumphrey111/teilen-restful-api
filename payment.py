'''
Created on Nov 14, 2017

@author: adrianhumphrey
'''
import config
import os
import stripe
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    stripe.verify_ssl_certs = False
import time

class Payment:
    
    def __init__(self, first_name, last_name, email):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
    
    def createCustomer(self):
        stripe.api_key = config.stripe_api_key_secret
        resp = stripe.Customer.create(email=self.email)
        
        customer_id = resp["id"]
        return customer_id
        
    def createUser(self):
        stripe.api_key = config.stripe_api_key_secret
        resp = stripe.Account.create(
                              type="custom",
                              country="US",
                              email=self.email
                              )
        
        #Grab id from the response
        acc_id = resp["id"]
        
        #Get the response of this call
        account = stripe.Account.retrieve(acc_id)
        account.payout_statement_descriptor = "Teilen Ride Share"
        
        #legal entity which is a dictionary
        account.legal_entity.first_name = self.first_name
        account.legal_entity.last_name = self.last_name
        account.legal_entity.type = 'individual'
        
        #Keep this for now until You figure out how to get this working
        account.tos_acceptance.user_agent ="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        account.tos_acceptance.ip = "70.169.190.10"
        account.tos_acceptance.date = int( time.time() )
        
        account.save()
        
        return acc_id
    
    def addCard(self):
        stripe.api_key = config.stripe_api_key_secret
        acc_id = "acct_1BOJFkA6DKpcTIJK"
         #Get the response of this call
        account = stripe.Account.retrieve(acc_id)
        token = self.cardToken()
        account.external_accounts.create(external_account={token.id})
    
    def cardToken(self):
        stripe.api_key = config.stripe_api_key_publish
        token = stripe.Token.create(
                        card={
                            "number": '4232230106071918',
                            "exp_month": 10,
                            "exp_year": 2021,
                            "cvc": '472'
                            }
                                    )
        print token
        print token.id
        return token
    
    def updateUser(self):
        '''
        account.legal_entity.dob.day = 4
        account.legal_entity.dob.month = 5
        account.legal_entity.dob.year = 1995
        account.legal_entity.ssn_last_4 = "9559"
        
        #Set the address of for the user
        account.legal_entity.address.line1 = "6503 Del Playa Dr"
        account.legal_entity.address.city = "Goleta"
        account.legal_entity.address.state = "CA"
        account.legal_entity.address.postal_code = "93117"
        '''
        pass


        
        
        
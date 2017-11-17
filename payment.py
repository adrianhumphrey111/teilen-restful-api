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
    
    def __init__(self, first_name="", last_name="", email=""):
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
    
    def chargeRider(self, amount, customer_id, transaction_key):
        stripe.api_key = config.stripe_api_key_secret
        
        try:
            # Use Stripe's library to make requests...
            resp = stripe.Charge.create(
                          amount=amount,
                          currency="usd",
                          customer=customer_id, # obtained with Stripe.js
                          metadata={'transaction_key': transaction_key}
                        )
            return True, resp
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            body = e.json_body
            err  = body.get('error', {})
            error = {'Status is:': e.http_status,
                     'Type is: ' : err.get('type'),
                     'Code is: ': err.get('code'),
                     'Param is: ': err.get('param'),
                     'Message is: ': err.get('message')}
        
            print "Status is: %s" % e.http_status
            print "Type is: %s" % err.get('type')
            print "Code is: %s" % err.get('code')
            # param is '' in this case
            print "Param is: %s" % err.get('param')
            print "Message is: %s" % err.get('message')
            
            return False, error
    
        
        

        
        
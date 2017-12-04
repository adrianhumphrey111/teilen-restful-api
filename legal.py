'''
Created on Dec 3, 2017

@author: adrianhumphrey
'''

import webapp2

class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        INDEX_HTML = open('privacy.html').read()
        self.response.out.write(INDEX_HTML)

class TermsHandler(webapp2.RequestHandler):
    def get(self):
        INDEX_HTML = open('terms.html').read()
        self.response.out.write(INDEX_HTML)

app = webapp2.WSGIApplication([
    ('/privacy-policy', PrivacyHandler),
    ('/legal/terms-of-service', TermsHandler)
], debug=True)
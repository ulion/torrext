import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

import bencode
import sha
import base64
import time


class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
      
    

class MainPage(webapp.RequestHandler):
  def get(self, hash_info):
    page=memcache.get(hash_info)
    if page is None:
      torrents_query = Torrent.all().order('-date')
      torrent = torrents_query.get()

      template_values = {
        'torrent': torrent
        }

      path = os.path.join(os.path.dirname(__file__), 'torrent_page.html')
      page=template.render(path, template_values)
      memcache.set(hash_info, page)
      
    self.response.out.write(page)
      
application = webapp.WSGIApplication(
                                     [('/([\w]*)', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
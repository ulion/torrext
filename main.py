import cgi
from google.appengine.ext.webapp import template, RequestHandler, WSGIApplication
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.ext import db


class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
class MainPage(RequestHandler):
  def get(self):
    frontpage=memcache.get('front_page')
    if frontpage is None:
      import os
      torrents_query = Torrent.all().order('-date')
      torrents = torrents_query.fetch(50)
      template_values = {
        'torrents': torrents,
        }
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      frontpage=template.render(path, template_values)
      memcache.set('front_page', frontpage)
      
    self.response.out.write(frontpage)

application = WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
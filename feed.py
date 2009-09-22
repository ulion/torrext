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
  def get(self, feed_type): 
    feed_cache=memcache.get(feed_type)
    if feed_cache is None:
      import os
      torrents_query = Torrent.all().order('-date')
      torrents = torrents_query.fetch(250)
      template_values = {
        'torrents': torrents,
        }
      if feed_type == 'rss':
        path = os.path.join(os.path.dirname(__file__), 'rss.xml')
      elif:
        path = os.path.join(os.path.dirname(__file__), 'feed.txt')
      feed_cache=template.render(path, template_values)

      memcache.set(feed_type, feed_cache)

      
    self.response.out.write(feed_cache)

application = WSGIApplication([('/(rss).xml', MainPage),
                               ('/(feed).txt', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
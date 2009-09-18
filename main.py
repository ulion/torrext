import time
times=[]
begin=time.time()
import cgi
times.append(begin-time.time())
#from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, RequestHandler, WSGIApplication
times.append(begin-time.time())
from google.appengine.ext.webapp.util import run_wsgi_app
times.append(begin-time.time())
from google.appengine.api import memcache
times.append(begin-time.time())
from google.appengine.ext import db
times.append(begin-time.time())

class Torrent(db.Model):
  info_hash = db.StringProperty()
  #content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
class MainPage(RequestHandler):
  def get(self):
    frontpage=memcache.get('front_page')
    if frontpage is None:
      start=time.time()
      times.append(begin-time.time())
      import os
      times.append(begin-time.time())
      self.response.out.write('<!--imports: ' + str(start-time.time()) + '-->\n')
      torrents_query = Torrent.all().order('-date')
      torrents = torrents_query.fetch(100)
      self.response.out.write('<!--fetch(10): ' + str(start-time.time()) + '-->\n')
      template_values = {
        'torrents': torrents,
        }
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      frontpage=template.render(path, template_values)
      self.response.out.write('<!--render(): ' + str(start-time.time()) + '-->\n')
      memcache.set('front_page', frontpage, 30)
      self.response.out.write('<!--set(): ' + str(start-time.time()) + '-->\n')
      
    self.response.out.write(frontpage)
    self.response.out.write('<!\n')
    for e in times:
      self.response.out.write(str(e) + '\n')
    self.response.out.write('-->')

application = WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
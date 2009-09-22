import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache


class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
      
class TorrentURL(db.Model):
  torrent = db.StringProperty()
  url = db.StringProperty()

class MainPage(webapp.RequestHandler):
  def get(self, info_hash):

    if shelf.reques.get('raw') == '1':
      torrent_text = memcache.get(info_hash)
      if torrent_text is None:
        torrents_query = Torrent.all()
        torrents_query.filter("info_hash = ", info_hash)
        torrent = torrents_query.get()
        torrent_urls_query = TorrentURL.all()
        torrent_urls_query.filter("torrent =", torrent.info_hash)
        torrent_urls = torrent_urls_query.fetch(10)
        page         = torrent.content + '\n\n'
        for url in torrent_urls:
          page += url + '\n'
        memcache.set(info_hash, page)
        
    else:
      page=memcache.get('page' + info_hash)
      if page is None:
        torrents_query = Torrent.all()
        torrents_query.filter("info_hash = ", info_hash)
        torrent = torrents_query.get()
        torrent_urls_query = TorrentURL.all()
        torrent_urls_query.filter("torrent =", torrent.info_hash)
        torrent_urls = torrent_urls_query.fetch(10)
      
        template_values = {
          'torrent': torrent,
          'torrent_urls': torrent_urls
          }

        path = os.path.join(os.path.dirname(__file__), 'torrent_page.html')
        page=template.render(path, template_values)
        memcache.set('page' + info_hash, page)
      
      self.response.out.write(page)
      
application = webapp.WSGIApplication(
                                     [('/([\w]*)', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
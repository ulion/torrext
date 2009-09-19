import cgi
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import base64
import sys

class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class TorrentURL(db.Model):
  torrent = db.StringProperty()
  url = db.StringProperty()
  
class Upload(webapp.RequestHandler):
  def post(self):
    torrent_url=self.request.get('torrent_url')
    torrent64=self.request.get('fileb64')
    file_contents=''
    if torrent_url is not None and len(torrent_url) > 12: # CHECK IF IT'S URL SUBMISSION
      torrent_urls_query = TorrentURL.all()
      torrent_urls_query.filter("url =", torrent_url)
      if torrent_urls_query.count(1) < 1:
        import urllib2
        from google.appengine.api import urlfetch
        try:
          result = urlfetch.fetch(torrent_url)
          file_contents = result.content
        except:
          self.response.out.write('failed to get the file ' + str(sys.exc_info()[0]))
      else:
        self.response.out.write('url already in store')
        
    elif torrent64 is not None and len(torrent64) > 1: # BASE64 ENCODED FILE
      file_contents = base64.b64decode(torrent64)

    else:
      try: # TRY TO ACCESS FILE CONTENTS
        file_contents = self.request.POST['file'].value
      except:
        self.response.out.write('no url nor file were provided')
        
    if len(file_contents) > 0:
      try: # DO NOT OUTPUT ANYTHING TOO UGLY :P
        import bencode
        try: # TRY TO DECODE BENCODE
          file_dictionary = bencode.bdecode(file_contents)
        except:
          self.response.out.write('torrent file can\'t be read' + str(sys.exc_info()[0]))
          file_dictionary=None
      
        if file_dictionary is not None:
          import sha
          info_hash = sha.new(bencode.bencode(file_dictionary['info'])).hexdigest().upper() # create info_hash
          import binascii
          info_hash_b32 = base64.b32encode(binascii.unhexlify(info_hash))
      
          torrent = Torrent()
          torrent.info_hash = info_hash
      
          torrents_query = Torrent.all()
          torrents_query.filter("info_hash = ",info_hash)

          if torrents_query.count(1) < 1:
            torrent.content  = "info hash: " + info_hash + "\n"
            torrent.content += "magnet link: <a href=\"magnet:?xt=urn:btih:" + info_hash_b32 + "\">magnet:?xt=urn:btih:" + info_hash_b32 + "</a>\n"
            if torrent_url is not None: # IN CASE ITS FROM A FETCH ALSO ADD WHERE IT CAME FROM
              torrent.content  += "Download: <a href=\"" + torrent_url + "\">" + torrent_url + "</a>\n"
            else:
              torrent.content  += "\n"
            try: # TRY TO READ THE CREATION DATE
              import time
              torrent.content += "Created: " + time.asctime(time.gmtime(file_dictionary['creation date'])) + "\n"
            except:
              torrent.content += "no date in file.\n"
            try: # TRY TO ACCESS THE CREATOR STRING
              torrent.content += "Created by: " + file_dictionary['created by'] + "\n\n"
            except:
              torrent.content += "\n"
            try: # TRY TO GET COMMENTS FROM THE CREATOR
              torrent.content += file_dictionary['comment'] + "\n\n"
            except:
              torrent.content += "This torrent has no comments.\n\n"
            try: #TRY TO ACCESS THE LIST OF FILES IN CASE ITS MULTIFILE TORRENT
              file_dictionary['info']['files']
              torrent.content += "Files:\n"
              for each_file in file_dictionary['info']['files']:
                torrent.content += each_file['path'][0] + " - " + str(each_file['length']) + "\n"
            except:
              try: # IF THE LIST OF FILES IS NOT ACCESSIBLE GET THE NAME OF THE TORRENT
                file_dictionary['info']['name']
                torrent.content += "File:\n"
                torrent.content += file_dictionary['info']['name']
                try: # GET THE SIZE OF THE TORRENT
                  torrent.content += " - " + str(file_dictionary['info']['length']) + "\n"
                except:
                  torrent.content += "\n"
              except:
                self.response.out.write('bad torrent, no file name declared')

            torrent.put() # STORE THE TEXT TO THE DATASTORE
            from google.appengine.api import memcache
            memcache.delete('front_page')
            memcache.delete('rss')
        
            self.redirect('/' + info_hash) # 302 HTTP REDIRECT TO THE TORRENT PAGE
  
          else:
            if torrent_url is not None and len(torrent_url) > 12:
              torrent_URL = TorrentURL()
              torrent_URL.torrent = torrent.info_hash
              torrent_URL.url = torrent_url
              torrent_URL.put()
              from google.appengine.api import memcache
              memcache.delete(torrent.info_hash)
              memcache.delete('rss')
              self.redirect('/' + info_hash) # 302 HTTP REDIRECT TO THE TORRENT PAGE
            else:
              self.response.out.write('torrent already here')
      except:
        self.response.out.write('unexpected error' + sys.exc_info()[0])

application = webapp.WSGIApplication([('/upload', Upload)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

import bencode
import sha
import base64
import time
import binascii
import sys

class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  

  
class Upload(webapp.RequestHandler):
  def post(self):
    
    torrent_url=self.request.get('torrent_url')
    if torrent_url is not None:
      self.response.out.write(torrent_url)
      file_contents='omg'
                                                                 ## TODO: get the file!!!
    else:
      try:
        file_contents = self.request.POST['file'].value
      except:
        self.response.out.write('no url nor file were provided')
      
    try:
      try:
        file_dictionary = bencode.bdecode(file_contents)
      except:
        self.response.out.write('torrent file can\'t be read')
        file_dictionary=None
        
      if file_dictionary is not None:
        info_hash = sha.new(bencode.bencode(file_dictionary['info'])).hexdigest().upper() # create info_hash
        info_hash_b32 = base64.b32encode(binascii.unhexlify(info_hash))
  
        torrents_query = Torrent.all().order('-date')
        torrents_query.filter("info_hash = ",info_hash)
  
        if torrents_query.count(1) < 1:
          torrent = Torrent()
          torrent.info_hash = info_hash
          torrent.content  = "info hash: " + info_hash + "\n"
          torrent.content += "magnet link: <a href=\"magnet:?xt=urn:btih:" + info_hash_b32 + "\">magnet:?xt=urn:btih:" + info_hash_b32 + "</a>\n\n"
          try: # TRY TO READ THE CREATION DATE
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
          self.redirect('/' + info_hash_b32) # 302 HTTP REDIRECT TO THE TORRENT PAGE
    
      else:
        self.response.out.write('torrent already here')
    except:
      self.response.out.write('unexpected error' + str(sys.exc_info()))

application = webapp.WSGIApplication([('/upload', Upload)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
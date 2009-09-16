import cgi
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
#from google.appengine.api import urlfetch

import bencode
import sha
import base64
import time
import binascii

class Torrent(db.Model):
  info_hash = db.StringProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  
  
class Upload(webapp.RequestHandler):
  def post(self):
    
    uploaded_file = self.request.get('file')
    file_contents=self.request.POST['file'].value
    file_dictionary=bencode.bdecode(file_contents)
    info_hash=sha.new(bencode.bencode(file_dictionary['info'])).hexdigest().upper() # create info_hash
    info_hash_b32=base64.b32encode(binascii.unhexlify(info_hash))
    
    torrents_query = Torrent.all().order('-date')
    torrents_query.filter("info_hash = ",info_hash)
    
    if torrents_query.count(1) < 1:
      torrent = Torrent()
      torrent.info_hash = info_hash
      torrent.content  = "info hash: " + info_hash + "\n"
      torrent.content += "magnet link: <a href=\"magnet:?xt=urn:btih:" + info_hash_b32 + "\">magnet:?xt=urn:btih:" + info_hash_b32 + "</a>\n\n"
      try:
        torrent.content += "Created: " + time.asctime(time.gmtime(file_dictionary['creation date'])) + "\n"
      except:
        torrent.content += "no date in file.\n"
      try:
        torrent.content += "Created by: " + file_dictionary['created by'] + "\n\n"
      except:
        torrent.content += "\n"
      try:
        torrent.content += file_dictionary['comment'] + "\n\n"
      except:
        torrent.content += "This torrent has no comments.\n\n"
      try:
        file_dictionary['info']['files']
        torrent.content += "Files:\n"
        for each_file in file_dictionary['info']['files']:
          torrent.content += each_file['path'][0] + " - " + str(each_file['length']) + "\n"
      except:
        try:
          file_dictionary['info']['name']
          torrent.content += "File:\n"
          torrent.content += file_dictionary['info']['name']
          try:
            torrent.content += " - " + str(file_dictionary['info']['length']) + "\n"
          except:
            torrent.content += "\n"
        except:
          self.response.out.write('bad torrent, no file name declared')
    
      torrent.put()
      self.redirect('/' + info_hash_b32)
    else:
      self.response.out.write('torrent already here')

application = webapp.WSGIApplication(
                                     [('/upload', Upload)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
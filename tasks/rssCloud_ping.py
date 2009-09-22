import re
from google.appengine.api import urlfetch
import urllib
from google.appengine.api import memcache
import logging

def main():
  url='http://brisk.ly/rest/ping'
  feed_url='http://torrext.appspot.com/rss.xml'
  should_ping=memcache.get('fresh')
  if should_ping is not None:
    form_fields = {
      "url": feed_url
    }
    form_data = urllib.urlencode(form_fields)
    #result = urlfetch.fetch(url=url+feed_url)
    result = urlfetch.fetch(url=url,
                            payload=form_data,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
    logging.debug(str(result.status_code) + ' - ' + result.content)              
    memcache.delete('fresh')

if __name__ == '__main__':
  main()
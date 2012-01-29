#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from time import mktime
from datetime import datetime, timedelta
from wsgiref.handlers import format_date_time

from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch
import string
import PyRSS2Gen

from models import *

class AllFlavorsRSSHandler(webapp.RequestHandler):

    def get_expires(self, expire_days=1):
        expire_date_time = datetime.now() + timedelta(days=expire_days)
        expire_date_time = expire_date_time.replace(hour=0, minute=0)
        return expire_date_time

    def get(self):
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.headers['Expires'] = format_date_time(mktime(self.get_expires().timetuple()))

        # create rss feed
        items = []
        for flavor in fanta_flavor_all():
            item = PyRSS2Gen.RSSItem(
                title = flavor.title,
                link = flavor.url,
                description = flavor.description
            )
            items.append(item)
        
        rss = PyRSS2Gen.RSS2(
            title = "Fanta Flavors",
            link = "http://www.fanta-flavor-finder.appspot.com/",
            description = "A list of all the fanta flavors, from http://m.fanta.com/flavors.xml",
            # lastBuildDate = flavor_response.headers['last-modified'],
            items = items
        )

        self.response.out.write(rss.to_xml())


class RefreshFlavorHandler(webapp.RequestHandler):
    
    flavor_url = 'http://m.fanta.com/flavors.xml'

    def get(self):
        logging.info('Deleting deals')
        # Allow only the cron scheduler to call this URL
        if not self.request.headers.has_key('X-AppEngine-Cron') or not self.request.headers['X-AppEngine-Cron']:
            logging.warn("This URL can only be accessed by the app-engine cron scheduler.")
            return

        logging.info('Refreshing flavors')

        # get flavors from html, and clean
        flavor_response = urlfetch.fetch(url=RefreshFlavorHandler.flavor_url)

        soup = BeautifulSoup(flavor_response.content)
        raw_flavors = soup.findAll('strong')
        logging.info('%s flavors' % len(raw_flavors))

        flavors = map(lambda raw_flavor: {
            'title': string.capwords(raw_flavor.text),
            'description': raw_flavor.findParent().contents[2],
            'url': RefreshFlavorHandler.flavor_url
        }, raw_flavors)

        # add any flavors that don't exist
        for flavor in flavors:
            fanta_flavor_add(flavor['title'], flavor['description'], flavor['url'])
        

def main():
    application = webapp.WSGIApplication([
        ('/rss', AllFlavorsRSSHandler),
        ('/refresh', RefreshFlavorHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

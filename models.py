from google.appengine.ext import db
import logging

class FantaFlavor(db.Model):
    title = db.StringProperty(required=True)
    description = db.StringProperty(required=True)
    url = db.StringProperty(required=True)


def fanta_flavor_all():
    return FantaFlavor.all()

def fanta_flavor_exists(title):
    fanta_flavors = FantaFlavor.all()
    fanta_flavors = fanta_flavors.filter('title =', title)
    return fanta_flavors.count() == 1

def fanta_flavor_add(title, description, url):
    if not fanta_flavor_exists(title):
        logging.info("Adding flavor %s to database, desc=%s, url=%s" % (title, description, url))
        FantaFlavor(title=unicode(title), description=unicode(description), url=unicode(url)).put()

def fanta_flavor_reset():
    for fanta_flavor in fanta_flavor_all():
        db.delete(fanta_flavor)
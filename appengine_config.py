from gaesessions import SessionMiddleware

# suggestion: generate your own random key using os.urandom(64)
# WARNING: Make sure you run os.urandom(64) OFFLINE and copy/paste the output to
# this file.  If you use os.urandom() to *dynamically* generate your key at
# runtime then any existing sessions will become junk every time you start,
# deploy, or update your app!
import os

# https://cloud.google.com/appengine/docs/standard/python/tools/using-libraries-python-27
# appengine_config.py
from google.appengine.ext import vendor
# Add any libraries install in the "lib" folder.
# vendor.add('lib')
vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))


# def add_vendor_packages(vendor_folder):
#     """
#     Adds our vendor packages folder to sys.path so that third-party
#     packages can be imported.
#     """
#     import site
#     import os.path
#     import sys
#
#     # Use site.addsitedir() because it appropriately reads .pth
#     # files for namespaced packages. Unfortunately, there's not an
#     # option to choose where addsitedir() puts its paths in sys.path
#     # so we have to do a little bit of magic to make it play along.
#
#     # We're going to grab the current sys.path and split it up into
#     # the first entry and then the rest. Essentially turning
#     #   ['.', '/site-packages/x', 'site-packages/y']
#     # into
#     #   ['.'] and ['/site-packages/x', 'site-packages/y']
#     # The reason for this is we want '.' to remain at the top of the
#     # list but we want our vendor files to override everything else.
#     sys.path, remainder = sys.path[:1], sys.path[1:]
#
#     # Now we call addsitedir which will append our vendor directories
#     # to sys.path (which was truncated by the last step.)
#     site.addsitedir(os.path.join(os.path.dirname(__file__), vendor_folder))
#
#     # Finally, we'll add the paths we removed back.
#     sys.path.extend(remainder)
#
# # Change 'lib' to whichever directory you use for your vendored packages.
# add_vendor_packages('lib')


COOKIE_KEY = "" # TODO: Generate new COOKIE_KEY using os.urandom(64) See above

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  app = recording.appstats_wsgi_middleware(app)
  return app

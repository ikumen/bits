"""
[gist: drafts]
[gist: published]
"""
import logging
import re
import time
from abc import ABCMeta, abstractmethod
from flask import Flask, redirect, session, jsonify
from flask_github import GitHub
from functools import wraps
from hashids import Hashids
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)
app.config.from_pyfile('local.settings')

logging.basicConfig()
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

github = GitHub(app)
hashids = Hashids(app.config.get('SECRET_KEY'))

print(app.config.get('SECRET_KEY'))

class BitRepository(object):
   __metaclass__ = ABCMeta

   @abstractmethod
   def get(self, user_id, id):
      """Return Bit with given id."""
      pass

   @abstractmethod
   def list(self, user_id):
      """Return list of Bits for user with given id."""

   @abstractmethod
   def save(self, user_id, bit):
      """Save instance to the underlying persistence system."""
      pass

   @abstractmethod
   def delete(self, user_id, id):
      """Delete instance from underlying persistence system."""
      pass


class GistBitRepository(BitRepository):
   def __init__(self, **kwargs):
      self.cache = SimpleCache()

   def _get_user_bits(self, user_id, default=None):
      return self.cache.get(user_id + '_bits') or default

   def get(self, user_id, id):
      for bit in self._get_user_bits(user_id, []):
         if bit['id'] == id:
            return bit
      return None
   
   def list(self, user_id):
      bits = self._get_user_bits(user_id)
      if not bits:
         bits = self._sync_with_bits_resource(user_id)
         self.cache.set(user_id + '_bits', bits)
      return bits

   def _sync_with_bits_resource(self, user_id):
      print('--- inside _sync' + user_id)
      gists = github.get('/users/' + user_id + '/gists?page=1&per_page=30', all_pages=True)
      print(gists)
      bits = []
      for gist in gists:
         if '_bits_' in gist['description']:
            bits.append(self._convert_gist_to_bit(gist['id']))
      return bits

   def save(self, user_id, bit):
      pass

   def delete(self, user_id, bit_id):
      pass

   def _parse_bits_metadata(self, d):
      """
      1-6     _bits_ tag
      7       status 
      8-15    published_at (optional)
      16-88   tags (72 chars ~3 tags)
      89-256  description (~166)
      """
      status = d[6:7]
      m = re.search('_(.*)_(.*)', d[15:])
      return {
         'status': status,
         'published_at': d[7:15] if status is 'P' else None,
         'tags': m.group(1),
         'title': m.group(2)
      }

   def _convert_gist_to_bit(self, gist_id):
      gist = github.get('/' + gist_id)
      print('----> got gist')
      print(gist)
      metadata = self._parse_bits_metadata(gist['description'])
      return {
         'id': hashids.encode(int(time.gmtime())),
         'gist_id': gist['id'],
         'status': metadata['status'],
         'published_at': metadata['published_at'],
         'tags': metadata['tags'],
         'title': metadata['title']
      }


bits_repo = GistBitRepository()


@app.route('/signin')
def login():
   user = session.get('user')
   if not user or 'gh_oauth_token' not in user:
      _log.debug('No authenticated user in session!')
      return github.authorize(scope='read:user,gist')
   else:
      _log.debug('Found authenticated user, redirect to home!')
      return redirect('/')


@app.route('/signout', methods=['get'])
def signout():
   _log.debug('Signing out!')
   session.clear()
   return 'signed out <a href="/signin">signin</a>'


@app.route('/signin/complete')
@github.authorized_handler
def authorized(oauth_token):
   if oauth_token is None:
      return _handle_error(message='Authorization failed!', status=401)

   session['user'] = {'gh_oauth_token': oauth_token}

   # let's get user login info
   user_info = github.get('/user')
   if 'login' not in user_info:
      return _handle_error(message='Unable to load user!', status=401)

   session['user']['login'] = user_info['login']   
   return redirect('/user')


@github.access_token_getter
def token_getter():
   user = session.get('user')
   if user is not None:
      return user['gh_oauth_token']

def _handle_error(message, status=400):
   response = jsonify({'message': message, 'status_code': status})
   response.status_code = status
   return response

def authenticated(f):
   """
   Decorator for routes that require an authenticated user. Decorated
   route handler will get user passed in.
   """
   @wraps(f)
   def decorated(*args, **kwargs):
      if 'user' not in session:
         return redirect('/signout')
      else:
         return f(session['user'], **kwargs)
   return decorated

@app.route('/api/bits')
@authenticated
def api_bits(user):
   print(user)
   bits = bits_repo.list(user['login'], sync_if_empty=True)
   return jsonify(bits)



if __name__ == '__main__':
   app.run(debug=True)
import logging
import re

from flask import current_app, app
from flask_github import GitHub
from pymongo import MongoClient
from werkzeug.contrib.cache import SimpleCache


# shared db instance
db = MongoClient()['bits_db']
# shared github instance
github = GitHub()
# shared cache instance
cache = SimpleCache()
log = logging.getLogger(__name__)


class Dao(object):
    """Generic DAO wrapper for pymongo functions."""
    def __init__(self, db, collection_name, **kwargs):
        self._db = db
        self._collection = db[collection_name]

    def list(self, skip=0, limit=100, **filters):
        bits = self._collection.find(filters, skip=0, limit=100)
        return bits

    def get_by(self, k, v):
        return self._collection.find_one({k: v})

    def get(self, id):
        model = self.get_by(k='_id', v=id)
        if model is None:
            raise KeyError('Unable to find model: %s' % id)
        return model

    def save(self, model):
        rv = self._collection.update_one({'_id': model['_id']}, {'$set': model}, True)
        model['_id'] = model['_id'] if model['_id'] else rv['upserted_id']
        return model

    def delete(self, id):
        return self._collection.delete_one({'_id': id}).deleted_count == 1
            

class Service(object):
    def __init__(self, dao, **kwargs):
        self.dao = dao

    def get(self, id):
        return self.dao.get(id)

    def update(self, id, **data):
        model = self.get(id)
        for k,v in data.items():
            model[k] = v
        return self.save(model)

    def save(self, model):
        return self.dao.save(model)

    def delete(self, id):
        return self.dao.delete(id)

    def list(self, skip=0, limit=100, filters=None):
        return self.dao.list(skip=skip, limit=limit, **filters)


class BitService(Service):
    def __init__(self, dao, cache, **kwargs):
        super(BitService, self).__init__(dao, **kwargs)
        self.cache = cache

    def _fetch_all_from_github(self, user_id):
        """TODO: only able to fetch currently authenticated user's bits."""
        gists = github.get('/gists')
        for gist in gists:
            if self._is_bit(gist):
                bit = self._to_bit_from_gist(self._fetch_one_from_github(gist['id']))
                self.dao.save(bit)

    def _fetch_one_from_github(self, gist_id):
        return github.get('/gists/' + gist_id)

    def _is_bit(self, gist):
        return 'bit.md' in gist['files'].keys()

    def _push_to_github(self, bit):
        """Pushes the given bit information to github as a gist."""
        url = '/gists' # post url
        data = self._to_gist_from_bit(bit)
        if '_id' in bit:
            url = url + '/' + bit['_id'] # gist id is required for patches
            return github.patch(url, data=data)
        else:
            return github.post(url, data=data)

    def _to_bit_from_gist(self, gist):
        files = gist['files']
        meta = self._parse_meta(files['_meta_'])
        return {
            '_id': gist['id'],
            'description': gist['description'],
            'created_at': gist['created_at'],
            'updated_at': gist['updated_at'],
            'user_id': gist['owner']['login'],
            'published': meta['published'],
            'published_at': meta['published_at'],
            'tags': meta['tags'],
            'content': files['bit.md']['content']
        }

    def _parse_meta(self, meta):
        tokens = re.split('\n', meta['content'])
        tags = None
        published = False
        date = None

        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if t.startswith('tags:'):
                tags = filter(None, re.split(',\s+', t[5:].strip()))
            elif t.startswith('published:'):
                t = t[10:].strip()
                published = t or False        
            elif t.startswith('published_at:'):
                t = t[13:].strip()
                date = t or None
        return {'tags': tags, 'published': published, 'published_at': date}


    def _to_gist_from_bit(self, bit):
        return {
            'description': bit['description'],
            'files': {
                '_meta_': {'content': self._denormalize_meta(bit)},
                'bit.md': {'content': bit['content']}
            }
        }

    def _denormalize_meta(self, bit):
        return 'tags:' + (','.join(bit['tags']) if bit['tags'] else '') + '\n' \
                + 'published:' + str(bit['published'] or '') + '\n' \
                + 'published_at:' + (bit['published_at'] or '')


    def save(self, bit):
        # take modified bit, convert to gist and push to github
        gist = self._push_to_github(bit)
        # take returned gist, convert back to bit and save locally
        bit = self._to_bit_from_gist(gist)
        return self.dao.save(bit)

    def create(self, user, **data):
        """Create and new bit for given user.
        """
        if not data:
            data = {
                'description': 'Enter description here',
                'content': 'Enter markdown here',
                'tags': [],
                'published': None,
                'published_at': None
            }
        return self.save(data)
        
    def sync(self, user_id):
        self._fetch_all_from_github(user_id)

    def delete(self, id):
        resp = github.delete('/gists/' + id)
        if resp.status_code is 204:
            self.dao.delete(id)
            return id
        else:
            log.warn('Nothing to delete for %s, reason=%s' % (id, resp.status_code))
            raise RuntimeError('Unable to delete %s, reason=%s', (resp.status_code))
        


class UserService(Service):
    def __init__(self, dao, **kwargs):
        super(UserService, self).__init__(dao, **kwargs)


# shared user service impl
user_service = UserService(Dao(db, 'users'))
# shared bit service impl
bit_service = BitService(Dao(db, 'bits'), cache)
import logging
import pprint

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


class Dao(object):
    """Generic DAO wrapper for pymongo functions."""
    def __init__(self, db, collection_name, **kwargs):
        self._db = db
        self._collection = db[collection_name]

    def list(self, skip=0, limit=100, **filters):
        print('---------')
        print(filters)
        return self._collection.find(filters, skip=0, limit=100)

    def get_by(self, k, v):
        return self._collection.find_one({k: v})

    def get(self, id):
        return self.get_by(k='_id', v=id)

    def save(self, model):
        self._collection.update_one({'_id': model['_id']}, {'$set': model}, True)
        return model

    def delete(self, id):
        return self._collection.delete_one({'_id': id}).deleted_count == 1
            

class Service(object):
    def __init__(self, dao, **kwargs):
        self.dao = dao

    def get(self, id):
        return self.dao.get(id)

    def save(self, model):
        return self.dao.save(model)

    def list(self, skip=0, limit=100, filters=None):
        return self.dao.list(skip=skip, limit=limit, **filters)


class BitService(Service):
    def __init__(self, dao, cache, **kwargs):
        super(BitService, self).__init__(dao, **kwargs)
        self.cache = cache

    def _fetch_all_from_github(self, user_id):
        gists = github.get('/gists')
        for gist in gists:
            if self._is_bit(gist):
                bit = self._to_bit_from_gist(self._fetch_one_from_github(gist['id']))
                self.dao.save(bit)

    def _fetch_one_from_github(self, gist_id):
        return github.get('/gists/' + gist_id)

    def _is_bit(self, gist):
        return '_bits_' in gist['files'].keys()

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
        return {
            '_id': gist['id'],
            'description': gist['description'],
            'created_at': gist['created_at'],
            'updated_at': gist['updated_at'],
            'user_id': gist['owner']['login'],
            'files': {
                '_bits_': {'content': files['_bits_']['content']},
                'README.md': {'content': files['README.md']['content']}
            }
        }

    def _to_gist_from_bit(self, bit):
        return {
            'description': bit['description'],
            'files': {
                '_bits_': {'content': '---'},
                'README.md': {'content': bit['content']}
            }
        }

    def save(self, bit):
        # take modified bit, convert to gist and push to github
        gist = self._push_to_github(bit)
        # take returned gist, convert back to bit and save locally
        bit = self._to_bit_from_gist(gist)
        return self.dao.save(bit)
        


class UserService(Service):
    def __init__(self, dao, **kwargs):
        super(UserService, self).__init__(dao, **kwargs)


# shared user service impl
user_service = UserService(Dao(db, 'users'))
# shared bit service impl
bit_service = BitService(Dao(db, 'bits'), cache)
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
        return self._collection.find(filter=filters, skip=0, limit=100)

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
        self.dao.save(model)

    def list(self, skip=0, limit=100, **filters):
        return self.dao.list(skip=skip, limit=limit, **filters)


class BitService(Service):
    def __init__(self, dao, cache, **kwargs):
        super(BitService, self).__init__(dao, **kwargs)
        self.cache = cache

    def _commit_to_github(self, bit):
        url = '/gists' # post url
        data = self._create_gist_data(bit)
        if '_id' in bit:
            url = url + '/' + bit['_id'] # gist id is required for patches
            return github.patch(url, data=data)
        else:
            return github.post(url, data=data)


    def _create_bit_from_gist_data(self, gist):
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

    def _create_gist_data(self, bit):
        return {
            'description': bit['description'],
            'files': {
                '_bits_': {'content': '---'},
                'README.md': {'content': bit['content']}
            }
        }

    def save(self, bit):
        gist = self._commit_to_github(bit)
        bit = self._create_bit_from_gist_data(gist)
        super(BitService, self).save(bit)
        return bit


class UserService(Service):
    def __init__(self, dao, **kwargs):
        super(UserService, self).__init__(dao, **kwargs)


# shared user service impl
user_service = UserService(Dao(db, 'users'))
# shared bit service impl
bit_service = BitService(Dao(db, 'bits'), cache)
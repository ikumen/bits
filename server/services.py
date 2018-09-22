import logging
import re

from abc import abstractmethod, ABCMeta
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


class UserDao(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, id):
        """Return user with given id or None if user does not exists."""
        pass

    @abstractmethod
    def list(self, filter=None, skip=0, limit=100):
        """Return list of users."""
        pass
    
    @abstractmethod
    def save(self, user):
        """Saves a new user."""
        pass

    @abstractmethod
    def update(self, id, **kwargs):
        """Update user with given id."""
        pass

    @abstractmethod
    def delete(self, id):
        """Delete user with given id."""
        pass


class BitDao(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, user_id, id):
        """Return bit with id and owned by or None if bit does not exists."""
        pass

    @abstractmethod
    def list(self, user_id, filter=None, skip=0, limit=100):
        """Return list of bits owned by user."""
        pass
    
    @abstractmethod
    def save(self, user_id, bit):
        """Saves a bit for user."""
        pass

    @abstractmethod
    def update(self, user_id, id, **kwargs):
        """Update bit with given id and owned by user."""
        pass

    @abstractmethod
    def delete(self, user_id, id):
        """Delete bit with given id and owned by user."""
        pass


class UserMongoDao(UserDao):

    def __init__(self, db, collection_name='users', **kwargs):
        self._db = db
        self._collection_name = collection_name
        self._collection = db[collection_name]

    def get(self, id):
        return self._collection.find_one({'_id': id}, projection={'bits': False})

    def list(self, filter=None, skip=0, limit=100):
        return self._collection.find(filter=filter, projection={'bits': False}, skip=skip, limit=limit)
    
    def save(self, user):
        rv = self._collection.insert_one(user)
        return user

    def update(self, id, **kwargs):
        rv = self._collection.update_one({'_id': id}, {'$set': kwargs})
        return rv.modified_count == 1

    def delete(self, id):
        rv = self._collection.delete_one({'_id': id})
        return rv.deleted_count == 1


class BitMongoDao(BitDao):
    _user_bit_projection = {'oauth': False}
    _user_all_bits_projection = {'oauth': False}

    def __init__(self, db, collection_name='users', **kwargs):
        self.db = db
        self._collection_name = collection_name
        self._collection = db[collection_name]

    def get(self, user_id, id):
        return self._collection.find_one(filter={'_id': user_id},
            projection={'name': 1, 'avatar_url': 1, 'bits': {'$elemMatch': {'_id': id}}})

    def list(self, user_id, filter=None, skip=0, limit=100):
        # combine required user_id and optional filter into 1 filter
        filter = dict(filter or {})
        filter.update({'_id': user_id})
        return self._collection.find_one(
            filter=filter, projection={'oauth': 0, 'bits.content': 0})
        # return self._collection.aggregate([
        #     {'$match': filter},
        #     {'$project': {
        #         'name': 1,
        #         'avatar_url': 1,
        #         'bits._id': 1,
        #         'bits.description': 1,
        #         'bits.created_at': 1,
        #         'bits.updated_at': 1,
        #         'bits.published': 1,
        #         'bits.published_at': 1,
        #         'bits.tags': 1,
        #         'authenticated': {'$eq': ['$_id', user_id]}
        #     }}], batchSize=1)
            
    def save(self, user_id, bit):
        rv = self._collection.update_one(
                {'_id': user_id, 'bits._id': {'$ne': bit['_id']}}, # ensure not duplicate
                {'$push': {'bits': bit}})
        if rv.modified_count != 1 or rv.matched_count != 1:
            raise ValueError('Unable to add new bit! modified=%d modified=%d, bit=%s' % 
                (rv.matched_count, rv.modified_count, bit))
        return bit
        
    def update(self, user_id, id, **kwargs):
        rv = self._collection.update_one(
            {'_id': user_id, 'bits._id': {'$eq': id}},
            {'$set': {'bits.$[bit]': kwargs}},
            array_filters=[{'bit._id': {'$eq': id}}])
        return rv.modified_count == 1

    def delete(self, user_id, id):
        rv = self._collection.update_one({'_id': user_id}, 
            {'$pull': {'bits': {'_id': id}}})
        return rv.modified_count == 1


class UserService(object):
    def __init__(self, dao, **kwargs):
        self._dao = dao

    def get(self, id):
        return self._dao.get(id)

    def update(self, id, **kwargs):
        return self._dao.update(id, **kwargs)

    def save(self, user):
        return self._dao.save(user)

    def delete(self, id):
        return self._dao.delete(id)

    def list(self, filter=None, skip=0, limit=100):
        return self._dao.list(filter=filter, skip=skip, limit=limit)


class BitService(object):
    def __init__(self, dao, **kwargs):
        self._dao = dao

    def _fetch_all_from_github(self, user_id):
        """TODO: only able to fetch currently authenticated user's bits."""
        gists = github.get('/gists')
        for gist in gists:
            if self._is_bit(gist):
                full_gist = self._fetch_one_from_github(gist['id'])
                bit = self._to_bit_from_gist(full_gist)
                self._dao.save(user_id, bit)

    def _fetch_one_from_github(self, gist_id):
        return github.get('/gists/' + gist_id)

    def _is_bit(self, gist):
        return 'bit.md' in gist['files'].keys()

    def _patch_to_github(self, id, bit):
        url = '/gists/' + id
        gist_data = self._build_gist_data(bit)
        gist = github.patch(url, data=gist_data)
        return self._to_bit_from_gist(gist)
        
    def _post_to_github(self, bit):
        gist_data = self._build_gist_data(bit)
        gist = github.post('/gists', data=gist_data)
        return self._to_bit_from_gist(gist)

    def _to_bit_from_gist(self, gist):
        files = gist['files']
        meta = self._parse_meta(files['_meta_'])
        return {
            '_id': gist['id'],
            'description': gist['description'],
            'created_at': gist['created_at'],
            'updated_at': gist['updated_at'],
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

    def _build_gist_data(self, bit):
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

    def update(self, user_id, id, **kwargs):
        """Convert bit -> gist data -> github -> gist -> bit."""
        bit = self._patch_to_github(id, kwargs)
        return self._dao.update(user_id, id, **bit)

    def create(self, user_id, **kwargs):
        """Creates a brand new bit with defaults."""
        if kwargs is None:
            return self.save(user_id, {
                'description': 'Enter description here',
                'content': 'Enter markdown here',
                'tags': [],
                'published': None,
                'published_at': None})
        else:
            return self.save(user_id, kwargs)

    def save(self, user_id, bit):
        bit = self._post_to_github(bit)
        return self._dao.save(user_id, bit)
        
    def sync(self, user_id):
        self._fetch_all_from_github(user_id)

    def delete(self, user_id, id):
        resp = github.delete('/gists/' + id)
        if resp.status_code is 204:
            self._dao.delete(user_id, id)
            return id
        else:
            log.warn('Nothing to delete for %s, reason=%s' % (id, resp.status_code))
            raise RuntimeError('Unable to delete %s, reason=%s', (resp.status_code))
        
    def get(self, user_id, id):
        return self._dao.get(user_id, id)

    def list(self, user_id, filter=None, skip=0, limit=100):
        return self._dao.list(user_id, filter, skip, limit)


# shared user service impl
user_service = UserService(UserMongoDao(db))
# shared bit service impl
bit_service = BitService(BitMongoDao(db))
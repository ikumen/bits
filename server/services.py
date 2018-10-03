import logging
import re

from datetime import datetime
from abc import abstractmethod, ABCMeta
from flask import current_app, app
from flask_github import GitHub, GitHubError
from pymongo import MongoClient
from werkzeug.contrib.cache import SimpleCache
from .models import User, Bit


# shared db instance
# db = MongoClient()['bits_db']
# shared github instance
github = GitHub()
# shared cache instance
cache = SimpleCache()
log = logging.getLogger(__name__)

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
BLANK_BIT = {}


class UserService(object):
    __model__ = User

    @classmethod
    def get(cls, id):
        return cls.__model__.get(id)

    @classmethod
    def update(cls, id, **kwargs):
        return cls.__model__.update(id, **kwargs)


class BitService(object):
    __model__ = Bit

    @classmethod
    def get(cls, id):
        return cls.__model__.get(id)

    @classmethod
    def _fetch_all_from_github(cls, user_id):
        gists = github.get('/gists', all_pages=True)
        for gist in gists:
            if cls._is_bit(gist):
                full_gist = cls._fetch_one_from_github(gist['id'])
                cls._to_bit_from_gist(full_gist, upsert=True)

    @classmethod
    def _fetch_one_from_github(cls, gist_id):
        return github.get('/gists/' + gist_id)

    @classmethod
    def _is_bit(cls, gist):
        return 'bit.md' in gist['files'].keys()

    @classmethod
    def _patch_to_github(cls, id, gist_data):
        return github.patch('/gists/' + id, data=gist_data)
        
    @classmethod
    def _post_to_github(cls, gist_data):
        return github.post('/gists', data=gist_data)

    @classmethod
    def _to_bit_from_gist(cls, gist, upsert=False):
        # TODO: validate upstream
        raw_bit_file = gist.get('files', {}).get('bit.md')
        meta, content = cls._parse_raw_bit_file(raw_bit_file)
        return cls.__model__.update(
                id=gist['id'], 
                user_id=gist['owner']['login'], 
                title=gist['description'],
                tags=meta.get('tags', []),
                updated_at=cls._parse_datetime(gist['updated_at']),
                created_at=cls._parse_datetime(gist['created_at']),
                published_at=cls._parse_datetime(meta.get('published_at')),
                content=content,
                upsert=upsert)

    @classmethod
    def _parse_datetime(cls, s):
        return datetime.strptime(s, DATETIME_FORMAT) if s else None

    @classmethod
    def _parse_raw_bit_file(cls, bit_file):
        """Splits the yaml front matter (meta) and markdown (content).

        @param bit_file raw bit file from gist
        @returns tuple of (meta, content)
        """
        meta = {}
        content = ''
        matches = re.search(r'^---(.*?)---\s*(.*)', bit_file['content'], re.DOTALL)
        if matches:
            meta = cls._normalize_meta(matches.groups()[0])
            content = matches.groups()[1] if len(matches.groups()) >= 2 else None
        return (meta, content)
 
    @classmethod
    def _normalize_meta(cls, meta):
        tokens = re.split('\n', meta)
        tags = None
        published_at = None

        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if t.startswith('tags:'):
                tags = filter(None, re.split(',\s*', t[5:].strip()))
            elif t.startswith('published_at:'):
                t = t[13:].strip()
                published_at = t or None


        return {'tags': tags, 'published_at': published_at}

    @classmethod
    def _build_gist_data(cls, bit_data):
        return {
            'description': bit_data.get('title',''),
            'files': {
                'bit.md': {'content': cls._denormalize_meta(bit_data) + bit_data.get('content','')}
            }
        }

    @classmethod
    def _denormalize_meta(cls, bit_data):
        return  '---\n' \
                + 'title: ' + bit_data.get('title', '') + '\n' \
                + 'tags: ' + ','.join(bit_data.get('tags', '')) + '\n' \
                + 'published_at: ' + bit_data.get('published_at','') + '\n' \
                + '---\n'
    
    @classmethod
    def update(cls, id, **kwargs):
        # convert bit -> gist data -> github -> gist -> bit model -> ndb
        gist_data = cls._build_gist_data(kwargs)
        gist = cls._patch_to_github(id, gist_data)
        return cls._to_bit_from_gist(gist)

    @classmethod
    def create(cls, **kwargs):
        # convert bit -> gist data -> github -> gist -> bit model -> ndb
        gist_data = cls._build_gist_data(kwargs)
        gist = cls._post_to_github(gist_data)
        return cls._to_bit_from_gist(gist, upsert=True)

    @classmethod
    def list(cls, user_id, **kwargs):
        return cls.__model__.list(user_id, **kwargs)

    @classmethod
    def delete(cls, id):
        try:
            resp = github.delete('/gists/' + id)
        except GitHubError as e:
            log.exception('Delete unsuccessful, but removing local copy from datastore anyways.')
        cls.__model__.delete(id)

    @classmethod
    def sync(cls, user_id):
        cls._fetch_all_from_github(user_id)
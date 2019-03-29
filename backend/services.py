import json
import re
import time
import logging
import datetime
import requests

from abc import ABCMeta
from concurrent import futures
from flask_github import GitHubError
from requests.exceptions import ConnectionError
from google.cloud import datastore
from google.auth import credentials
from . import helpers


log = logging.getLogger(__name__)


class _EntityService(metaclass=ABCMeta):
    # Name of entity
    _entity = None
    # Name of identifier field
    _id = 'id'
    # Fields for this entity
    _fields = []
    _exclude_from_indexes = []

    def __init__(self, client=None):
        self._client = client

    def _key(self, id):
        """Create entity key for this this model and it's given id.
        """
        return self._client.key(self._entity, id)

    def _query(self):
        return self._client.query(kind=self._entity)

    def upsert(self, **kwargs):
        """Upsert an entity with the given attributes.
        """
        id = kwargs[self._id]
        # get existing or new
        try: 
            with self._client.transaction():
                entity = self.get(id)
                if entity is None:
                    entity = datastore.Entity(key=self._key(id), exclude_from_indexes=self._exclude_from_indexes)
                for k,v in kwargs.items():
                    if k in self._fields:
                        entity.update({k: v})
                self._client.put(entity)
                return entity
        except: 
            msg = 'Unable to save %s: %s' % (self._entity, kwargs)
            log.error(msg, exc_info=1)
            raise helpers.AppError(msg) # pylint: disable=no-member

    def get(self, id):
        return self._client.get(self._key(id))

    def all(self, filters=None, projection=None, order=None, limit=None, offset=0, keys_only=False):
        query = self._query()
        for filter in filters or []:
            if len(filter) == 3:
                query.add_filter(*filter)

        if keys_only:
            query.keys_only()
            return list(query.fetch())
        else:
            if order:
                query.order = order
            if projection:
                query.projection = projection

        return list(query.fetch(limit=limit, offset=offset))

    def delete(self, id):
        self._client.delete(self._key(id))
            

class Users(_EntityService):
    _entity = 'User'
    _id = 'login'
    _fields = ['login', 'email', 'avatar_url', 'access_token', 'name']
    _exclude_from_indexes = ['email', 'avatar_url', 'access_token', 'name']

    def init_app(self, client, app):
        self._client = client
        self._app = app

    def get_for_public(self, id):
        """Return a filtered version of user for public to consume.
        """
        user = self.get(id)

        if user is not None:
            return dict(login=user['login'], avatar_url=user['avatar_url'], name=user['name'] or user['login'])
        return None


class Bits(_EntityService):
    _entity = 'Bit'
    _id = 'id'
    _fields = ['id', 'description', 'content', 'filename', 'updated_at', 'created_at', 'synced_at', 'modified_at']
    _exclude_from_indexes = ['content', 'filename']
    _gists_url_prefix = '/gists'

    def init_app(self, client, github, app):
        self._client = client
        self._github = github
        self._app = app
        self._gist_bit_filenames = app.config.get('BIT_FILE_NAMES', ['bit.md'])

    def create(self, **kwargs):
        try:
            gist_resp = self.upload(**kwargs)
            return self._handle_gist_response(gist_resp)
        except (GitHubError, ConnectionError):
            msg = 'Error while creating bit %s' % json.dumps(kwargs)
            log.error(msg, exc_info=1)
            raise helpers.AppError(msg) # pylint: disable=no-member

    def save(self, **kwargs):
        modified_at = self._now_as_strftime()
        return self.upsert(modified_at=modified_at, **kwargs)

    def all_by_created_at(self):
        return self.all(order=['-created_at'])

    def delete(self, id):
        try:
            super(Bits, self).delete(id)
            self._github.delete('%s/%s' % (self._gists_url_prefix, id))
        except (GitHubError, ConnectionError):
            msg = "Error while deleting '%s'" % id
            log.error(msg, exc_info=1)
            raise helpers.AppError(msg) # pylint: disable=no-member

    def _get_last_synced_datetime(self):
        rv = self.all(projection=['synced_at'], order=['synced_at'], limit=1)
        if len(rv) != 0:
            return rv[0]['synced_at']
        return None

    def load(self, from_beginning=False):
        """Get from GitHub, all gist of type bit that have been updated 
        since given datedtime or all since beginning if since is None.
        """
        since = None
        if not from_beginning:
            since = self._get_last_synced_datetime()
            log.debug('Loading from: %s' % (since))

        # mark our new load time
        synced_at = self._now_as_strftime()

        # start loading gist/bits from GitHub
        executor = futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(self._fetch_all_gists, since, synced_at)
        return synced_at

    def _all_modified(self):
        return self.all(filters=[('modified_at', '>', None)], keys_only=True)

    def upload_modified_to_github(self):
        """Checks to see if there have been any bits saved locally that need
        to be uploaded to GitHub.
        """
        modified_bit_ids_only = self._all_modified()
        log.debug('Found %s modified bits!' % len(modified_bit_ids_only))
        executor = futures.ThreadPoolExecutor(max_workers=1)
        for bit in modified_bit_ids_only:
            executor.submit(self.upload_and_clear_modified_at, bit.key.id_or_name)

    def upload_and_clear_modified_at(self, id):
        """Wrapper for upload so we can put pull up latest data and clearing
        modified_at in transaction.
        """
        log.info('Upload and clear modified flag for: %s' % id)
        try:
            with self._client.transaction():
                bit = self.get(id)
                self.upload(**bit)
                self.upsert(id=id, modified_at=None)
        except:
            log.error('Unable to upload modified bits.', exc_info=1)

    def upload(self, id=None, **kwargs):
        """Submit to GitHub, new (POST) or updated (PATCH) gist from 
        the given bit data.
        """
        log.info('Uploading: %s' % (id or 'new bit'))
        # default is to create/post assuming we have no id
        url, method = self._gists_url_prefix, self._github.post
        if id is not None:
            # otherwise do update since we have id
            url = '%s/%s' % (url, id)
            method = self._github.patch

        # use the filename on record or default to bits.md        
        filename = kwargs.get('filename', self._gist_bit_filenames[0])

        # convert bit data to a structure expected by Github API
        # https://developer.github.com/v3/gists/#create-a-gist
        gist_data = {
            'description': kwargs.get('description', ''),
            'files': { filename: {
                'content': kwargs.get('content', '') }
        }}
        return method(url, data=gist_data)        

    def _fetch_all_gists(self, since, synced_at):
        """Fetch all gists since given datetime."""
        try:
            url = self._gists_url_prefix
            if since is not None:
                url = '%s?since=%s' % (url, since)
            gists = self._github.get(url, all_pages=True)
            log.info('%s gists to load since last load.' % (len(gists)))
            executor = futures.ThreadPoolExecutor(max_workers=1)
            for gist in gists:
                filename = self._get_bit_filename(gist)
                if filename is not None:
                    executor.submit(self._fetch_gist, gist['id'], filename, synced_at)
        except:
            log.error('fetching all gists', exc_info=1)


    def _fetch_gist(self, gist_id, filename, synced_at):
        """Fetch gist with given id."""
        time.sleep(1)
        gist_resp = self._github.get('%s/%s' % (self._gists_url_prefix, gist_id))
        self._handle_gist_response(gist_resp, filename, synced_at)

    def _handle_gist_response(self, gist_resp, filename=None, synced_at=None):
        if synced_at is None:
            synced_at = self._now_as_strftime()

        if filename is None:
            log.info('default filename to: bit.md')
            filename = self._gist_bit_filenames[0]

        file_entry = gist_resp.get('files', {}).get(filename)
        log.debug('saving file: %s = %s' % (filename, gist_resp.get('description', '')))
        return self.upsert(
            content=file_entry['content'], 
            filename=file_entry['filename'],
            modified_at=None,
            synced_at=synced_at,
            **gist_resp)
        
    def _get_bit_filename(self, gist):
        """Returns the file in this gist that contains a bit."""
        for f in gist['files'].keys():
            if f in self._gist_bit_filenames:
                log.debug('filename: %s IS a bit' % f)
                return f
        log.debug('filename: %s, NOT a bit' % f)
        return None

    def _now_as_strftime(self):
        return helpers.strftime(datetime.datetime.now()) # pylint: disable=no-member


import time
import logging

from concurrent import futures
from backend import support
from backend.support import googlecloud
from backend.support.github import github
from backend.bit import model as Bit


log = logging.getLogger(__name__)


class GitHubSyncService(googlecloud.GCModel):
    _kind = 'Sync'
    _id = 'id'
    _fields = [
        'id', # download or upload
        'synced_at'
    ]
    _exclude_from_indexes = []
    _gists_url_prefix = '/gists'
    _empty_content_filler = '---'

    def init_app(self, app):
        self._default_bit_filename = app.config.get('DEFAULT_BIT_FILENAME', 'bit.md')
        # get the supported file names to look for that may contain a bit
        self._gist_bit_filenames = app.config.get('BIT_FILE_NAMES', [self._default_bit_filename])

    def _update_synced_at(self, id, synced_at):
        self.update(id=id, synced_at=synced_at)

    def download(self, since=None):
        """Download all bit type gists from GitHub that have been 
        updated since our last download. Optionally pass since
        to restrict downloading gists updated at or after this time.
        
        :param since: datetime string (YYYY-MM-DDTHH:MM:SSZ) to restrict by
        """
        # mark our new synced_at time
        synced_at = support.strftime()
        executor = futures.ThreadPoolExecutor(max_workers=1)
        executor.submit(self._update_synced_at, 'download', synced_at)
        executor.submit(self._download_all_gists, since)
        return synced_at

    def _get_bit_filename(self, gist):
        """Returns the file in this gist that contains a bit."""
        for f in gist['files'].keys():
            if f in self._gist_bit_filenames:
                log.debug('filename: %s IS a bit' % f)
                return f
            log.debug('filename: %s, NOT a bit' % f)
        return None

    def _download_all_gists(self, since=None):
        """Fetch all gists at or after given since datetime"""
        try:
            url = self._gists_url_prefix
            if since is not None:
                url = '%s?since=%s' % (url, since)
            gists = github.get(url, all_pages=True)
            log.info('%s gists to load' % (len(gists)))
            executor = futures.ThreadPoolExecutor(max_workers=1)
            for gist in gists:
                filename = self._get_bit_filename(gist)
                if filename is not None:
                    executor.submit(self._download_gist, gist['id'], filename)
        except:
            log.error('Fetching all gists', exc_info=1)

    def _download_gist(self, gist_id, filename):
        """Fetch gist with given id."""
        time.sleep(2)
        gist_resp = github.get('%s/%s' % (self._gists_url_prefix, gist_id))
        self._convert_gist_to_bit(gist_resp, filename)

    def _convert_gist_to_bit(self, gist_resp, filename):
        if filename is None:
            log.info('default filename to: bit.md')
            filename = self._gist_bit_filenames[0]

        file_entry = gist_resp.get('files', {}).get(filename)

        log.debug('saving file: %s = %s' % (filename, gist_resp.get('description', '')))
        
        gist_id = gist_resp.get('id')
        bit_data = dict(
            gist_id=gist_id,
            description=gist_resp.get('description', ''),
            content=(file_entry['content'] or self._empty_content_filler)[len(self._empty_content_filler):],
            filename=file_entry['filename'],
            created_at=gist_resp.get('created_at')
        )

        bit = Bit.save(bit_data)        
        return bit

    def upload(self):
        """Uploads all modified bits to their corresponding gists.

        Specifically, we use the following workflow:
            - get all bits that have been modified since our last sync
            - for each bit, upload
        """
        modified_bits_with_keys_only = self._get_all_modified_since_last_sync()
        synced_at = support.strftime()
        executor = futures.ThreadPoolExecutor(max_workers=1)
        for bit in modified_bits_with_keys_only:
            executor.submit(self._upload_bit, bit.key.id_or_name)        
        # finally update our last synced_at time
        executor.submit(self._update_synced_at, 'upload', synced_at)

    def _get_all_modified_since_last_sync(self):
        """Find all bits that have been modified since our last upload.
        """
        # assume we've never uploaded before
        synced_at = None
        operator = '>' 
        rv = self.get('upload')
        # but if we've uploaded before, then
        if rv is not None:
            synced_at = rv[0]['synced_at']
            operator = '>='
        # query bit repository    
        return Bit.all(
            filters=[('modified_at', operator, synced_at)], 
            keys_only=True)

    def _get_bit_and_upload(self, id):
        """Get the bit and upload."""
        self._upload_bit(**Bit.get(id))

    def _upload_bit(self, id=None, **kwargs):
        """Uploads given bit attributes to a gists."""
        log.debug('Uploading: %s' % (id))
        # default is to create a new gist to hold the given bit attributes
        url, method = self._gists_url_prefix, github.post
        if kwargs.get('gist_id') is not None:
            # but if we have an id, then assume we're updating a gist
            url = '%s/%s' % (url, kwargs.get('gist_id'))
            method = github.patch

        filename = kwargs.get('filename', self._default_bit_filename)

        # convert bit data to a structure expected by Github API
        # https://developer.github.com/v3/gists/#create-a-gist
        gist_data = {
            'description': kwargs.get('description', ''),
            'files': { filename: { 'content': self._empty_content_filler + kwargs.get('content', '') } }
        }

        return method(url, data=gist_data)

        

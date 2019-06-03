from .core import log, DatastoreService

class Users(DatastoreService):
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


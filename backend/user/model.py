from backend.support import googlecloud


class UserModel(googlecloud.GCModel):
    _kind = 'User'
    _id = 'login'
    _fields = ['login', 'email', 'avatar_url', 'access_token', 'name']
    _exclude_from_indexes = ['email', 'avatar_url', 'access_token', 'name']

    def get_for_public(self, id):
        """Return a filtered version of user for public to consume.
        """
        user = self.get(id)
        if user is not None:
            return dict(login=user['login'], avatar_url=user['avatar_url'], name=user['name'] or user['login'])
        return None


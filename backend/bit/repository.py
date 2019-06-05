from backend.support.repository import googlecloud


class BitRepository(googlecloud.DatastoreRepository):
    _entity = 'Bit'
    _id = 'id'
    _fields = [
        'id',
        'title',
        'teaser', # snippet of content
        'content',
        'updated_at',
        'created_at',
        'published_at',
        'tags',
    ]
    _exclude_from_indexes = ['content', 'created_at', 'tags']

    def all_by_created_at(self):
        return self.all(order=['-created_at'])

    
from ..support.googlecloud import DatastoreRepository

class BitRepository(DatastoreRepository):
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

    
from backend.support import googlecloud


class BitModel(googlecloud.GCModel):
    _kind = 'Bit'
    _id = 'id'
    _fields = [
        'id', # expose our id, instead of gist_id
        'gist_id', 
        'description',
        'teaser', # snippet of content
        'content',
        'modified_at',
        'created_at',
        'published_at',
        'tags',
    ]
    _exclude_from_indexes = ['content', 'description', 'tags', 'teaser']        

    def all_by_created_at(self):
        return self.all(order=['-created_at'])

    

    
from backend import support
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
        'updated_at',
        'created_at',
        'published_at',
        'tags',
    ]
    _exclude_from_indexes = ['content', 'tags']  

    _partial_bit_projection = ['id', 'teaser', 'description', 'created_at', 'published_at'] 

    def _init_entity(self, entity):
        now = support.strftime()
        entity.update(dict(
            gist_id=None,
            description=None,
            teaser=None,
            content=None,
            updated_at=None,
            created_at=now,
            published_at=None,
            tags=None
        ))
        return entity

    def update(self, upsert=True, **kwargs):
        kwargs['updated_at'] = support.strftime()
        return super(BitModel, self).update(**kwargs)

    def save(self, entity):
        entity['teaser'] = self._make_teaser(entity.get('content'))
        entity['published_at'] = entity.get('published_at') or None
        return super(BitModel, self).save(entity)

    def _make_teaser(self, content=''):
        words = content.split()
        char_count = 0
        teaser_words = []
        for word in words:
            char_count += len(word)
            if char_count > 155:
                break
            teaser_words.append(word)
        return " ".join(teaser_words)

    def all_partial(self):
        return super(BitModel, self).all(
            projection=self._partial_bit_projection, 
            order=['-published_at'])

    def all_partial_drafts(self):
        return super(BitModel, self).all(
            filters=[('published_at', '<=', '')],
            projection=self._partial_bit_projection,
            order=['published_at', '-updated_at'])

    def all_partial_published(self):
        return super(BitModel, self).all(
            filters=[('published_at', '>', '')],
            projection=self._partial_bit_projection,
            order=['-published_at']
        )

    

    
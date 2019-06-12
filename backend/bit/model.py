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
        'modified_at',
        'created_at',
        'published_at',
        'tags',
    ]
    _exclude_from_indexes = ['content', 'tags']        

    def _init_entity(self, entity):
        now = support.strftime()
        entity.update(dict(
            gist_id=None,
            description=None,
            teaser=None,
            content=None,
            modified_at=now,
            created_at=now,
            published_at=None,
            tags=None
        ))
        return entity

    def save(self, entity):
        entity['teaser'] = self._make_teaser(entity.get('content'))
        entity['modified_at'] = support.strftime()
        return super(BitModel, self).save(entity)

    def _make_teaser(self, content=''):
        words = content.split()
        char_count = 0
        teaser_words = []
        for word in words:
            char_count += len(word)
            if char_count > 300:
                break
            teaser_words.append(word)
        return " ".join(teaser_words)

    def all_by_created_at(self):
        return self.all(projection=['id', 'teaser', 'description', 'created_at'], order=['-created_at'])

    

    
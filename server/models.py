# from abc import abstractmethod
# from helpers import JSONSerializable



# class Dao(object):

#     def __init__(self, db, **kwargs):
#         self.__db = db
#         if not self.__model__.__collection_name__:
#             raise ValueError('__collection_name__ is not set for %s' % (self.__model__))
#         self._collection = db[self.__model__.__collection_name__]

#     def _check_type(self, model):
#         if not isinstance(model, self.__model__):
#             raise ValueError('%s is not type %s' % (model, self.__model__))

#     def list(self, **filters):
#         return self._collection.find()

#     def get(self, id):
#         return self._collection.find_one({'_id': id})

#     def save(self, model):
#         self._check_type(model)
#         self._collection.insert_one(model.to_dict(), )
#         return model  

#     def _upsert(self, model)   

#     @abstractmethod
#     def update(self, id, **kwargs):
#         model = self.get(id)
#         if model is None:
#             raise LookupError('Unable to find model %s to update' % (id))
#         for k,v in kwargs.items():
#             setattr(model, k, v)
        

#     def delete(self, id):
#         self._collection.delete_one({'_id': id})


# class BaseModel(JSONSerializable, object):
#     __collection_name__ = None

#     def to_dict(self):
#         return self.__dict__

#     def to_json(self):
#         return self.to_dict()

#     def __repr__(self):
#         return str(self.to_dict())


# class User(BaseModel):
#     __collection_name__ = 'users'

#     def __init__(self, id, name=None, oauth=None):
#         self._id = id
#         self.name = name
#         self.oauth = oauth


# class UserDao(Dao):
#     """User Dao implementation."""
#     __model__ = User

#     def update(self, ):
#         self._check_type(up_user)
#         user = self.get(up_user.id)
#         if user is None:
#             raise LookupError('Unable to find user %s' % (user.id))
#         user.oauth = up_user.oauth
#         self._collection.up

#     def upsert(self, user):
#         if self.exists(user):
#             self.update(user)


# class Bit(BaseModel):
#     __collection_name__ = 'bits'

#     def __init__(self, id, user_id, title, content=None, created_at=None, updated_at=None):
#         self._id = id
#         self.title = title
#         self.content = content
#         self.created_at = created_at
#         self.updated_at = updated_at
#         self.user_id = user_id
    

# class BitDao(Dao):
#     __model__ = Bit



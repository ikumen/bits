import os

from google.cloud import firestore
from google.cloud.exceptions import NotFound
from google.cloud.firestore import DocumentReference, Query

from bitsapp import settings


class Collection:
    def __init__(self, collection_name, db=None):
        self.init(collection_name, db)

    def init(self, collection_name, db=None):
        if db is None:
            db = firestore.Client(project=settings.config.FIRESTORE_PROJECT_ID)
        self.collection = db.collection(collection_name)

    def generate_id(self):
        """Return a new unique document id"""
        doc_ref: DocumentReference = self.collection.document()
        return doc_ref.id
 
    def save(self, **doc): 
        """Save the given document to the collection. An id will be auto-generated if
        it's a new document with no id. Otherwise the given id will be used, overwriting
        any existing data with the same id.
        """
        doc_ref: DocumentReference = self.collection.document(doc.get('id'))
        doc['id'] = doc_ref.id
        doc_ref.set(doc)
        return doc

    def get(self, id): 
        """Return document in the collection with given id, or None."""
        doc_ref: DocumentReference = self.collection.document(id)
        return doc_ref.get().to_dict()

    def list(self, filters=[]): 
        """Return all documents in collection, filtered by given filters."""
        query: Query = None
        for filter in filters:
            if (isinstance(filter, tuple) or isinstance(filter, list)) and len(filter) == 3:
                query = self.collection.where(*filter)
        
        docs = (query.stream() if query 
                    else self.collection.stream())
        return [doc.to_dict() for doc in docs]

    def delete(self, id): 
        """Delete document in collection with given id."""
        doc_ref: DocumentReference = self.collection.document(id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True



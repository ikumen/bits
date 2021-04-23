from google.cloud import firestore
from google.cloud.exceptions import NotFound
from google.cloud.firestore import CollectionReference, Client, DocumentReference, Query


class Collection:
    def __init__(self, name, db=None):
        if not db:
            db = firestore.Client(project="bits")
        self.__collection = db.collection(name)
 
    def add(self, id=None, **doc): 
        """Add given document to the collection."""
        doc_ref: DocumentReference = self.__collection.document(id)
        if doc_ref.get().exists:
            raise Exception(f"Document({id}) already exists")
        else:
            doc['id'] = doc_ref.id
        doc_ref.set(doc)
        return doc

    def update(self, id, doc): 
        """Update the given document."""
        try:
            doc_ref: DocumentReference = self.__collection.document(id)
            doc_ref.update(doc)
        except NotFound:
            raise Exception(f"Document does not exists")            

    def get(self, id): 
        """Return document in the collection with given id, or None."""
        doc_ref: DocumentReference = self.__collection.document(id)
        return doc_ref.get().to_dict()

    def all(self, filters): 
        """Return all documents in collection, filtered by given filters."""
        query: Query = None
        for filter in filters:
            if (isinstance(filter, tuple) or isinstance(filter, list)) and len(filter) == 3:
                query = self.__collection.where(*filter)
        if query:
            return query.stream()
        return self.__collection.stream()

    def delete(self, id): 
        """Delete document in collection with given id."""
        doc_ref: DocumentReference = self.__collection.document(id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True


class BitsCollection(Collection):
    def __init__(self, name='bits', db=None):
        super().__init__(name, db)


bits_collection = BitsCollection()

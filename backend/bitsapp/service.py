import datetime

from typing import List
from pydantic import validate_arguments

from bitsapp import datastore


class BitService(datastore.Collection):
    def __init__(self, db=None):
        super().__init__(collection_name='bits', db=db)

    @validate_arguments
    def new(self, user: dict):
        """Create a new empty bit."""
        return dict(id=self.generate_id(), user=user)

    @validate_arguments
    def save(self, 
            id: str,
            user: str, 
            title: str, 
            category: str = None, 
            content: str = None,
            published: bool = False,
            tags: List[str] = []):
        """Save the given document."""            
        published_at = str(datetime.date.today()) if published else None

        return super().update(
            id=id,
            user=user, 
            title=title, 
            category=category, 
            content=content,
            published_at=published_at,
            tags=tags)  


class CategoryService(datastore.Collection):
    def __init__(self, db=None):
        super().__init__(collection_name='categories', db=db)


bit_service = BitService()
category_service = CategoryService()

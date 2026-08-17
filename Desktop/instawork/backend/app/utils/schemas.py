from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class VideoResponse(BaseModel):
    id: int
    url: str
    file_path: Optional[str]
    tagger: Optional[str]
    status: str
    description: Optional[str]
    tags: List[str]
    error: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            url=obj.url,
            file_path=obj.file_path,
            tagger=obj.tagger,
            status=obj.status,
            description=obj.description,
            tags=obj.tags,
            error=obj.error,
            created_at=obj.created_at,
        )


class SearchResponse(BaseModel):
    results: List[VideoResponse]
    total: int
    rewritten_query: Optional[str] = None
    extracted_tags: List[str] = []

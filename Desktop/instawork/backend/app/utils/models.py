import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

EMBEDDING_DIM = 1536  # text-embedding-3-small


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)           # original filename
    file_path = Column(String, nullable=True)      # permanent path on disk for streaming
    tagger = Column(String, default="gpt4o")       # gpt4o | gemini
    status = Column(String, default="processing")  # processing | ready | failed
    tags_json = Column(Text, default="[]")
    description = Column(Text, nullable=True)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)  # embedding of description
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def tags(self):
        return json.loads(self.tags_json or "[]")

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value)

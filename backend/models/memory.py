from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # text, voice, image, document
    original_filename = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    
    # Metadata
    source = Column(String, nullable=True)  # whatsapp, email, journal, upload, etc.
    timestamp = Column(DateTime(timezone=True), nullable=True)  # When the memory actually occurred
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # AI Processing
    embedding_id = Column(String, nullable=True)  # ChromaDB document ID
    processed = Column(Boolean, default=False)
    
    # Emotional and contextual data
    emotions = Column(JSON, nullable=True)  # {"joy": 0.8, "sadness": 0.1, etc.}
    people_mentioned = Column(JSON, nullable=True)  # List of people mentioned
    locations = Column(JSON, nullable=True)  # List of locations mentioned
    topics = Column(JSON, nullable=True)  # List of topics/themes
    
    # Privacy and access
    is_private = Column(Boolean, default=True)
    encryption_level = Column(String, default="standard")
    
    # Relationships
    user = relationship("User", back_populates="memories")
    
    def __repr__(self):
        return f"<Memory(id={self.id}, user_id={self.user_id}, type='{self.content_type}', title='{self.title}')>" 
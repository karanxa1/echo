from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Replica(Base):
    __tablename__ = "replicas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic Info
    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=True)  # mother, father, friend, etc.
    description = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Status
    status = Column(String, default="alive")  # alive, deceased, unknown
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    date_of_death = Column(DateTime(timezone=True), nullable=True)
    
    # AI Configuration
    personality_traits = Column(JSON, nullable=True)  # {"humor": 0.8, "empathy": 0.9, etc.}
    speaking_style = Column(JSON, nullable=True)  # Tone, vocabulary, patterns
    voice_model_id = Column(String, nullable=True)  # ElevenLabs voice ID
    
    # Memory and Training Data
    training_status = Column(String, default="untrained")  # untrained, training, trained
    memory_collection_id = Column(String, nullable=True)  # ChromaDB collection ID
    total_memories = Column(Integer, default=0)
    last_training_date = Column(DateTime(timezone=True), nullable=True)
    
    # Interaction Settings
    is_active = Column(Boolean, default=True)
    interaction_count = Column(Integer, default=0)
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy
    is_shared = Column(Boolean, default=False)  # Can other family members access?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Replica(id={self.id}, name='{self.name}', relationship='{self.relationship_type}', status='{self.status}')>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    replica_id = Column(Integer, ForeignKey("replicas.id"), nullable=True)  # None for self-conversations
    
    # Conversation metadata
    title = Column(String, nullable=True)
    conversation_type = Column(String, nullable=False)  # self, replica, memory_exploration
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=False)  # user, ai, system
    
    # AI metadata
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Context
    relevant_memories = Column(JSON, nullable=True)  # IDs of memories used for context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Define relationships
Replica.user = relationship("User", back_populates="replicas")
Conversation.user = relationship("User", back_populates="conversations")
Conversation.replica = relationship("Replica")
Conversation.messages = relationship("Message", back_populates="conversation")
Message.conversation = relationship("Conversation", back_populates="messages") 
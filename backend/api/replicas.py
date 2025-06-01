from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.replica import Replica
from api.auth import get_current_active_user

router = APIRouter(prefix="/replicas", tags=["Replicas"])

# Pydantic models
class ReplicaCreate(BaseModel):
    name: str
    relationship: Optional[str] = None
    description: Optional[str] = None
    status: str = "alive"  # alive, deceased, unknown
    date_of_birth: Optional[datetime] = None
    date_of_death: Optional[datetime] = None
    personality_traits: Optional[dict] = None
    speaking_style: Optional[dict] = None

class ReplicaUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    date_of_death: Optional[datetime] = None
    personality_traits: Optional[dict] = None
    speaking_style: Optional[dict] = None
    is_active: Optional[bool] = None

class ReplicaResponse(BaseModel):
    id: int
    name: str
    relationship: Optional[str]
    description: Optional[str]
    status: str
    date_of_birth: Optional[datetime]
    date_of_death: Optional[datetime]
    personality_traits: Optional[dict]
    speaking_style: Optional[dict]
    training_status: str
    total_memories: int
    interaction_count: int
    last_interaction: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# API Endpoints
@router.post("/", response_model=ReplicaResponse)
async def create_replica(
    replica: ReplicaCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new AI replica of a loved one."""
    
    try:
        db_replica = Replica(
            user_id=current_user.id,
            name=replica.name,
            relationship=replica.relationship,
            description=replica.description,
            status=replica.status,
            date_of_birth=replica.date_of_birth,
            date_of_death=replica.date_of_death,
            personality_traits=replica.personality_traits,
            speaking_style=replica.speaking_style,
            training_status="untrained"
        )
        
        db.add(db_replica)
        db.commit()
        db.refresh(db_replica)
        
        return db_replica
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating replica: {str(e)}")

@router.get("/", response_model=List[ReplicaResponse])
async def get_replicas(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all replicas for the current user."""
    
    query = db.query(Replica).filter(Replica.user_id == current_user.id)
    
    if status:
        query = query.filter(Replica.status == status)
    
    replicas = query.order_by(Replica.created_at.desc()).offset(skip).limit(limit).all()
    
    return replicas

@router.get("/{replica_id}", response_model=ReplicaResponse)
async def get_replica(
    replica_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific replica by ID."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    return replica

@router.put("/{replica_id}", response_model=ReplicaResponse)
async def update_replica(
    replica_id: int,
    replica_update: ReplicaUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a replica's information."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    try:
        # Update fields that are provided
        update_data = replica_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(replica, field, value)
        
        db.commit()
        db.refresh(replica)
        
        return replica
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating replica: {str(e)}")

@router.delete("/{replica_id}")
async def delete_replica(
    replica_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a replica and all associated conversations."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    try:
        # Delete associated conversations and messages
        from models.replica import Conversation, Message
        conversations = db.query(Conversation).filter(
            Conversation.replica_id == replica_id
        ).all()
        
        for conv in conversations:
            # Delete messages in this conversation
            db.query(Message).filter(Message.conversation_id == conv.id).delete()
            # Delete the conversation
            db.delete(conv)
        
        # Delete the replica
        db.delete(replica)
        db.commit()
        
        return {"message": "Replica deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting replica: {str(e)}")

@router.post("/{replica_id}/train")
async def train_replica(
    replica_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Train a replica using available memories that mention them."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    try:
        # Import memory service to search for relevant memories
        from services.memory_service import memory_service
        
        # Search for memories that mention this person
        relevant_memories = memory_service.search_memories(
            query=replica.name,
            user_id=current_user.id,
            limit=100  # Get more memories for training
        )
        
        # Filter for high-relevance memories
        training_memories = [
            m for m in relevant_memories 
            if m["similarity_score"] > 0.3  # Lower threshold for training
        ]
        
        # Update replica training status
        replica.training_status = "trained"
        replica.total_memories = len(training_memories)
        replica.last_training_date = datetime.utcnow()
        
        # Create a dedicated collection for this replica's memories
        collection_name = f"user_{current_user.id}_replica_{replica_id}"
        replica.memory_collection_id = collection_name
        
        # Store replica-specific memories in ChromaDB
        if training_memories:
            collection = memory_service.chroma_client.create_collection(
                name=collection_name,
                get_or_create=True
            )
            
            documents = [m["content"] for m in training_memories]
            metadatas = [m["metadata"] for m in training_memories]
            ids = [f"replica_{replica_id}_memory_{i}" for i in range(len(training_memories))]
            
            # Generate embeddings for replica-specific memories
            embeddings = memory_service.embedding_model.encode(documents).tolist()
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
        
        db.commit()
        db.refresh(replica)
        
        return {
            "message": "Replica training completed",
            "memories_processed": len(training_memories),
            "training_status": replica.training_status
        }
        
    except Exception as e:
        replica.training_status = "untrained"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error training replica: {str(e)}")

@router.get("/{replica_id}/memories")
async def get_replica_memories(
    replica_id: int,
    query: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get memories associated with a specific replica."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    try:
        from services.memory_service import memory_service
        
        # Search for memories mentioning this person
        search_query = query if query else replica.name
        memories = memory_service.search_memories(
            query=search_query,
            user_id=current_user.id,
            limit=limit
        )
        
        # Filter for memories that likely involve this person
        relevant_memories = [
            m for m in memories 
            if replica.name.lower() in m["content"].lower() or m["similarity_score"] > 0.7
        ]
        
        return {
            "replica_name": replica.name,
            "total_found": len(relevant_memories),
            "memories": relevant_memories
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memories: {str(e)}")

@router.get("/{replica_id}/stats")
async def get_replica_stats(
    replica_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific replica."""
    
    replica = db.query(Replica).filter(
        Replica.id == replica_id,
        Replica.user_id == current_user.id
    ).first()
    
    if not replica:
        raise HTTPException(status_code=404, detail="Replica not found")
    
    # Get conversation count
    from models.replica import Conversation
    conversation_count = db.query(Conversation).filter(
        Conversation.replica_id == replica_id
    ).count()
    
    return {
        "replica_name": replica.name,
        "relationship": replica.relationship,
        "status": replica.status,
        "training_status": replica.training_status,
        "total_memories": replica.total_memories,
        "conversation_count": conversation_count,
        "interaction_count": replica.interaction_count,
        "last_interaction": replica.last_interaction,
        "created_at": replica.created_at,
        "last_training_date": replica.last_training_date
    } 
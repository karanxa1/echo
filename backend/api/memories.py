import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.memory import Memory
from models.user import User
from api.auth import get_current_active_user
from services.memory_service_simple import memory_service
from config import settings

router = APIRouter(prefix="/memories", tags=["Memories"])

# Pydantic models
class MemoryResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    content_type: str
    source: Optional[str]
    timestamp: Optional[datetime]
    created_at: datetime
    processed: bool
    emotions: Optional[dict]
    people_mentioned: Optional[list]
    locations: Optional[list]
    topics: Optional[list]

    class Config:
        from_attributes = True

class MemoryCreate(BaseModel):
    content: str
    title: Optional[str] = None
    source: str = "manual"
    timestamp: Optional[datetime] = None

class MemorySearch(BaseModel):
    query: str
    limit: int = 10

class SearchResult(BaseModel):
    content: str
    metadata: dict
    similarity_score: float
    memory_id: int

# Helper functions
def save_uploaded_file(file: UploadFile, user_id: int) -> str:
    """Save uploaded file and return file path."""
    # Create user-specific directory
    user_dir = os.path.join(settings.upload_directory, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(user_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

# API Endpoints
@router.post("/text", response_model=MemoryResponse)
async def create_text_memory(
    memory: MemoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a text-based memory."""
    try:
        memory_obj = memory_service.process_text_memory(
            content=memory.content,
            user_id=current_user.id,
            db=db,
            title=memory.title,
            source=memory.source,
            timestamp=memory.timestamp
        )
        
        # Analyze emotions and entities
        emotions = memory_service.analyze_emotions(memory.content)
        entities = memory_service.extract_entities(memory.content)
        
        # Update memory with analysis
        memory_obj.emotions = emotions
        memory_obj.people_mentioned = entities.get("people", [])
        memory_obj.locations = entities.get("locations", [])
        memory_obj.topics = entities.get("topics", [])
        
        db.commit()
        db.refresh(memory_obj)
        
        return memory_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating memory: {str(e)}")

@router.post("/upload/voice", response_model=MemoryResponse)
async def upload_voice_memory(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    source: str = Form("upload"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process a voice memo."""
    
    # Validate file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Check file size
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # Save file
        file_path = save_uploaded_file(file, current_user.id)
        
        # Process voice memory
        memory_obj = memory_service.process_voice_memory(
            file_path=file_path,
            user_id=current_user.id,
            db=db,
            filename=file.filename,
            title=title,
            source=source
        )
        
        # Analyze emotions and entities
        emotions = memory_service.analyze_emotions(memory_obj.content)
        entities = memory_service.extract_entities(memory_obj.content)
        
        # Update memory with analysis
        memory_obj.emotions = emotions
        memory_obj.people_mentioned = entities.get("people", [])
        memory_obj.locations = entities.get("locations", [])
        memory_obj.topics = entities.get("topics", [])
        
        db.commit()
        db.refresh(memory_obj)
        
        return memory_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice memory: {str(e)}")

@router.post("/upload/image", response_model=MemoryResponse)
async def upload_image_memory(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    source: str = Form("upload"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process an image memory."""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image file")
    
    # Check file size
    if file.size > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # Save file
        file_path = save_uploaded_file(file, current_user.id)
        
        # Process image memory
        memory_obj = memory_service.process_image_memory(
            file_path=file_path,
            user_id=current_user.id,
            db=db,
            filename=file.filename,
            title=title,
            description=description,
            source=source
        )
        
        # Analyze emotions and entities
        emotions = memory_service.analyze_emotions(memory_obj.content)
        entities = memory_service.extract_entities(memory_obj.content)
        
        # Update memory with analysis
        memory_obj.emotions = emotions
        memory_obj.people_mentioned = entities.get("people", [])
        memory_obj.locations = entities.get("locations", [])
        memory_obj.topics = entities.get("topics", [])
        
        db.commit()
        db.refresh(memory_obj)
        
        return memory_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image memory: {str(e)}")

@router.get("/", response_model=List[MemoryResponse])
async def get_memories(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's memories with optional filtering."""
    
    query = db.query(Memory).filter(Memory.user_id == current_user.id)
    
    if content_type:
        query = query.filter(Memory.content_type == content_type)
    
    if source:
        query = query.filter(Memory.source == source)
    
    memories = query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()
    
    return memories

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific memory by ID."""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return memory

@router.post("/search", response_model=List[SearchResult])
async def search_memories(
    search: MemorySearch,
    current_user: User = Depends(get_current_active_user)
):
    """Search memories using semantic similarity."""
    
    try:
        results = memory_service.search_memories(
            query=search.query,
            user_id=current_user.id,
            limit=search.limit
        )
        
        return [SearchResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")

@router.get("/files/{memory_id}")
async def get_memory_file(
    memory_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download the original file for a memory."""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    if not memory.file_path or not os.path.exists(memory.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=memory.file_path,
        filename=memory.original_filename or f"memory_{memory.id}",
        media_type="application/octet-stream"
    )

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a memory and its associated files."""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.user_id == current_user.id
    ).first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    try:
        # Delete file if exists
        if memory.file_path and os.path.exists(memory.file_path):
            os.remove(memory.file_path)
        
        # Delete from ChromaDB
        if memory.embedding_id:
            collection = memory_service.get_or_create_collection(current_user.id)
            collection.delete(ids=[memory.embedding_id])
        
        # Delete from database
        db.delete(memory)
        db.commit()
        
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")

@router.get("/stats/overview")
async def get_memory_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics about user's memories."""
    
    total_memories = db.query(Memory).filter(Memory.user_id == current_user.id).count()
    
    # Count by content type
    type_counts = {}
    for content_type in ["text", "voice", "image", "document"]:
        count = db.query(Memory).filter(
            Memory.user_id == current_user.id,
            Memory.content_type == content_type
        ).count()
        type_counts[content_type] = count
    
    # Recent memories
    recent = db.query(Memory).filter(
        Memory.user_id == current_user.id
    ).order_by(Memory.created_at.desc()).limit(5).all()
    
    return {
        "total_memories": total_memories,
        "by_type": type_counts,
        "recent_memories": [
            {
                "id": m.id,
                "title": m.title,
                "content_type": m.content_type,
                "created_at": m.created_at
            } for m in recent
        ]
    } 
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.replica import Conversation, Message
from api.auth import get_current_active_user
from services.ai_service import ai_service
from services.advanced_ai_service import advanced_ai_service

router = APIRouter(prefix="/chat", tags=["Chat"])

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ReplicaChat(BaseModel):
    message: str
    replica_id: int
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    tokens_used: Optional[int] = None
    replica_name: Optional[str] = None
    error: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    title: str
    type: str
    replica_name: Optional[str]
    started_at: str
    last_message_at: str

class MessageResponse(BaseModel):
    id: int
    content: str
    type: str
    timestamp: str
    tokens_used: Optional[int] = None

# API Endpoints
@router.post("/self", response_model=ChatResponse)
async def chat_with_self(
    chat: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with your past self using your memories."""
    
    try:
        result = ai_service.chat_with_self(
            user_message=chat.message,
            user_id=current_user.id,
            db=db,
            conversation_id=chat.conversation_id
        )
        
        if "error" in result:
            return ChatResponse(
                response="",
                conversation_id=result.get("conversation_id", 0),
                error=result["error"]
            )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            tokens_used=result.get("tokens_used")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/replica", response_model=ChatResponse)
async def chat_with_replica(
    chat: ReplicaChat,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with an AI replica of a loved one."""
    
    try:
        result = ai_service.chat_with_replica(
            user_message=chat.message,
            replica_id=chat.replica_id,
            user_id=current_user.id,
            db=db,
            conversation_id=chat.conversation_id
        )
        
        if "error" in result:
            return ChatResponse(
                response="",
                conversation_id=result.get("conversation_id", 0),
                error=result["error"]
            )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            replica_name=result.get("replica_name"),
            tokens_used=result.get("tokens_used")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user."""
    
    try:
        conversations = ai_service.get_user_conversations(current_user.id, db)
        return [ConversationResponse(**conv) for conv in conversations]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific conversation."""
    
    try:
        messages = ai_service.get_conversation_history(conversation_id, current_user.id, db)
        return [MessageResponse(**msg) for msg in messages]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Delete all messages in the conversation
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        
        # Delete the conversation
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

@router.get("/suggestions")
async def get_chat_suggestions(
    conversation_type: str = "self",  # self or replica
    replica_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get suggested conversation starters."""
    
    if conversation_type == "self":
        suggestions = [
            "What was I doing on my last birthday?",
            "How did I feel during my college years?",
            "What are some happy memories from my childhood?",
            "Tell me about a time when I overcame a challenge",
            "What patterns do you see in my relationships?",
            "What activities have brought me the most joy?",
            "How have I grown as a person over the years?",
            "What are my biggest accomplishments?"
        ]
    else:
        # Get replica info for personalized suggestions
        if replica_id:
            from models.replica import Replica
            replica = db.query(Replica).filter(
                Replica.id == replica_id,
                Replica.user_id == current_user.id
            ).first()
            
            if replica:
                suggestions = [
                    f"Hi {replica.name}, how are you?",
                    f"What would you say about my current situation?",
                    f"I miss you {replica.name}, can you comfort me?",
                    f"What advice would you give me right now?",
                    f"Tell me about a favorite memory we shared",
                    f"What are you proud of about me?",
                    f"How should I handle this difficult decision?",
                    f"What would you want me to remember about you?"
                ]
            else:
                suggestions = [
                    "How are you doing?",
                    "I miss you, can you comfort me?",
                    "What advice would you give me?",
                    "Tell me about a memory we shared",
                    "What are you proud of about me?"
                ]
        else:
            suggestions = [
                "How are you doing?",
                "I miss you, can you comfort me?",
                "What advice would you give me?",
                "Tell me about a memory we shared"
            ]
    
    return {"suggestions": suggestions}

@router.get("/stats")
async def get_chat_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat statistics for the user."""
    
    # Total conversations
    total_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()
    
    # Conversations by type
    self_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.conversation_type == "self"
    ).count()
    
    replica_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.conversation_type == "replica"
    ).count()
    
    # Total messages
    total_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()
    
    # User messages vs AI messages
    user_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        Message.message_type == "user"
    ).count()
    
    ai_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        Message.message_type == "ai"
    ).count()
    
    return {
        "total_conversations": total_conversations,
        "conversation_types": {
            "self": self_conversations,
            "replica": replica_conversations
        },
        "total_messages": total_messages,
        "message_breakdown": {
            "user": user_messages,
            "ai": ai_messages
        }
    }
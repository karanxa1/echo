from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.replica import Conversation, Message
from api.auth import get_current_active_user
from services.ai_service import ai_service
from services.advanced_ai_service import advanced_ai_service
from services.free_ai_service import free_ai_service

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

class AdvancedChatMessage(BaseModel):
    message: str
    service_id: str = "memory_companion"
    conversation_id: Optional[int] = None

class AIServiceResponse(BaseModel):
    id: str
    name: str
    description: str
    personality: str
    capabilities: List[str]

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

@router.get("/ai-services", response_model=List[AIServiceResponse])
async def get_ai_services(
    current_user: User = Depends(get_current_active_user)
):
    """Get all available AI services."""
    return advanced_ai_service.get_available_ai_services()

@router.post("/ai-chat", response_model=ChatResponse)
async def chat_with_ai_service(
    chat: AdvancedChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with a specialized AI service."""
    
    try:
        # Get user context
        user_context = {
            "name": current_user.full_name or current_user.username,
            "username": current_user.username,
            "user_id": current_user.id
        }
        
        # Get conversation history if conversation_id provided
        conversation_history = []
        if chat.conversation_id:
            messages = db.query(Message).filter(
                Message.conversation_id == chat.conversation_id
            ).order_by(Message.created_at.desc()).limit(6).all()
            
            for msg in reversed(messages):
                role = "user" if msg.message_type == "user" else "assistant"
                conversation_history.append({"role": role, "content": msg.content})
        
        # Get AI response
        result = advanced_ai_service.chat_with_ai_service(
            service_id=chat.service_id,
            user_message=chat.message,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        if not result.get("success"):
            return ChatResponse(
                response="I'm sorry, but I'm having trouble responding right now. Please try again in a moment.",
                conversation_id=chat.conversation_id or 0,
                error=result.get("error")
            )
        
        # Create or get conversation for advanced AI services
        conversation = None
        if chat.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == chat.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                conversation_type="ai_service",
                title=f"Chat with {result['service_name']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save messages
        user_msg = Message(
            conversation_id=conversation.id,
            content=chat.message,
            message_type="user"
        )
        db.add(user_msg)
        
        ai_msg = Message(
            conversation_id=conversation.id,
            content=result["response"],
            message_type="ai",
            tokens_used=result.get("tokens_used"),
            model_used="gpt-4"
        )
        db.add(ai_msg)
        
        # Update conversation timestamp
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation.id,
            tokens_used=result.get("tokens_used"),
            replica_name=result["service_name"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI chat error: {str(e)}")

@router.get("/ai-suggestions/{service_id}")
async def get_ai_service_suggestions(
    service_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation starters for a specific AI service."""
    
    suggestions = advanced_ai_service.get_service_suggestions(service_id)
    return {"service_id": service_id, "suggestions": suggestions}

@router.post("/smart-suggestions")
async def get_smart_suggestions(
    data: dict,  # {"message": "user message", "recent_topics": []}
    current_user: User = Depends(get_current_active_user)
):
    """Get smart AI service suggestions based on user message."""
    
    user_message = data.get("message", "")
    recent_topics = data.get("recent_topics", [])
    
    suggestions = advanced_ai_service.get_smart_suggestions(user_message, recent_topics)
    return {"message": user_message, "suggested_services": suggestions}

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

# === FREE AI ENDPOINTS ===

class FreeAIChatMessage(BaseModel):
    message: str
    service_id: str = "memory_companion"
    provider: str = "gemini"  # gemini, groq, ollama, huggingface
    conversation_id: Optional[int] = None

@router.get("/free-ai/providers")
async def get_free_ai_providers(
    current_user: User = Depends(get_current_active_user)
):
    """Get available free AI providers."""
    return free_ai_service.get_available_providers()

@router.post("/free-ai/test")
async def test_free_ai_providers(
    current_user: User = Depends(get_current_active_user)
):
    """Test which free AI providers are working."""
    return free_ai_service.test_providers()

@router.get("/free-ai/status")
async def get_free_ai_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed status of all AI providers including fallback info."""
    return free_ai_service.get_provider_status()

@router.post("/free-ai/chat-smart")
async def chat_with_smart_fallback(
    chat: FreeAIChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Smart chat that automatically selects the best available provider."""
    
    # Auto-select best provider if none specified or if specified provider is unavailable
    provider_status = free_ai_service.get_provider_status()
    available_providers = [p for p, status in provider_status.items() if status["available"]]
    
    if not chat.provider or chat.provider not in available_providers:
        # Auto-select best available provider
        if "gemini" in available_providers:
            chat.provider = "gemini"
        elif "groq" in available_providers:
            chat.provider = "groq"
        elif available_providers:
            chat.provider = available_providers[0]
        else:
            return ChatResponse(
                response="No AI providers are currently available. Please try again later.",
                conversation_id=chat.conversation_id or 0,
                error="No providers available"
            )
    
    # Use the regular fallback chat endpoint
    return await chat_with_free_ai(chat, current_user, db)

@router.post("/free-ai/chat", response_model=ChatResponse)
async def chat_with_free_ai(
    chat: FreeAIChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat using free AI providers with automatic fallback (Gemini ↔ Groq)."""
    
    try:
        # Get user context
        user_context = {
            "name": current_user.full_name or current_user.username,
            "username": current_user.username,
            "user_id": current_user.id
        }
        
        # Get conversation history if conversation_id provided
        conversation_history = []
        if chat.conversation_id:
            messages = db.query(Message).filter(
                Message.conversation_id == chat.conversation_id
            ).order_by(Message.created_at.desc()).limit(8).all()  # Increased context
            
            for msg in reversed(messages):
                role = "user" if msg.message_type == "user" else "assistant"
                conversation_history.append({"role": role, "content": msg.content})
        
        # Use the enhanced fallback system
        result = free_ai_service.chat_with_fallback(
            service_id=chat.service_id,
            user_message=chat.message,
            preferred_provider=chat.provider,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        if not result.get("success"):
            return ChatResponse(
                response="I apologize, but all AI providers are currently unavailable. Please try again in a moment.",
                conversation_id=chat.conversation_id or 0,
                error=result.get("error")
            )
        
        # Create or get conversation
        conversation = None
        if chat.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == chat.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
        else:
            # Create new conversation with provider info
            provider_name = result["provider"]
            conversation = Conversation(
                user_id=current_user.id,
                conversation_type="free_ai",
                title=f"AI Chat ({provider_name}) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save messages
        user_msg = Message(
            conversation_id=conversation.id,
            content=chat.message,
            message_type="user"
        )
        db.add(user_msg)
        
        # Include fallback info in the AI message if applicable
        ai_content = result["response"]
        if result.get("fallback_used"):
            fallback_note = f"\n\n*Note: Switched from {result['original_provider']} to {result['fallback_provider']} to ensure uninterrupted service.*"
            ai_content += fallback_note
        
        ai_msg = Message(
            conversation_id=conversation.id,
            content=ai_content,
            message_type="ai",
            model_used=result["provider"]
        )
        db.add(ai_msg)
        
        # Update conversation timestamp
        conversation.last_message_at = datetime.utcnow()
        db.commit()
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation.id,
            replica_name=result["provider"],
            tokens_used=result.get("conversation_length", 0)  # Return context length
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Free AI chat error: {str(e)}")
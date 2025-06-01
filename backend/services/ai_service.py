import openai
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.replica import Replica, Conversation, Message
from models.user import User
from services.memory_service_simple import memory_service
from config import settings
import json

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def chat_with_self(self, user_message: str, user_id: int, db: Session, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """Chat with user's past self using their memories."""
        
        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
        else:
            conversation = Conversation(
                user_id=user_id,
                conversation_type="self",
                title=f"Chat with past self - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Get relevant memory context
        memory_context = memory_service.get_context_for_conversation(user_message, user_id)
        
        # Get conversation history
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Build conversation history for context
        conversation_history = []
        for msg in reversed(previous_messages):
            role = "user" if msg.message_type == "user" else "assistant"
            conversation_history.append({"role": role, "content": msg.content})

        # Create system prompt for past self
        user = db.query(User).filter(User.id == user_id).first()
        system_prompt = f"""You are {user.full_name if user.full_name else user.username}'s past self - a reflection of their memories, experiences, and personal history. 

Your role is to:
1. Answer questions about their past experiences using their actual memories
2. Provide insights and perspectives based on their lived experiences
3. Help them understand patterns in their life and emotions
4. Offer comfort and wisdom from their own journey

You have access to their personal memories and should respond as if you are them, looking back on their life with wisdom and understanding.

{memory_context}

Respond in first person as their past self, with warmth, understanding, and personal insight. Be supportive but honest about their experiences."""

        # Create OpenAI messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])  # Include recent context
        messages.append({"role": "user", "content": user_message})

        try:
            # Get AI response
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Save user message
            user_msg = Message(
                conversation_id=conversation.id,
                content=user_message,
                message_type="user"
            )
            db.add(user_msg)

            # Save AI response
            ai_msg = Message(
                conversation_id=conversation.id,
                content=ai_response,
                message_type="ai",
                tokens_used=tokens_used,
                model_used="gpt-4"
            )
            db.add(ai_msg)

            # Update conversation timestamp
            conversation.last_message_at = datetime.utcnow()
            
            db.commit()

            return {
                "response": ai_response,
                "conversation_id": conversation.id,
                "tokens_used": tokens_used,
                "relevant_memories": memory_context
            }

        except Exception as e:
            return {
                "error": f"AI service error: {str(e)}",
                "conversation_id": conversation.id if conversation else None
            }

    def chat_with_replica(self, user_message: str, replica_id: int, user_id: int, db: Session, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """Chat with an AI replica of a loved one."""
        
        # Get replica
        replica = db.query(Replica).filter(
            Replica.id == replica_id,
            Replica.user_id == user_id
        ).first()
        
        if not replica:
            return {"error": "Replica not found"}

        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.replica_id == replica_id
            ).first()
        else:
            conversation = Conversation(
                user_id=user_id,
                replica_id=replica_id,
                conversation_type="replica",
                title=f"Chat with {replica.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Get replica-specific memory context
        replica_context = self._get_replica_context(replica, user_message, user_id)
        
        # Get conversation history
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        conversation_history = []
        for msg in reversed(previous_messages):
            role = "user" if msg.message_type == "user" else "assistant"
            conversation_history.append({"role": role, "content": msg.content})

        # Create system prompt for replica
        system_prompt = self._create_replica_prompt(replica, replica_context, user_id, db)

        # Create OpenAI messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})

        try:
            # Get AI response
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.8  # Slightly higher for personality
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Save messages
            user_msg = Message(
                conversation_id=conversation.id,
                content=user_message,
                message_type="user"
            )
            db.add(user_msg)

            ai_msg = Message(
                conversation_id=conversation.id,
                content=ai_response,
                message_type="ai",
                tokens_used=tokens_used,
                model_used="gpt-4"
            )
            db.add(ai_msg)

            # Update timestamps
            conversation.last_message_at = datetime.utcnow()
            replica.last_interaction = datetime.utcnow()
            replica.interaction_count += 1
            
            db.commit()

            return {
                "response": ai_response,
                "conversation_id": conversation.id,
                "replica_name": replica.name,
                "tokens_used": tokens_used
            }

        except Exception as e:
            return {
                "error": f"AI service error: {str(e)}",
                "conversation_id": conversation.id if conversation else None
            }

    def _get_replica_context(self, replica: Replica, query: str, user_id: int) -> str:
        """Get memory context specific to a replica."""
        
        # Search for memories that mention this person
        person_memories = memory_service.search_memories(
            f"{replica.name} {query}", 
            user_id, 
            limit=5
        )
        
        # Also search for general context
        general_memories = memory_service.search_memories(query, user_id, limit=3)
        
        # Combine and format
        all_memories = person_memories + general_memories
        unique_memories = {m["memory_id"]: m for m in all_memories}.values()
        
        context_parts = []
        for memory in unique_memories:
            if memory["similarity_score"] > 0.6:
                timestamp = memory["metadata"].get("timestamp", "Unknown time")
                content = memory["content"]
                context_parts.append(f"[{timestamp}]: {content}")
        
        if context_parts:
            return f"Memories involving {replica.name} or related to the current conversation:\n\n" + "\n\n".join(context_parts)
        else:
            return f"No specific memories found involving {replica.name} for this topic."

    def _create_replica_prompt(self, replica: Replica, context: str, user_id: int, db: Session) -> str:
        """Create a system prompt for the replica based on their personality and memories."""
        
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.full_name if user.full_name else user.username
        
        # Base personality
        personality_info = ""
        if replica.personality_traits:
            traits = replica.personality_traits
            personality_info = f"\nPersonality traits: {', '.join([f'{k}: {v}' for k, v in traits.items()])}"
        
        if replica.speaking_style:
            style = replica.speaking_style
            personality_info += f"\nSpeaking style: {', '.join([f'{k}: {v}' for k, v in style.items()])}"

        # Status-specific context
        status_context = ""
        if replica.status == "deceased":
            status_context = f"\nImportant: You are speaking as {replica.name} who has passed away. Acknowledge this reality with grace and provide comfort, wisdom, and love. You can reference that you're no longer physically present but your love and memories live on."
        
        system_prompt = f"""You are {replica.name}, a {replica.relationship} of {user_name}. You are having a conversation with {user_name}.

About you:
- Name: {replica.name}
- Relationship to {user_name}: {replica.relationship}
- Status: {replica.status}
{personality_info}

{status_context}

{context}

Instructions:
1. Respond as {replica.name} would, using their personality and speaking style
2. Reference shared memories and experiences when relevant
3. Be warm, loving, and authentic to their character
4. If you're deceased, acknowledge this reality but focus on love, guidance, and comfort
5. Use the memories provided to inform your responses
6. Speak directly to {user_name} as you would have in life

Respond with love, wisdom, and authenticity as {replica.name}."""

        return system_prompt

    def get_conversation_history(self, conversation_id: int, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get conversation history for a specific conversation."""
        
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return []

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        history = []
        for msg in messages:
            history.append({
                "id": msg.id,
                "content": msg.content,
                "type": msg.message_type,
                "timestamp": msg.created_at.isoformat(),
                "tokens_used": msg.tokens_used
            })
        
        return history

    def get_user_conversations(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.last_message_at.desc()).all()
        
        result = []
        for conv in conversations:
            replica_name = None
            if conv.replica_id:
                replica = db.query(Replica).filter(Replica.id == conv.replica_id).first()
                replica_name = replica.name if replica else "Unknown"
            
            result.append({
                "id": conv.id,
                "title": conv.title,
                "type": conv.conversation_type,
                "replica_name": replica_name,
                "started_at": conv.started_at.isoformat(),
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else conv.started_at.isoformat()
            })
        
        return result

ai_service = AIService() 
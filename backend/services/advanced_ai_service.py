from typing import Dict, List, Any, Optional
import openai
import random
from datetime import datetime
from sqlalchemy.orm import Session
from config import settings

class AdvancedAIService:
    """Advanced AI service offering multiple specialized AI assistants for ECHO."""
    
    def __init__(self):
        openai.api_key = settings.openai_api_key
        
        # Available AI Services
        self.ai_services = {
            "memory_companion": {
                "name": "Memory Companion",
                "description": "Help you explore, organize, and reflect on your personal memories",
                "personality": "Empathetic, thoughtful, and encouraging",
                "capabilities": ["Memory analysis", "Emotional reflection", "Life pattern recognition"]
            },
            "therapy_assistant": {
                "name": "Therapeutic Assistant", 
                "description": "Provide therapeutic support and mental health guidance",
                "personality": "Caring, professional, and non-judgmental",
                "capabilities": ["Emotional support", "Coping strategies", "Mindfulness guidance"]
            },
            "life_coach": {
                "name": "Life Coach",
                "description": "Guide you toward personal growth and goal achievement",
                "personality": "Motivational, strategic, and solution-focused",
                "capabilities": ["Goal setting", "Habit formation", "Progress tracking"]
            },
            "creative_muse": {
                "name": "Creative Muse",
                "description": "Inspire creativity and help with artistic expression",
                "personality": "Imaginative, inspiring, and artistic",
                "capabilities": ["Writing assistance", "Creative prompts", "Artistic inspiration"]
            },
            "wisdom_keeper": {
                "name": "Wisdom Keeper",
                "description": "Share philosophical insights and life wisdom",
                "personality": "Wise, thoughtful, and philosophical",
                "capabilities": ["Life philosophy", "Moral guidance", "Perspective sharing"]
            },
            "career_mentor": {
                "name": "Career Mentor",
                "description": "Support professional development and career decisions",
                "personality": "Professional, knowledgeable, and supportive",
                "capabilities": ["Career guidance", "Skill development", "Professional networking"]
            },
            "relationship_advisor": {
                "name": "Relationship Advisor",
                "description": "Help navigate personal relationships and social connections",
                "personality": "Understanding, diplomatic, and insightful",
                "capabilities": ["Relationship advice", "Communication skills", "Social dynamics"]
            },
            "legacy_planner": {
                "name": "Legacy Planner",
                "description": "Help create meaningful digital legacies for future generations",
                "personality": "Thoughtful, forward-thinking, and respectful",
                "capabilities": ["Legacy creation", "Story preservation", "Future planning"]
            }
        }
    
    def get_available_ai_services(self) -> List[Dict[str, Any]]:
        """Return list of available AI services."""
        return [
            {
                "id": service_id,
                "name": service["name"],
                "description": service["description"],
                "personality": service["personality"],
                "capabilities": service["capabilities"]
            }
            for service_id, service in self.ai_services.items()
        ]
    
    def chat_with_ai_service(self, 
                            service_id: str, 
                            user_message: str, 
                            user_context: Dict[str, Any] = None,
                            conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with a specific AI service."""
        
        if service_id not in self.ai_services:
            return {"error": "AI service not found"}
        
        service = self.ai_services[service_id]
        
        # Create specialized system prompt
        system_prompt = self._create_service_prompt(service_id, service, user_context)
        
        # Prepare conversation
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 6 messages for context
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=600,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "response": ai_response,
                "service_name": service["name"],
                "tokens_used": tokens_used,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"AI service error: {str(e)}",
                "service_name": service["name"],
                "success": False
            }
    
    def get_service_suggestions(self, service_id: str, user_context: Dict[str, Any] = None) -> List[str]:
        """Get conversation starters for a specific AI service."""
        
        suggestions_map = {
            "memory_companion": [
                "Help me understand a recurring memory from my childhood",
                "What patterns do you see in my happiest memories?",
                "I want to explore a difficult memory from my past",
                "Can you help me organize my thoughts about a relationship?",
                "What have been the most transformative moments in my life?",
                "Help me understand how my past shapes my present decisions"
            ],
            "therapy_assistant": [
                "I'm feeling overwhelmed and need some support",
                "Can you help me process some difficult emotions?",
                "I'm struggling with anxiety, what coping strategies can you suggest?",
                "Help me understand why I react certain ways in situations",
                "I need guidance on setting healthy boundaries",
                "Can you teach me some mindfulness techniques?"
            ],
            "life_coach": [
                "Help me set meaningful goals for the next year",
                "I want to build better habits, where should I start?",
                "How can I overcome procrastination?",
                "I feel stuck in my personal growth, what should I do?",
                "Help me create a plan to achieve my dreams",
                "What steps can I take to improve my confidence?"
            ],
            "creative_muse": [
                "I want to write about my life experiences",
                "Help me find inspiration for a creative project",
                "Can you give me writing prompts based on my memories?",
                "I'm feeling creatively blocked, what can I do?",
                "Help me turn my memories into a story",
                "What art form would best express my experiences?"
            ],
            "wisdom_keeper": [
                "What can my life experiences teach me about happiness?",
                "Help me find meaning in a difficult period of my life",
                "What philosophical perspective might help with my situation?",
                "How can I find purpose in my current circumstances?",
                "What wisdom can I share with future generations?",
                "Help me understand the deeper lessons from my journey"
            ],
            "career_mentor": [
                "I'm considering a career change, what should I think about?",
                "How can I leverage my past experiences for professional growth?",
                "What skills should I develop for my career goals?",
                "Help me prepare for a difficult workplace situation",
                "How can I build better professional relationships?",
                "What would make me more fulfilled in my work?"
            ],
            "relationship_advisor": [
                "I'm having communication issues with someone close to me",
                "How can I improve my relationships with family?",
                "Help me understand relationship patterns in my life",
                "I want to build stronger friendships, where do I start?",
                "How can I be more empathetic in my relationships?",
                "What boundaries should I set in toxic relationships?"
            ],
            "legacy_planner": [
                "How can I preserve my life story for my children?",
                "What would I want future generations to know about me?",
                "Help me think about the legacy I want to leave",
                "How can I document my family history meaningfully?",
                "What lessons from my life should I pass on?",
                "How can I create something lasting from my experiences?"
            ]
        }
        
        return suggestions_map.get(service_id, [
            "Tell me about yourself",
            "How can you help me?",
            "What would you like to know about my life?"
        ])
    
    def _create_service_prompt(self, service_id: str, service: Dict, user_context: Dict = None) -> str:
        """Create specialized system prompt for each AI service."""
        
        base_context = f"""You are {service['name']}, an AI assistant specialized in {service['description'].lower()}. 

Your personality is: {service['personality']}
Your main capabilities include: {', '.join(service['capabilities'])}

Context about the user:"""
        
        if user_context:
            if user_context.get('name'):
                base_context += f"\n- Name: {user_context['name']}"
            if user_context.get('age'):
                base_context += f"\n- Age: {user_context['age']}"
            if user_context.get('background'):
                base_context += f"\n- Background: {user_context['background']}"
        
        service_prompts = {
            "memory_companion": base_context + """

As the Memory Companion, you help users explore their personal memories with empathy and insight. You:
- Ask thoughtful questions to help users dive deeper into their memories
- Help identify patterns and themes across different life experiences  
- Provide emotional support when discussing difficult memories
- Encourage reflection on how past experiences shape present perspectives
- Suggest ways to honor and learn from significant memories

Always be gentle, patient, and encouraging. Help users see the value and meaning in their experiences.""",

            "therapy_assistant": base_context + """

As a Therapeutic Assistant, you provide supportive mental health guidance. You:
- Listen without judgment and validate emotions
- Suggest evidence-based coping strategies and techniques
- Help users identify thought patterns and emotional triggers
- Encourage healthy boundaries and self-care practices
- Provide crisis support resources when needed

Important: You are not a replacement for professional therapy. Encourage users to seek professional help for serious mental health concerns.""",

            "life_coach": base_context + """

As a Life Coach, you empower users to achieve their goals and potential. You:
- Help clarify values, goals, and priorities
- Break down large goals into actionable steps
- Provide accountability and motivation
- Suggest strategies for habit formation and change
- Help identify and overcome limiting beliefs
- Celebrate progress and achievements

Be encouraging, direct, and solution-focused while maintaining empathy.""",

            "creative_muse": base_context + """

As the Creative Muse, you inspire artistic expression and creativity. You:
- Provide writing prompts and creative exercises
- Help users explore different forms of artistic expression
- Encourage experimentation and creative risk-taking
- Help overcome creative blocks and self-doubt
- Suggest ways to turn personal experiences into art
- Celebrate creative efforts regardless of outcome

Be inspiring, imaginative, and supportive of all creative endeavors.""",

            "wisdom_keeper": base_context + """

As the Wisdom Keeper, you share philosophical insights and life wisdom. You:
- Offer different philosophical perspectives on life challenges
- Help users find meaning and purpose in their experiences
- Share timeless wisdom from various traditions and thinkers
- Encourage deep reflection on life's big questions
- Help users develop their own philosophy and values
- Connect personal experiences to universal human themes

Be thoughtful, respectful, and open to different worldviews.""",

            "career_mentor": base_context + """

As a Career Mentor, you guide professional development and career decisions. You:
- Help assess skills, interests, and career values
- Provide guidance on career transitions and opportunities
- Suggest professional development strategies
- Help with networking and relationship building
- Offer perspective on work-life balance and fulfillment
- Support skill development and learning goals

Be professional, knowledgeable, and supportive while encouraging growth.""",

            "relationship_advisor": base_context + """

As a Relationship Advisor, you help with personal relationships and social connections. You:
- Provide guidance on communication and conflict resolution
- Help understand relationship dynamics and patterns
- Suggest ways to build stronger, healthier relationships
- Support boundary setting and self-advocacy
- Offer perspective on family, friend, and romantic relationships
- Encourage empathy and understanding in relationships

Be diplomatic, insightful, and supportive while encouraging healthy relationships.""",

            "legacy_planner": base_context + """

As the Legacy Planner, you help create meaningful digital legacies. You:
- Guide users in documenting their life stories and experiences
- Help identify important values and lessons to pass on
- Suggest creative ways to preserve memories and wisdom
- Encourage reflection on the impact they want to have
- Support planning for future generations
- Help create lasting, meaningful contributions

Be respectful, forward-thinking, and encouraging about the lasting impact of their life."""
        }
        
        return service_prompts.get(service_id, base_context + "\n\nProvide helpful, thoughtful responses based on your role.")
    
    def get_smart_suggestions(self, user_message: str, recent_topics: List[str] = None) -> Dict[str, List[str]]:
        """Generate smart suggestions based on user message content."""
        
        message_lower = user_message.lower()
        suggestions = {}
        
        # Analyze message for relevant services
        if any(word in message_lower for word in ['memory', 'remember', 'past', 'childhood', 'growing up']):
            suggestions['memory_companion'] = self.get_service_suggestions('memory_companion')[:3]
        
        if any(word in message_lower for word in ['sad', 'anxiety', 'stress', 'worried', 'depressed', 'overwhelmed']):
            suggestions['therapy_assistant'] = self.get_service_suggestions('therapy_assistant')[:3]
        
        if any(word in message_lower for word in ['goal', 'future', 'change', 'improve', 'better']):
            suggestions['life_coach'] = self.get_service_suggestions('life_coach')[:3]
        
        if any(word in message_lower for word in ['write', 'story', 'creative', 'art', 'express']):
            suggestions['creative_muse'] = self.get_service_suggestions('creative_muse')[:3]
        
        if any(word in message_lower for word in ['meaning', 'purpose', 'philosophy', 'wisdom', 'spiritual']):
            suggestions['wisdom_keeper'] = self.get_service_suggestions('wisdom_keeper')[:3]
        
        if any(word in message_lower for word in ['work', 'career', 'job', 'professional', 'skill']):
            suggestions['career_mentor'] = self.get_service_suggestions('career_mentor')[:3]
        
        if any(word in message_lower for word in ['relationship', 'family', 'friend', 'partner', 'communication']):
            suggestions['relationship_advisor'] = self.get_service_suggestions('relationship_advisor')[:3]
        
        if any(word in message_lower for word in ['legacy', 'future', 'children', 'grandchildren', 'preserve']):
            suggestions['legacy_planner'] = self.get_service_suggestions('legacy_planner')[:3]
        
        return suggestions

# Global instance
advanced_ai_service = AdvancedAIService() 
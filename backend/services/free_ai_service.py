from typing import Dict, List, Any, Optional
import requests
import json
from datetime import datetime
from config import settings

class FreeAIService:
    """Free AI service supporting multiple free AI APIs for ECHO."""
    
    def __init__(self):
        # API Keys (add these to your config.env)
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '')
        self.groq_api_key = getattr(settings, 'GROQ_API_KEY', '')
        self.huggingface_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', '')
        
        # API Endpoints
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.hf_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        
        # Available providers
        self.providers = {
            "gemini": {"name": "Google Gemini", "available": bool(self.gemini_api_key)},
            "groq": {"name": "Groq", "available": bool(self.groq_api_key)},
            "huggingface": {"name": "Hugging Face", "available": bool(self.huggingface_api_key)},
            "ollama": {"name": "Ollama (Local)", "available": True}  # Always available if installed
        }

    def chat_with_free_ai(self, 
                         service_id: str, 
                         user_message: str, 
                         provider: str = "gemini",
                         user_context: Dict[str, Any] = None,
                         conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat using free AI providers with automatic fallback."""
        
        # Define fallback chain: primary -> secondary -> tertiary
        fallback_chain = self._get_fallback_chain(provider)
        
        for attempt, current_provider in enumerate(fallback_chain):
            try:
                result = self._call_provider(current_provider, service_id, user_message, user_context, conversation_history)
                
                if result.get("success"):
                    # Add fallback info if we had to switch providers
                    if attempt > 0:
                        result["fallback_used"] = True
                        result["original_provider"] = provider
                        result["fallback_provider"] = current_provider
                        result["provider"] = f"{result['provider']} (fallback)"
                    
                    return result
                    
            except Exception as e:
                print(f"Provider {current_provider} failed: {str(e)}")
                if attempt == len(fallback_chain) - 1:  # Last attempt
                    return {"error": f"All AI providers failed. Last error: {str(e)}", "success": False}
                continue
        
        return {"error": "All AI providers failed", "success": False}

    def _get_fallback_chain(self, primary_provider: str) -> List[str]:
        """Get the fallback chain for a given primary provider."""
        # Define intelligent fallback order based on reliability and speed
        fallback_chains = {
            "gemini": ["gemini", "groq", "ollama", "huggingface"],
            "groq": ["groq", "gemini", "ollama", "huggingface"],
            "ollama": ["ollama", "gemini", "groq", "huggingface"],
            "huggingface": ["huggingface", "gemini", "groq", "ollama"]
        }
        
        # Filter out unavailable providers
        chain = fallback_chains.get(primary_provider, ["gemini", "groq", "ollama", "huggingface"])
        return [p for p in chain if self.providers[p]["available"] or p == "ollama"]

    def _call_provider(self, provider: str, service_id: str, user_message: str, user_context: Dict = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Call a specific AI provider."""
        if provider == "gemini":
            return self._chat_with_gemini(service_id, user_message, user_context, conversation_history)
        elif provider == "groq":
            return self._chat_with_groq(service_id, user_message, user_context, conversation_history)
        elif provider == "ollama":
            return self._chat_with_ollama(service_id, user_message, user_context, conversation_history)
        elif provider == "huggingface":
            return self._chat_with_huggingface(service_id, user_message, user_context, conversation_history)
        else:
            return {"error": f"Provider '{provider}' not supported", "success": False}

    def _chat_with_gemini(self, service_id: str, user_message: str, user_context: Dict = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Google Gemini."""
        if not self.gemini_api_key:
            return {"error": "Gemini API key not configured", "success": False}
        
        # Build prompt
        system_prompt = self._get_service_prompt(service_id, user_context)
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
        
        # Add conversation history
        if conversation_history:
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-4:]])
            full_prompt = f"{system_prompt}\n\nConversation History:\n{context}\n\nUser: {user_message}\nAssistant:"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 600
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{self.gemini_url}?key={self.gemini_api_key}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "response": ai_response,
                "provider": "Google Gemini",
                "success": True
            }
        else:
            return {"error": f"Gemini API error: {response.text}", "success": False}

    def _chat_with_groq(self, service_id: str, user_message: str, user_context: Dict = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Groq."""
        if not self.groq_api_key:
            return {"error": "Groq API key not configured", "success": False}
        
        # Build messages
        messages = [
            {"role": "system", "content": self._get_service_prompt(service_id, user_context)}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])
        
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": "llama3-8b-8192",  # Fast and free model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600
        }
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.groq_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]
            return {
                "response": ai_response,
                "provider": "Groq (Llama 3)",
                "success": True
            }
        else:
            return {"error": f"Groq API error: {response.text}", "success": False}

    def _chat_with_ollama(self, service_id: str, user_message: str, user_context: Dict = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with local Ollama."""
        try:
            # Build prompt
            system_prompt = self._get_service_prompt(service_id, user_context)
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            
            # Add conversation history
            if conversation_history:
                context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-4:]])
                full_prompt = f"{system_prompt}\n\nConversation History:\n{context}\n\nUser: {user_message}\nAssistant:"
            
            payload = {
                "model": "llama3",  # You can change this to any installed model
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 600
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["response"]
                return {
                    "response": ai_response,
                    "provider": "Ollama (Local)",
                    "success": True
                }
            else:
                return {"error": f"Ollama error: {response.text}", "success": False}
                
        except requests.exceptions.ConnectionError:
            return {"error": "Ollama not running. Start with: ollama serve", "success": False}

    def _chat_with_huggingface(self, service_id: str, user_message: str, user_context: Dict = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Chat with Hugging Face."""
        if not self.huggingface_api_key:
            return {"error": "Hugging Face API key not configured", "success": False}
        
        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
        
        payload = {
            "inputs": user_message,
            "parameters": {
                "max_new_tokens": 600,
                "temperature": 0.7
            }
        }
        
        response = requests.post(
            self.hf_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data[0]["generated_text"] if isinstance(data, list) else data["generated_text"]
            return {
                "response": ai_response,
                "provider": "Hugging Face",
                "success": True
            }
        else:
            return {"error": f"Hugging Face API error: {response.text}", "success": False}

    def _get_service_prompt(self, service_id: str, user_context: Dict = None) -> str:
        """Get the system prompt for a specific service."""
        service_prompts = {
            "memory_companion": "You are a compassionate Memory Companion. Help users explore and reflect on their personal memories with empathy and insight.",
            "therapy_assistant": "You are a supportive Therapeutic Assistant. Provide caring mental health guidance and coping strategies.",
            "life_coach": "You are a motivational Life Coach. Help users achieve their goals and personal growth.",
            "creative_muse": "You are an inspiring Creative Muse. Help users with artistic expression and creativity.",
            "wisdom_keeper": "You are a wise Wisdom Keeper. Share philosophical insights and life wisdom.",
            "career_mentor": "You are a professional Career Mentor. Guide users in their professional development.",
            "relationship_advisor": "You are a diplomatic Relationship Advisor. Help with personal relationships and communication.",
            "legacy_planner": "You are a thoughtful Legacy Planner. Help users create meaningful digital legacies."
        }
        
        base_prompt = service_prompts.get(service_id, "You are a helpful AI assistant.")
        
        if user_context and user_context.get('name'):
            base_prompt += f" The user's name is {user_context['name']}."
        
        return base_prompt

    def get_available_providers(self) -> Dict[str, Any]:
        """Get list of available AI providers."""
        return self.providers

    def test_providers(self) -> Dict[str, Any]:
        """Test which providers are working."""
        results = {}
        test_message = "Hello, how are you?"
        
        for provider in self.providers:
            try:
                result = self.chat_with_free_ai("memory_companion", test_message, provider)
                results[provider] = {
                    "status": "working" if result.get("success") else "error",
                    "message": result.get("response", result.get("error", "Unknown error"))[:100]
                }
            except Exception as e:
                results[provider] = {"status": "error", "message": str(e)[:100]}
        
        return results

    def chat_with_fallback(self, 
                          service_id: str, 
                          user_message: str, 
                          preferred_provider: str = "gemini",
                          user_context: Dict[str, Any] = None,
                          conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Enhanced chat with intelligent fallback system.
        Automatically switches between Gemini and Groq while preserving conversation context.
        """
        
        # Ensure conversation history is properly formatted
        if conversation_history is None:
            conversation_history = []
        
        # Try the preferred provider first, then fallback
        result = self.chat_with_free_ai(
            service_id=service_id,
            user_message=user_message,
            provider=preferred_provider,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        # Add conversation context info to the result
        result["conversation_length"] = len(conversation_history)
        result["user_context"] = user_context
        
        return result

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all providers including fallback availability."""
        status = {}
        
        for provider_id, provider_info in self.providers.items():
            # Test basic availability
            is_available = provider_info["available"]
            
            if provider_id == "ollama":
                # Special check for Ollama
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    is_available = response.status_code == 200
                except:
                    is_available = False
            
            status[provider_id] = {
                "name": provider_info["name"],
                "available": is_available,
                "fallback_priority": self._get_fallback_priority(provider_id),
                "recommended_for": self._get_provider_recommendations(provider_id)
            }
        
        return status
    
    def _get_fallback_priority(self, provider: str) -> int:
        """Get fallback priority for a provider (lower = higher priority)."""
        priority_map = {
            "gemini": 1,  # Highest quality, good free tier
            "groq": 2,    # Fastest, good for fallback
            "ollama": 3,  # Local, no API limits
            "huggingface": 4  # Backup option
        }
        return priority_map.get(provider, 5)
    
    def _get_provider_recommendations(self, provider: str) -> List[str]:
        """Get recommendations for when to use each provider."""
        recommendations = {
            "gemini": ["High-quality responses", "Complex conversations", "Primary choice"],
            "groq": ["Fast responses", "High-volume usage", "Best fallback for Gemini"],
            "ollama": ["Privacy-focused", "Offline usage", "No API limits"],
            "huggingface": ["Experimental models", "Specialized tasks", "Research purposes"]
        }
        return recommendations.get(provider, ["General use"])

# Global instance
free_ai_service = FreeAIService() 
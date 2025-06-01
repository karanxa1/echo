import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Send, Mic, MicOff, LogOut, User, Bot, Sparkles } from 'lucide-react';
import { apiService } from '../services/api';
import type { User as UserType } from '../services/api';
import ChatBackgroundVideo from '../components/ChatBackgroundVideo';
import AIServiceSelector from '../components/AIServiceSelector';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'ai';
  timestamp: Date;
}

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedAIService, setSelectedAIService] = useState('memory_companion');
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!apiService.isAuthenticated()) {
          router.push('/login');
          return;
        }

        const userData = await apiService.getCurrentUser();
        setUser(userData);
        
        // Add welcome message
        setMessages([
          {
            id: '1',
            content: `Hello ${userData.full_name?.split(' ')[0] || userData.username}! I'm your Memory Companion, ready to help you explore your memories and thoughts. Choose any AI assistant from the sidebar to get started, or ask me anything about your life experiences.`,
            type: 'ai',
            timestamp: new Date(),
          },
        ]);
      } catch (error) {
        console.error('Auth check failed:', error);
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isSending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim(),
      type: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsSending(true);

    try {
      // Use the advanced AI service
      const response = await apiService.chatWithAIService(
        selectedAIService, 
        userMessage.content, 
        currentConversationId || undefined
      );
      
      // Update conversation ID for future messages
      if (response.data.conversation_id && !currentConversationId) {
        setCurrentConversationId(response.data.conversation_id);
      }
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        type: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      
      // Fallback AI response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I understand what you're sharing. While I'm processing your request, I'm here to listen and help you reflect on your experiences. Could you tell me more about what's on your mind?",
        type: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
      toast.error('Using fallback response. AI service may be limited.');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleLogout = () => {
    apiService.logout();
    router.push('/');
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    toast.info(isRecording ? 'Recording stopped' : 'Recording started');
  };

  const handleServiceChange = (serviceId: string) => {
    setSelectedAIService(serviceId);
    // Reset conversation when switching services
    setCurrentConversationId(null);
    
    // Add a service switch message
    const switchMessage: Message = {
      id: Date.now().toString(),
      content: `Switched to ${serviceId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}. How can I help you today?`,
      type: 'ai',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, switchMessage]);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-center">
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading ECHO AI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      <ChatBackgroundVideo />
      
      {/* Header */}
      <header className="relative z-10 bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">ECHO AI</h1>
                  <p className="text-sm text-white/70">Your Memory Companion</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-white/80">
                <User className="h-5 w-5" />
                <span className="hidden sm:block">{user?.full_name || user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-white/80 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:block">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="relative z-10 flex h-[calc(100vh-4rem)]">
        {/* AI Service Sidebar */}
        <div className="w-80 bg-black/10 backdrop-blur-sm border-r border-white/10 p-4 overflow-y-auto">
          <AIServiceSelector
            selectedService={selectedAIService}
            onServiceChange={handleServiceChange}
            onSuggestionClick={handleSuggestionClick}
          />
        </div>

        {/* Chat Content */}
        <div className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-white/90 text-gray-900 backdrop-blur-sm'
                      : 'bg-black/40 text-white backdrop-blur-sm border border-white/20'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.type === 'ai' && (
                      <Bot className="h-5 w-5 mt-0.5 text-blue-400 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <p className={`text-xs mt-2 ${
                        message.type === 'user' ? 'text-gray-500' : 'text-white/50'
                      }`}>
                        {message.timestamp.toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isSending && (
              <div className="flex justify-start">
                <div className="bg-black/40 text-white backdrop-blur-sm border border-white/20 rounded-2xl px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <Bot className="h-5 w-5 text-blue-400" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-black/20 backdrop-blur-sm border-t border-white/10 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-4">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Share your thoughts, memories, or ask me anything..."
                  className="w-full bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl px-4 py-3 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent resize-none"
                  disabled={isSending}
                />
              </div>
              
              <button
                onClick={toggleRecording}
                className={`p-3 rounded-xl transition-all duration-200 ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-white/10 hover:bg-white/20 text-white border border-white/20'
                }`}
              >
                {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>
              
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isSending}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 
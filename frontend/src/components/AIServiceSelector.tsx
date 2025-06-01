import { useState, useEffect } from 'react';
import { Brain, Heart, Lightbulb, Palette, Book, Briefcase, Users, Star, ChevronDown, ChevronUp } from 'lucide-react';
import { apiService } from '../services/api';

interface AIService {
  id: string;
  name: string;
  description: string;
  personality: string;
  capabilities: string[];
}

interface AIServiceSelectorProps {
  selectedService: string;
  onServiceChange: (serviceId: string) => void;
  onSuggestionClick: (suggestion: string) => void;
}

const serviceIcons: Record<string, any> = {
  memory_companion: Heart,
  therapy_assistant: Brain,
  life_coach: Lightbulb,
  creative_muse: Palette,
  wisdom_keeper: Book,
  career_mentor: Briefcase,
  relationship_advisor: Users,
  legacy_planner: Star,
};

const serviceColors: Record<string, string> = {
  memory_companion: 'from-pink-500 to-rose-500',
  therapy_assistant: 'from-blue-500 to-indigo-500',
  life_coach: 'from-green-500 to-emerald-500',
  creative_muse: 'from-purple-500 to-violet-500',
  wisdom_keeper: 'from-amber-500 to-orange-500',
  career_mentor: 'from-cyan-500 to-teal-500',
  relationship_advisor: 'from-red-500 to-pink-500',
  legacy_planner: 'from-yellow-500 to-amber-500',
};

export default function AIServiceSelector({ selectedService, onServiceChange, onSuggestionClick }: AIServiceSelectorProps) {
  const [services, setServices] = useState<AIService[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  useEffect(() => {
    loadServices();
  }, []);

  useEffect(() => {
    if (selectedService) {
      loadSuggestions(selectedService);
    }
  }, [selectedService]);

  const loadServices = async () => {
    try {
      const response = await apiService.getAIServices();
      setServices(response.data);
    } catch (error) {
      console.error('Failed to load AI services:', error);
    }
  };

  const loadSuggestions = async (serviceId: string) => {
    setLoadingSuggestions(true);
    try {
      const response = await apiService.getAIServiceSuggestions(serviceId);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleServiceSelect = (serviceId: string) => {
    onServiceChange(serviceId);
    setIsExpanded(false);
  };

  const selectedServiceData = services.find(s => s.id === selectedService);
  const SelectedIcon = selectedServiceData ? serviceIcons[selectedService] : Heart;
  const selectedColor = serviceColors[selectedService] || 'from-gray-500 to-gray-600';

  return (
    <div className="space-y-4">
      {/* Service Selector */}
      <div className="relative">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full bg-black/20 backdrop-blur-sm border border-white/20 rounded-2xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all duration-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 bg-gradient-to-r ${selectedColor} rounded-lg flex items-center justify-center`}>
                <SelectedIcon className="h-4 w-4 text-white" />
              </div>
              <div className="text-left">
                <p className="font-medium">{selectedServiceData?.name || 'Memory Companion'}</p>
                <p className="text-xs text-white/70">{selectedServiceData?.personality || 'Empathetic and thoughtful'}</p>
              </div>
            </div>
            {isExpanded ? (
              <ChevronUp className="h-5 w-5 text-white/70" />
            ) : (
              <ChevronDown className="h-5 w-5 text-white/70" />
            )}
          </div>
        </button>

        {/* Dropdown */}
        {isExpanded && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-black/80 backdrop-blur-sm border border-white/20 rounded-2xl p-2 z-50 max-h-96 overflow-y-auto">
            <div className="space-y-1">
              {services.map((service) => {
                const Icon = serviceIcons[service.id] || Heart;
                const color = serviceColors[service.id] || 'from-gray-500 to-gray-600';
                
                return (
                  <button
                    key={service.id}
                    onClick={() => handleServiceSelect(service.id)}
                    className={`w-full p-3 rounded-xl text-left transition-all duration-200 hover:bg-white/10 ${
                      selectedService === service.id ? 'bg-white/10 ring-1 ring-white/20' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-8 h-8 bg-gradient-to-r ${color} rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5`}>
                        <Icon className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white text-sm">{service.name}</p>
                        <p className="text-xs text-white/70 mt-1">{service.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {service.capabilities.slice(0, 3).map((capability, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-white/10 rounded-md text-xs text-white/80"
                            >
                              {capability}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Quick Suggestions */}
      {selectedServiceData && (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <div className={`w-6 h-6 bg-gradient-to-r ${selectedColor} rounded-lg flex items-center justify-center`}>
              <SelectedIcon className="h-3 w-3 text-white" />
            </div>
            <h3 className="text-sm font-medium text-white">Conversation Starters</h3>
          </div>
          
          {loadingSuggestions ? (
            <div className="flex items-center justify-center py-4">
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {suggestions.slice(0, 3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onSuggestionClick(suggestion)}
                  className="w-full p-3 bg-black/20 backdrop-blur-sm border border-white/10 rounded-xl text-left text-sm text-white/90 hover:bg-white/10 hover:border-white/20 transition-all duration-200 group"
                >
                  <div className="flex items-start space-x-2">
                    <span className="text-white/50 group-hover:text-white/70 transition-colors">💭</span>
                    <span className="flex-1">{suggestion}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
} 
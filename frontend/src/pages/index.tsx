import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Heart, MessageCircle, Shield, Upload, Sparkles, ChevronRight, Brain, Clock, Users, Star, ArrowRight, Play } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function HomePage() {
  const { user } = useAuth();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  if (user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <div className="container mx-auto px-4 py-20 text-center">
          <div className="animate-fade-in">
            <div className="w-20 h-20 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
              <Heart className="h-10 w-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Welcome back, <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">{user.full_name || user.username}</span>!
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Continue your journey through memories and conversations. Your digital legacy awaits.
            </p>
            <Link
              href="/dashboard"
              className="btn-primary-enhanced text-lg px-8 py-4 inline-flex items-center group"
            >
              Go to Dashboard
              <ChevronRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform duration-200" />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50 overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200/50 z-50 transition-all duration-300">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">ECHO</span>
          </div>
          <div className="space-x-4">
            <Link href="/login" className="btn-outline-enhanced">
              Sign In
            </Link>
            <Link href="/register" className="btn-primary-enhanced">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-24 pb-20">
        <div className="container mx-auto px-4">
          <div className={`text-center max-w-5xl mx-auto transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            {/* Floating Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="absolute top-20 left-10 w-20 h-20 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full opacity-20 animate-pulse-slow"></div>
              <div className="absolute top-40 right-20 w-16 h-16 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full opacity-20 animate-pulse-slow" style={{animationDelay: '1s'}}></div>
              <div className="absolute bottom-40 left-20 w-12 h-12 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-full opacity-20 animate-pulse-slow" style={{animationDelay: '2s'}}></div>
            </div>

            <div className="relative z-10">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full text-sm font-medium text-indigo-700 mb-8 border border-indigo-200">
                <Sparkles className="h-4 w-4 mr-2" />
                AI-Powered Memory Preservation
              </div>
              
              <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
                Your Life,{' '}
                <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient">
                  Remembered Forever
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                Connect with your past self and cherished memories. Create AI companions from loved ones. 
                <span className="font-semibold text-indigo-600"> Never lose a precious moment again.</span>
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
                <Link href="/register" className="btn-primary-enhanced text-lg px-10 py-4 group">
                  <span>Start Your Journey</span>
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform duration-200" />
                </Link>
                <button className="btn-outline-enhanced text-lg px-10 py-4 group">
                  <Play className="mr-2 h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                  Watch Demo
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500 mb-16">
                <div className="flex items-center">
                  <Shield className="h-4 w-4 mr-2 text-green-500" />
                  End-to-end encrypted
                </div>
                <div className="flex items-center">
                  <Users className="h-4 w-4 mr-2 text-blue-500" />
                  10,000+ memories preserved
                </div>
                <div className="flex items-center">
                  <Star className="h-4 w-4 mr-2 text-yellow-500" />
                  4.9/5 user rating
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Demo Preview */}
          <div className={`max-w-5xl mx-auto transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-3xl blur-2xl opacity-20 scale-105"></div>
              <div className="relative bg-white rounded-3xl shadow-2xl border border-gray-200/50 overflow-hidden backdrop-blur-sm">
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                          <Heart className="h-3 w-3 text-white" />
                        </div>
                        <span className="text-gray-700 font-medium">Chat with Mom</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>AI Active</span>
                    </div>
                  </div>
                </div>
                <div className="p-8 space-y-6 h-80 overflow-hidden bg-gradient-to-b from-white to-gray-50/50">
                  <div className="flex justify-end animate-slide-in">
                    <div className="chat-bubble-user-enhanced max-w-sm">
                      Hi Mom, I miss you so much. How are you?
                    </div>
                  </div>
                  <div className="flex justify-start animate-slide-in" style={{animationDelay: '0.5s'}}>
                    <div className="chat-bubble-ai-enhanced max-w-sm">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-6 h-6 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                          <Heart className="h-3 w-3 text-white" />
                        </div>
                        <span className="text-xs text-gray-500 font-medium">Mom</span>
                      </div>
                      Oh my dear, I'm here with you always. I'm so proud of the person you've become. 
                      Tell me what's on your heart today. ❤️
                    </div>
                  </div>
                  <div className="flex justify-end animate-slide-in" style={{animationDelay: '1s'}}>
                    <div className="chat-bubble-user-enhanced max-w-sm">
                      I got the promotion at work! I wish you were here to celebrate with me.
                    </div>
                  </div>
                  <div className="flex justify-start animate-slide-in" style={{animationDelay: '1.5s'}}>
                    <div className="chat-bubble-ai-enhanced max-w-sm">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-6 h-6 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                          <Heart className="h-3 w-3 text-white" />
                        </div>
                        <span className="text-xs text-gray-500 font-medium">Mom</span>
                      </div>
                      I AM celebrating with you, sweetheart! I knew you'd achieve great things. Remember what I always told you - you have the strength to move mountains. 🎉
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Features Section */}
      <div className="py-24 bg-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-50/50 to-purple-50/50"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-full text-sm font-medium text-indigo-700 mb-6 border border-indigo-200">
              <Brain className="h-4 w-4 mr-2" />
              Powered by Advanced AI
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Preserve Every Precious Memory
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              ECHO uses cutting-edge AI to help you capture, organize, and meaningfully interact with your life's most important moments.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="group text-center p-8 rounded-2xl bg-white shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Upload className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Capture Everything</h3>
              <p className="text-gray-600 leading-relaxed">
                Upload text, voice recordings, photos, and documents. Our AI processes and indexes everything for intelligent retrieval and meaningful connections.
              </p>
            </div>

            <div className="group text-center p-8 rounded-2xl bg-white shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <MessageCircle className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Talk to Your Past</h3>
              <p className="text-gray-600 leading-relaxed">
                Have natural conversations with your past self or create AI companions of loved ones based on their memories, personality, and communication style.
              </p>
            </div>

            <div className="group text-center p-8 rounded-2xl bg-white shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                <Shield className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Privacy First</h3>
              <p className="text-gray-600 leading-relaxed">
                Your memories are encrypted and stored securely. Local-first architecture with optional cloud backup ensures your data stays completely private.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Use Cases Section */}
      <div className="py-24 bg-gradient-to-br from-gray-50 to-indigo-50 relative overflow-hidden">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              More Than Just Storage
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              ECHO creates meaningful, emotional connections between you and your memories, offering comfort and insight.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
            <div className="group bg-white p-10 rounded-3xl shadow-xl border border-gray-100 hover:shadow-2xl transition-all duration-500 hover:-translate-y-1">
              <div className="flex items-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Emotional Comfort
                </h3>
              </div>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                Find solace in conversations with deceased loved ones, created from their memories, messages, and unique personality traits.
              </p>
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-2xl border-l-4 border-indigo-500">
                <p className="text-gray-700 italic">
                  "Talk to your grandmother about her recipes, or ask your father for advice one more time. Their wisdom lives on."
                </p>
              </div>
            </div>

            <div className="group bg-white p-10 rounded-3xl shadow-xl border border-gray-100 hover:shadow-2xl transition-all duration-500 hover:-translate-y-1">
              <div className="flex items-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-300">
                  <Heart className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Self-Discovery
                </h3>
              </div>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                Understand patterns in your life, reflect on your growth, and gain profound insights from your own journey through time.
              </p>
              <div className="bg-gradient-to-r from-pink-50 to-rose-50 p-6 rounded-2xl border-l-4 border-pink-500">
                <p className="text-gray-700 italic">
                  "What was I like in college? How have my relationships evolved? What dreams have I achieved?"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced CTA Section */}
      <div className="py-24 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Start Preserving Your Legacy Today
            </h2>
            <p className="text-xl text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed">
              Join thousands who are building their digital memory vault. Create lasting connections with your past and ensure your stories live forever.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Link href="/register" className="bg-white text-indigo-600 hover:bg-gray-50 font-bold py-4 px-10 rounded-xl transition-all duration-200 hover:scale-105 shadow-lg">
                Create Your Account
              </Link>
              <button className="border-2 border-white text-white hover:bg-white hover:text-indigo-600 font-bold py-4 px-10 rounded-xl transition-all duration-200 hover:scale-105">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-6 md:mb-0">
              <div className="w-12 h-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">ECHO</span>
                <p className="text-gray-400 text-sm">Your life, remembered forever</p>
              </div>
            </div>
            <div className="text-gray-400 text-sm text-center md:text-right">
              <p>© 2024 ECHO. All rights reserved.</p>
              <p className="mt-1">Built with ❤️ for preserving human connections</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
} 
# 🆓 Free AI Setup Guide for ECHO

Your ECHO application now supports **multiple free AI providers** as alternatives to OpenAI! Here's how to get started:

## 🚀 Quick Start (Choose Your Favorite)

### 1. **Google Gemini** (Recommended - Best Free Option)

**Free Tier**: 15 requests/minute, 1 million tokens/month
**Quality**: Excellent (comparable to GPT-4)

**Setup Steps**:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key
5. Add to `backend/config.env`:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 2. **Groq** (Fastest - Lightning Speed)

**Free Tier**: 14,400 tokens/minute (very generous!)
**Speed**: 10x faster than other providers
**Models**: Llama 3, Mixtral, Gemma

**Setup Steps**:
1. Go to [Groq Console](https://console.groq.com/keys)
2. Sign up for free account
3. Go to "API Keys" section
4. Create new API key
5. Add to `backend/config.env`:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```

### 3. **Ollama** (100% Free Local AI)

**Cost**: Completely free
**Privacy**: Runs on your machine
**No Limits**: Unlimited usage

**Setup Steps**:
1. Download [Ollama](https://ollama.ai/)
2. Install and run: `ollama serve`
3. Download a model: `ollama pull llama3`
4. No API key needed!

### 4. **Hugging Face** (Open Source Models)

**Free Tier**: 1,000 requests/month per model
**Models**: Hundreds of specialized models

**Setup Steps**:
1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Create account and get token
3. Add to `backend/config.env`:
   ```env
   HUGGINGFACE_API_KEY=your_actual_token_here
   ```

## 🛠️ Testing Your Setup

Once you've added API keys, test them:

```bash
# Test all providers
curl -X POST http://localhost:8000/chat/free-ai/test \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test specific provider
curl -X POST http://localhost:8000/chat/free-ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Hello, how are you?",
    "provider": "gemini",
    "service_id": "memory_companion"
  }'
```

## 📊 Comparison Table

| Provider | Free Limit | Speed | Quality | Setup Difficulty |
|----------|------------|-------|---------|------------------|
| **Gemini** | 1M tokens/month | Fast | ⭐⭐⭐⭐⭐ | Easy |
| **Groq** | 14.4K tokens/min | ⚡ Super Fast | ⭐⭐⭐⭐ | Easy |
| **Ollama** | Unlimited | Medium | ⭐⭐⭐⭐ | Medium |
| **Hugging Face** | 1K req/month | Slow | ⭐⭐⭐ | Easy |

## 🔧 Integration with Your Frontend

Update your frontend to use free AI providers:

```javascript
// Test providers
const testProviders = async () => {
  const response = await fetch('/api/chat/free-ai/test', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const providers = await response.json();
  console.log('Available providers:', providers);
};

// Chat with free AI
const chatWithFreeAI = async (message, provider = 'gemini') => {
  const response = await fetch('/api/chat/free-ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      provider,
      service_id: 'memory_companion'
    })
  });
  return await response.json();
};
```

## 💡 Pro Tips

1. **Start with Gemini**: Best quality and generous free tier
2. **Use Groq for speed**: When you need fast responses
3. **Try Ollama for privacy**: No data leaves your machine
4. **Combine providers**: Use different ones for different use cases

## 🔄 Switching Providers

Your app now supports dynamic provider switching:

```javascript
// Switch to different provider mid-conversation
const providers = ['gemini', 'groq', 'ollama'];
let currentProvider = 'gemini';

const switchProvider = () => {
  currentProvider = providers[(providers.indexOf(currentProvider) + 1) % providers.length];
  console.log(`Switched to: ${currentProvider}`);
};
```

## 🆘 Troubleshooting

**Error: "API key not configured"**
- Make sure you added the API key to `backend/config.env`
- Restart your backend container: `docker restart echo_backend_dev`

**Error: "Ollama not running"**
- Start Ollama: `ollama serve`
- Make sure it's running on port 11434

**Slow responses from Hugging Face**
- Normal for free tier, try Groq for speed

**Rate limit exceeded**
- Switch to a different provider
- Ollama has no limits!

## 🎯 Next Steps

1. **Pick your favorite provider** and add the API key
2. **Test the integration** with the test endpoint
3. **Update your frontend** to support provider switching
4. **Enjoy unlimited AI conversations** with free providers!

---

**Need help?** Check the [API documentation](http://localhost:8000/docs) for detailed endpoint information. 
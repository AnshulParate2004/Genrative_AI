# Quick Start Guide - Weather & Serper Search Tools

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install aiohttp
```

### Step 2: Get Your API Keys

**OpenWeatherMap (Weather):**
1. Visit https://openweathermap.org/api
2. Click "Sign Up" (it's FREE!)
3. Verify your email
4. Go to "API keys" tab
5. Copy your API key

**Serper (Web Search):**
1. Visit https://serper.dev/
2. Sign up (Google login works)
3. Copy your API key from dashboard
4. You get 2,500 free searches!

### Step 3: Update Your .env File
```bash
# Add these lines to your existing .env file
OPENWEATHER_API_KEY=paste_your_key_here
SERPER_API_KEY=paste_your_key_here
```

### Step 4: Test the Tools
```bash
cd api
python test_tools.py
```

You should see:
- ✅ Weather data for London, New York, Paris
- ✅ Web search results
- ✅ News articles
- ✅ Places/locations

### Step 5: Update Your MCP Client

**Option A - Easy Way (Recommended):**
```bash
cd api
# Backup original
copy mcp_client.py mcp_client_backup.py
# Use new version
copy mcp_client_updated.py mcp_client.py
```

**Option B - Keep Both:**
Just update your `main.py` to import from `mcp_client_updated` instead.

### Step 6: Start Your Server
```bash
cd api
python main.py
```

### Step 7: Try It Out!

Open your chat interface and try:

**Weather:**
- "What's the weather in London?"
- "Give me the forecast for Tokyo"
- "How's the weather in New York in Fahrenheit?"

**Search:**
- "Search for Python tutorials"
- "Find recent news about artificial intelligence"
- "Search for restaurants near Central Park"

## 🎯 What You Get

### Weather Tool
✅ Real-time weather for ANY city worldwide  
✅ 5-day forecasts  
✅ Temperature, humidity, wind, pressure  
✅ Multiple units (Celsius, Fahrenheit, Kelvin)

### Web Search Tool
✅ Google search results  
✅ News articles with filters  
✅ Image search  
✅ Video search  
✅ Local places search  
✅ Shopping results

## 📊 Free Tier Limits

**OpenWeatherMap:**
- 60 calls/minute
- 1,000,000 calls/month
- That's about 33,000 calls per day!

**Serper:**
- 2,500 searches total for free
- Then $5 per 1,000 searches

## 🆘 Common Issues

**"Invalid API Key"**
- Double-check you copied the full key
- No spaces before/after the key in .env
- Make sure .env is in the correct directory

**"Module not found"**
- Run: `pip install aiohttp`
- Make sure you're in the right directory

**"Location not found"**
- Use format: "CityName,CountryCode"
- Example: "Paris,FR" not just "Paris"

## 🎉 You're Done!

Your MCP server now has:
1. ✅ Weather data from anywhere in the world
2. ✅ Web search capabilities
3. ✅ News, images, videos, places, shopping search
4. ✅ All integrated with your LLM

Enjoy! 🚀

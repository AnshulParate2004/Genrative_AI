# Weather and Web Search Tools for MCP

This project includes two powerful tools integrated into your MCP (Model Context Protocol) server:

1. **Weather Tool** - Real-time weather data using OpenWeatherMap API
2. **Serper Search Tool** - Web search capabilities using Serper API (Google Search)

## 📋 Features

### Weather Tool
- ✅ Current weather for any location
- ✅ 5-day weather forecast (3-hour intervals)
- ✅ Multiple temperature units (Celsius, Fahrenheit, Kelvin)
- ✅ Detailed weather information (temperature, humidity, wind, pressure, etc.)
- ✅ Formatted output for easy reading

### Serper Search Tool
- ✅ Regular web search
- ✅ News search with time filters
- ✅ Image search
- ✅ Video search
- ✅ Places/local search
- ✅ Shopping search
- ✅ Geographic location filtering
- ✅ Structured search results

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements_new.txt
```

Or install individually:
```bash
pip install aiohttp fastapi uvicorn mcp python-dotenv pydantic-settings google-generativeai
```

### 2. Get API Keys

#### OpenWeatherMap API (Weather Tool)
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Navigate to "API keys" section
4. Copy your API key
5. Free tier includes: 60 calls/minute, 1,000,000 calls/month

#### Serper API (Web Search Tool)
1. Go to https://serper.dev/
2. Sign up for an account
3. Get your API key from the dashboard
4. Free tier includes: 2,500 searches

### 3. Configure Environment Variables

Add these to your `.env` file:

```env
# Existing keys
GEMINI_API_KEY=your_gemini_key_here

# New tool keys
OPENWEATHER_API_KEY=your_openweather_key_here
SERPER_API_KEY=your_serper_key_here
```

## 📁 Project Structure

```
MY-MCP/
├── api/
│   ├── main.py                    # FastAPI application
│   ├── mcp_client.py              # Original MCP client
│   ├── mcp_client_updated.py      # Updated client with new tools
│   ├── test_tools.py              # Test suite for tools
│   └── utils/
│       ├── logger.py              # Logging configuration
│       ├── weather_tool.py        # Weather tool implementation
│       └── serper_tool.py         # Serper search tool implementation
├── .env                            # Environment variables
└── requirements_new.txt            # Updated dependencies
```

## 🧪 Testing the Tools

Run the test suite to verify everything works:

```bash
cd api
python test_tools.py
```

This will test:
- ✅ Weather queries for multiple cities
- ✅ Weather forecasts
- ✅ Web searches
- ✅ News searches
- ✅ Places searches
- ✅ Image searches
- ✅ Combined tool usage

## 🔧 Integration with Your MCP Client

### Option 1: Replace the existing client

Backup your current `mcp_client.py`:
```bash
cd api
copy mcp_client.py mcp_client_backup.py
```

Replace with the updated version:
```bash
copy mcp_client_updated.py mcp_client.py
```

### Option 2: Manual integration

Add these imports to your `mcp_client.py`:
```python
from utils.weather_tool import WeatherTool, WEATHER_TOOL_SCHEMA, FORECAST_TOOL_SCHEMA
from utils.serper_tool import SerperSearchTool, SERPER_SEARCH_TOOL_SCHEMA
```

Add tool initialization in `__init__`:
```python
self.weather_tool = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY"))
self.serper_tool = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))
self.custom_tools = [WEATHER_TOOL_SCHEMA, FORECAST_TOOL_SCHEMA, SERPER_SEARCH_TOOL_SCHEMA]
```

## 📖 Usage Examples

### Weather Queries

**Current Weather:**
```
Query: "What's the weather in London?"
Query: "Tell me the current weather in Tokyo in Fahrenheit"
Query: "How's the weather in Paris?"
```

**Weather Forecast:**
```
Query: "What's the 5-day forecast for New York?"
Query: "Give me the weather forecast for Berlin"
```

### Web Search Queries

**Regular Search:**
```
Query: "Search for Python tutorials"
Query: "Find information about machine learning"
```

**News Search:**
```
Query: "Search for recent news about AI"
Query: "Find latest technology news from this week"
```

**Places Search:**
```
Query: "Find restaurants near Times Square"
Query: "Search for coffee shops in Seattle"
```

**Image Search:**
```
Query: "Search for images of golden gate bridge"
Query: "Find pictures of cute puppies"
```

## 🛠️ Tool Schemas

### Weather Tool

**Function:** `get_weather`
- **Parameters:**
  - `location` (required): City name with optional country code (e.g., "London,UK")
  - `units` (optional): "metric", "imperial", or "standard" (default: "metric")

**Function:** `get_weather_forecast`
- **Parameters:**
  - `location` (required): City name with optional country code
  - `units` (optional): Temperature units (default: "metric")
  - `cnt` (optional): Number of forecast periods, 1-40 (default: 5)

### Serper Search Tool

**Function:** `web_search`
- **Parameters:**
  - `query` (required): Search query string
  - `num_results` (optional): Number of results, 1-100 (default: 10)
  - `search_type` (optional): "search", "news", "images", "videos", "places", "shopping" (default: "search")
  - `location` (optional): Geographic location filter
  - `time_range` (optional): "qdr:h" (hour), "qdr:d" (day), "qdr:w" (week), "qdr:m" (month), "qdr:y" (year)

## 🔍 How It Works

1. **Tool Registration**: Custom tools are registered alongside MCP server tools
2. **LLM Integration**: Gemini sees all available tools and can call them
3. **Tool Routing**: The client routes calls to either MCP tools or custom tools
4. **Response Formatting**: Results are formatted for readability
5. **Conversation Flow**: Tools can be called multiple times in a conversation

## 📊 API Limits

### OpenWeatherMap (Free Tier)
- 60 calls/minute
- 1,000,000 calls/month
- Historical data: Not available in free tier

### Serper API
- Free tier: 2,500 searches
- Paid plans available for higher usage

## 🐛 Troubleshooting

**API Key Errors:**
- Verify keys are correctly set in `.env`
- Check if keys are active and not expired
- Ensure no extra spaces in the `.env` file

**Import Errors:**
- Install all dependencies: `pip install -r requirements_new.txt`
- Verify you're in the correct directory

**Rate Limit Errors:**
- OpenWeatherMap: Wait a minute before retrying
- Serper: Check your usage at https://serper.dev/dashboard

**Location Not Found:**
- Use format: "CityName,CountryCode" (e.g., "Paris,FR")
- Try without country code if having issues
- Check spelling of city names

## 📝 Notes

- Weather data updates every 10 minutes for free tier
- Search results are real-time
- All API calls are async for better performance
- Tools are automatically available to the LLM
- Error handling is built-in with informative messages

## 🎯 Next Steps

1. Test the tools with `python test_tools.py`
2. Integrate into your MCP client
3. Start the FastAPI server: `python main.py`
4. Make queries through your chat interface

## 📧 Support

If you encounter issues:
1. Check the logs in `mcp_client.log`
2. Verify API keys are correct
3. Test tools independently with `test_tools.py`
4. Check API documentation:
   - OpenWeatherMap: https://openweathermap.org/api
   - Serper: https://serper.dev/docs

Enjoy your enhanced MCP server with weather and web search capabilities! 🎉

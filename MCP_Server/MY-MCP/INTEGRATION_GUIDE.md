# 🔗 Integration Guide: Weather & Search Tools with Your MCP Server

## 📍 Your Current Setup

### MCP Server Location
```
D:\Learning\Genrative_AI\MCP_Server\MCP_Server\MCP_File_Manager.py
```

### Your API Client Location
```
D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api\
```

## 🎯 How It All Works Together

```
┌─────────────────────────────────────────────────────────┐
│                    Your Architecture                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FastAPI (main.py)                                     │
│      ↓                                                  │
│  MCP Client (mcp_client.py) ←─ Connects to MCP Server │
│      ↓                                                  │
│  Gemini LLM                                            │
│      ↓                                                  │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │   MCP Tools     │         │  Custom Tools    │     │
│  │                 │         │                  │     │
│  │ - File Manager  │         │ - Weather Tool   │     │
│  │ - run_command   │         │ - Serper Search  │     │
│  │ - write_file    │         │                  │     │
│  │ - read_file     │         └──────────────────┘     │
│  │ - edit_file     │                                   │
│  │ - etc...        │                                   │
│  └─────────────────┘                                   │
│         ↓                            ↓                  │
│   MCP Server                    Direct API Calls       │
│   (MCP_File_Manager.py)        (OpenWeather, Serper)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Integration Steps

### Step 1: Update Your MCP Client Configuration

Edit: `D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api\main.py`

**Current (WRONG):**
```python
class Settings(BaseSettings):
    server_script_path: str = r"D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api\main.py"
```

**Corrected (RIGHT):**
```python
class Settings(BaseSettings):
    server_script_path: str = r"D:\Learning\Genrative_AI\MCP_Server\MCP_Server\MCP_File_Manager.py"
```

### Step 2: Install Dependencies

```bash
cd D:\Learning\Genrative_AI\MCP_Server\MY-MCP
pip install aiohttp
```

### Step 3: Add API Keys to .env

Edit: `D:\Learning\Genrative_AI\MCP_Server\MY-MCP\.env`

```env
# Existing
GEMINI_API_KEY=your_gemini_key

# Add these NEW keys:
OPENWEATHER_API_KEY=your_openweather_key_here
SERPER_API_KEY=your_serper_key_here
```

### Step 4: Replace MCP Client

```bash
cd D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api

# Backup original
copy mcp_client.py mcp_client_backup.py

# Use new version with tools
copy mcp_client_updated.py mcp_client.py
```

### Step 5: Test Everything

```bash
# Test the custom tools first
cd D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api
python test_tools.py

# Then start your server
python main.py
```

## 🧪 Test Your Setup

### Test 1: Check MCP Server Tools
```bash
curl http://localhost:8000/tools
```

You should see:
- ✅ MCP tools (run_command, write_file, read_file, etc.)
- ✅ Custom tools (get_weather, web_search, get_weather_forecast)

### Test 2: Try a Weather Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London?"}'
```

### Test 3: Try a File Operation Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "List all Python files in D:/Learning"}'
```

### Test 4: Try a Web Search Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Search for recent news about AI"}'
```

## 📊 What Tools You'll Have

### From MCP Server (MCP_File_Manager.py)
1. ✅ `run_command` - Execute system commands
2. ✅ `write_file` - Create/write files
3. ✅ `append_to_file` - Append to files
4. ✅ `read_file` - Read file contents
5. ✅ `list_files` - List directory contents
6. ✅ `open_in_vscode` - Open files in VS Code
7. ✅ `delete_text_from_file` - Delete text from files
8. ✅ `edit_file_at_position` - Precise file editing
9. ✅ `find_and_replace` - Find and replace text
10. ✅ `insert_at_line` - Insert text at specific lines

### From Custom Tools (New)
1. ✅ `get_weather` - Get current weather
2. ✅ `get_weather_forecast` - Get weather forecast
3. ✅ `web_search` - Search the web (Google)

**Total: 13 powerful tools!**

## 🎯 Example Queries That Now Work

### File Operations (Existing MCP Tools)
```
"Create a new Python file called app.py with a hello world function"
"Read the contents of D:/test.txt"
"List all files in my Learning folder"
"Open config.json in VS Code"
"Find and replace 'old_name' with 'new_name' in app.py"
```

### Weather Queries (New Custom Tool)
```
"What's the weather in London?"
"Give me the forecast for Tokyo"
"How hot is it in New York in Fahrenheit?"
"What's the temperature in Mumbai?"
```

### Web Search Queries (New Custom Tool)
```
"Search for Python tutorials"
"Find recent news about artificial intelligence"
"Search for restaurants in Paris"
"Find images of the Eiffel Tower"
"Look up latest tech news from this week"
```

### Combined Queries (Multiple Tools)
```
"Search for weather in Tokyo and save the result to weather.txt"
"Find Python tutorials and create a study plan file"
"Get the forecast for London and write it to forecast.txt"
```

## 🔧 Troubleshooting

### Issue: "Cannot connect to MCP server"
**Solution:** Check that `server_script_path` points to:
```python
r"D:\Learning\Genrative_AI\MCP_Server\MCP_Server\MCP_File_Manager.py"
```

### Issue: "Weather tool not working"
**Solution:** 
1. Verify `OPENWEATHER_API_KEY` in .env
2. Test with: `python api/test_tools.py`
3. Check logs in `api/mcp_client.log`

### Issue: "Search tool not working"
**Solution:**
1. Verify `SERPER_API_KEY` in .env
2. Check you have free searches remaining
3. Test independently with test_tools.py

### Issue: "Module 'aiohttp' not found"
**Solution:**
```bash
pip install aiohttp
```

### Issue: "No tools showing up"
**Solution:**
1. Make sure you replaced mcp_client.py with mcp_client_updated.py
2. Restart the FastAPI server
3. Check logs for errors

## 📝 File Structure After Integration

```
D:\Learning\Genrative_AI\MCP_Server\
│
├── MCP_Server\                          ← Your MCP Server
│   ├── MCP_File_Manager.py              ← Main server (File operations)
│   ├── MCP_Google_Auth.py               ← Google auth server
│   └── config.json                      ← Server config
│
└── MY-MCP\                              ← Your API Client
    ├── api\
    │   ├── main.py                      ← FastAPI app (UPDATE THIS!)
    │   ├── mcp_client.py                ← New version with tools
    │   ├── mcp_client_backup.py         ← Backup of original
    │   ├── test_tools.py                ← Test suite
    │   └── utils\
    │       ├── logger.py                ← Logging
    │       ├── weather_tool.py          ← Weather tool (NEW)
    │       └── serper_tool.py           ← Search tool (NEW)
    │
    ├── .env                             ← Add API keys here
    ├── QUICKSTART.md                    ← Quick setup guide
    └── TOOLS_README.md                  ← Full documentation
```

## ✅ Verification Checklist

Before starting your server, verify:

- [ ] `main.py` points to correct MCP server path
- [ ] `aiohttp` is installed
- [ ] API keys are in `.env` file
- [ ] `mcp_client.py` is replaced with updated version
- [ ] Test tools work: `python api/test_tools.py`

## 🎉 Success Indicators

When everything is working, you'll see:

1. **In logs:** "Available tools: 13 total"
2. **In logs:** "MCP tools: 10" 
3. **In logs:** "Custom tools: 3"
4. **Server starts** without errors
5. **Test queries** return results

## 🆘 Need Help?

1. Check `api/mcp_client.log` for detailed logs
2. Run `python api/test_tools.py` to test tools independently
3. Verify API keys are correct
4. Make sure MCP server path is correct in main.py

---

**Ready to go? Start here:**
```bash
cd D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api
python main.py
```

Then test: "What's the weather in London?"

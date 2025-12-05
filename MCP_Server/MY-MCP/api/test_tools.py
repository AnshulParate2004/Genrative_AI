"""
Example usage of Weather and Serper Search tools
Run this file to test the tools independently
"""

import asyncio
import os
from dotenv import load_dotenv
from utils.weather_tool import WeatherTool
from utils.serper_tool import SerperSearchTool

load_dotenv()


async def test_weather_tool():
    """Test weather tool"""
    print("\n" + "="*60)
    print("TESTING WEATHER TOOL")
    print("="*60)
    
    weather = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY"))
    
    # Test 1: Get current weather
    print("\n📍 Test 1: Current Weather for London")
    result = await weather.get_weather("London,UK", units="metric")
    formatted = weather.format_weather_response(result)
    print(formatted)
    
    # Test 2: Get weather for multiple cities
    print("\n📍 Test 2: Current Weather for New York")
    result = await weather.get_weather("New York,US", units="imperial")
    formatted = weather.format_weather_response(result)
    print(formatted)
    
    # Test 3: Get forecast
    print("\n📍 Test 3: 5-day Forecast for Paris")
    result = await weather.get_forecast("Paris,FR", units="metric", cnt=5)
    if "error" not in result:
        print(f"\nForecast for {result['location']}:")
        for forecast in result['forecasts'][:3]:  # Show first 3
            print(f"\n📅 {forecast['datetime']}")
            print(f"   🌡️ {forecast['temperature']}°C - {forecast['weather']}")
            print(f"   {forecast['description']}")
    else:
        print(f"Error: {result['error']}")


async def test_serper_tool():
    """Test Serper search tool"""
    print("\n" + "="*60)
    print("TESTING SERPER SEARCH TOOL")
    print("="*60)
    
    serper = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))
    
    # Test 1: Regular search
    print("\n🔍 Test 1: Regular Web Search")
    result = await serper.search("Python programming tutorials", num_results=5)
    formatted = serper.format_search_response(result, "search")
    print(formatted)
    
    # Test 2: News search
    print("\n📰 Test 2: News Search")
    result = await serper.search(
        "artificial intelligence",
        num_results=5,
        search_type="news",
        time_range="qdr:w"  # Last week
    )
    formatted = serper.format_search_response(result, "news")
    print(formatted)
    
    # Test 3: Places search
    print("\n📍 Test 3: Places Search")
    result = await serper.search(
        "restaurants near me",
        num_results=5,
        search_type="places",
        location="New York, NY"
    )
    formatted = serper.format_search_response(result, "places")
    print(formatted)
    
    # Test 4: Image search (just check if it works)
    print("\n🖼️ Test 4: Image Search")
    result = await serper.search(
        "sunset landscape",
        num_results=3,
        search_type="images"
    )
    if "error" not in result:
        print(f"Found {len(result.get('image_results', []))} images")
        for img in result.get('image_results', [])[:3]:
            print(f"  - {img['title']}: {img['image_url']}")
    else:
        print(f"Error: {result['error']}")


async def test_combined():
    """Test combining weather and search"""
    print("\n" + "="*60)
    print("TESTING COMBINED USAGE")
    print("="*60)
    
    weather = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY"))
    serper = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))
    
    # Get weather for a city
    print("\n📍 Getting weather for Tokyo...")
    weather_result = await weather.get_weather("Tokyo,JP", units="metric")
    print(weather.format_weather_response(weather_result))
    
    # Search for related news
    print("\n🔍 Searching for Tokyo weather news...")
    search_result = await serper.search(
        "Tokyo weather forecast",
        num_results=3,
        search_type="news"
    )
    print(serper.format_search_response(search_result, "news"))


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WEATHER AND SERPER TOOLS TEST SUITE")
    print("="*60)
    
    # Check API keys
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("⚠️ Warning: OPENWEATHER_API_KEY not found in .env")
        print("Get your free API key from: https://openweathermap.org/api")
    
    if not os.getenv("SERPER_API_KEY"):
        print("⚠️ Warning: SERPER_API_KEY not found in .env")
        print("Get your API key from: https://serper.dev/")
    
    # Run tests
    try:
        if os.getenv("OPENWEATHER_API_KEY"):
            await test_weather_tool()
        
        if os.getenv("SERPER_API_KEY"):
            await test_serper_tool()
        
        if os.getenv("OPENWEATHER_API_KEY") and os.getenv("SERPER_API_KEY"):
            await test_combined()
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

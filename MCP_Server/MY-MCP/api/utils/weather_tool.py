import aiohttp
from typing import Dict, Any
from utils.logger import logger


class WeatherTool:
    """Weather tool using OpenWeatherMap API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    async def get_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather for a location
        
        Args:
            location: City name, state code, country code (e.g., "London,UK" or "New York,US")
            units: Temperature units - "metric" (Celsius), "imperial" (Fahrenheit), or "standard" (Kelvin)
        
        Returns:
            Dictionary with weather information
        """
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract relevant weather information
                        weather_info = {
                            "location": f"{data['name']}, {data['sys']['country']}",
                            "temperature": data['main']['temp'],
                            "feels_like": data['main']['feels_like'],
                            "temp_min": data['main']['temp_min'],
                            "temp_max": data['main']['temp_max'],
                            "humidity": data['main']['humidity'],
                            "pressure": data['main']['pressure'],
                            "weather": data['weather'][0]['main'],
                            "description": data['weather'][0]['description'],
                            "wind_speed": data['wind']['speed'],
                            "clouds": data['clouds']['all'],
                            "units": units
                        }
                        
                        logger.info(f"Weather data retrieved for {location}")
                        return weather_info
                    
                    elif response.status == 404:
                        error_msg = f"Location '{location}' not found"
                        logger.error(error_msg)
                        return {"error": error_msg, "status_code": 404}
                    
                    elif response.status == 401:
                        error_msg = "Invalid API key"
                        logger.error(error_msg)
                        return {"error": error_msg, "status_code": 401}
                    
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("message", "Unknown error")
                        logger.error(f"Weather API error: {error_msg}")
                        return {"error": error_msg, "status_code": response.status}
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error getting weather: {e}")
            return {"error": f"Network error: {str(e)}"}
        
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {"error": f"Error: {str(e)}"}
    
    async def get_forecast(self, location: str, units: str = "metric", cnt: int = 5) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name, state code, country code
            units: Temperature units
            cnt: Number of forecast entries (max 40, each 3 hours apart)
        
        Returns:
            Dictionary with forecast information
        """
        try:
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units,
                "cnt": min(cnt, 40)  # API limit is 40
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(forecast_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        forecasts = []
                        for item in data['list']:
                            forecast = {
                                "datetime": item['dt_txt'],
                                "temperature": item['main']['temp'],
                                "feels_like": item['main']['feels_like'],
                                "weather": item['weather'][0]['main'],
                                "description": item['weather'][0]['description'],
                                "humidity": item['main']['humidity'],
                                "wind_speed": item['wind']['speed'],
                                "clouds": item['clouds']['all']
                            }
                            forecasts.append(forecast)
                        
                        forecast_info = {
                            "location": f"{data['city']['name']}, {data['city']['country']}",
                            "forecasts": forecasts,
                            "units": units
                        }
                        
                        logger.info(f"Forecast data retrieved for {location}")
                        return forecast_info
                    
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("message", "Unknown error")
                        logger.error(f"Forecast API error: {error_msg}")
                        return {"error": error_msg, "status_code": response.status}
                        
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return {"error": f"Error: {str(e)}"}
    
    def format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data into a readable string"""
        if "error" in weather_data:
            return f"Error: {weather_data['error']}"
        
        unit_symbol = "°C" if weather_data.get("units") == "metric" else "°F" if weather_data.get("units") == "imperial" else "K"
        
        return f"""Weather in {weather_data['location']}:
🌡️ Temperature: {weather_data['temperature']}{unit_symbol} (feels like {weather_data['feels_like']}{unit_symbol})
📊 Range: {weather_data['temp_min']}{unit_symbol} - {weather_data['temp_max']}{unit_symbol}
☁️ Conditions: {weather_data['weather']} - {weather_data['description']}
💧 Humidity: {weather_data['humidity']}%
🌬️ Wind Speed: {weather_data['wind_speed']} m/s
🌫️ Cloud Cover: {weather_data['clouds']}%
🔽 Pressure: {weather_data['pressure']} hPa"""


# Tool schema for MCP/LLM integration
WEATHER_TOOL_SCHEMA = {
    "name": "get_weather",
    "description": "Get current weather information for a specific location. Supports city names with optional country codes (e.g., 'London,UK', 'New York,US').",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, optionally with state/country code (e.g., 'London,UK' or 'Paris')"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial", "standard"],
                "description": "Temperature units: 'metric' for Celsius, 'imperial' for Fahrenheit, 'standard' for Kelvin",
                "default": "metric"
            }
        },
        "required": ["location"]
    }
}

FORECAST_TOOL_SCHEMA = {
    "name": "get_weather_forecast",
    "description": "Get weather forecast for a location (up to 5 days, 3-hour intervals)",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, optionally with state/country code"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial", "standard"],
                "description": "Temperature units",
                "default": "metric"
            },
            "cnt": {
                "type": "integer",
                "description": "Number of forecast entries (max 40, each 3 hours apart)",
                "default": 5,
                "minimum": 1,
                "maximum": 40
            }
        },
        "required": ["location"]
    }
}

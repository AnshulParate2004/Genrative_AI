import aiohttp
from typing import Dict, Any, List, Optional
from utils.logger import logger


class SerperSearchTool:
    """Web search tool using Serper API (Google Search API)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def search(
        self, 
        query: str, 
        num_results: int = 10,
        search_type: str = "search",
        location: Optional[str] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform a web search using Serper API
        
        Args:
            query: Search query string
            num_results: Number of results to return (default 10, max 100)
            search_type: Type of search - "search", "news", "images", "videos", "places", "shopping"
            location: Geographic location for search (e.g., "United States", "London, UK")
            time_range: Time range filter - "qdr:h" (hour), "qdr:d" (day), "qdr:w" (week), 
                       "qdr:m" (month), "qdr:y" (year)
        
        Returns:
            Dictionary with search results
        """
        try:
            # Construct endpoint based on search type
            endpoint = f"{self.base_url}/{search_type}"
            
            # Build request payload
            payload = {
                "q": query,
                "num": min(num_results, 100)  # API max is 100
            }
            
            if location:
                payload["location"] = location
            
            if time_range:
                payload["tbs"] = time_range
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=self.headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format results based on search type
                        if search_type == "search":
                            results = self._format_search_results(data)
                        elif search_type == "news":
                            results = self._format_news_results(data)
                        elif search_type == "images":
                            results = self._format_image_results(data)
                        elif search_type == "videos":
                            results = self._format_video_results(data)
                        elif search_type == "places":
                            results = self._format_places_results(data)
                        elif search_type == "shopping":
                            results = self._format_shopping_results(data)
                        else:
                            results = data
                        
                        logger.info(f"Search completed for query: {query}")
                        return results
                    
                    elif response.status == 401:
                        error_msg = "Invalid API key"
                        logger.error(error_msg)
                        return {"error": error_msg, "status_code": 401}
                    
                    elif response.status == 429:
                        error_msg = "Rate limit exceeded"
                        logger.error(error_msg)
                        return {"error": error_msg, "status_code": 429}
                    
                    else:
                        error_data = await response.text()
                        logger.error(f"Search API error: {error_data}")
                        return {"error": error_data, "status_code": response.status}
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error during search: {e}")
            return {"error": f"Network error: {str(e)}"}
        
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return {"error": f"Error: {str(e)}"}
    
    def _format_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format regular search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "answer_box": data.get("answerBox"),
            "knowledge_graph": data.get("knowledgeGraph"),
            "organic_results": []
        }
        
        for result in data.get("organic", []):
            results["organic_results"].append({
                "position": result.get("position"),
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "date": result.get("date")
            })
        
        # Add related searches
        results["related_searches"] = data.get("relatedSearches", [])
        
        return results
    
    def _format_news_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format news search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "news_results": []
        }
        
        for result in data.get("news", []):
            results["news_results"].append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "date": result.get("date"),
                "source": result.get("source"),
                "image_url": result.get("imageUrl")
            })
        
        return results
    
    def _format_image_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format image search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "image_results": []
        }
        
        for result in data.get("images", []):
            results["image_results"].append({
                "title": result.get("title"),
                "image_url": result.get("imageUrl"),
                "image_width": result.get("imageWidth"),
                "image_height": result.get("imageHeight"),
                "thumbnail_url": result.get("thumbnailUrl"),
                "source": result.get("source"),
                "link": result.get("link")
            })
        
        return results
    
    def _format_video_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format video search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "video_results": []
        }
        
        for result in data.get("videos", []):
            results["video_results"].append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "date": result.get("date"),
                "duration": result.get("duration"),
                "channel": result.get("channel"),
                "image_url": result.get("imageUrl")
            })
        
        return results
    
    def _format_places_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format places/local search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "places_results": []
        }
        
        for result in data.get("places", []):
            results["places_results"].append({
                "position": result.get("position"),
                "title": result.get("title"),
                "address": result.get("address"),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "rating": result.get("rating"),
                "reviews": result.get("ratingCount"),
                "category": result.get("category"),
                "phone_number": result.get("phoneNumber"),
                "website": result.get("website")
            })
        
        return results
    
    def _format_shopping_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format shopping search results"""
        results = {
            "search_parameters": data.get("searchParameters", {}),
            "shopping_results": []
        }
        
        for result in data.get("shopping", []):
            results["shopping_results"].append({
                "title": result.get("title"),
                "link": result.get("link"),
                "source": result.get("source"),
                "price": result.get("price"),
                "rating": result.get("rating"),
                "reviews": result.get("ratingCount"),
                "image_url": result.get("imageUrl"),
                "delivery": result.get("delivery")
            })
        
        return results
    
    def format_search_response(self, search_data: Dict[str, Any], search_type: str = "search") -> str:
        """Format search results into a readable string"""
        if "error" in search_data:
            return f"Error: {search_data['error']}"
        
        output = []
        
        # Handle different search types
        if search_type == "search":
            # Answer box
            if search_data.get("answer_box"):
                answer = search_data["answer_box"]
                output.append(f"📌 Quick Answer: {answer.get('answer', answer.get('snippet', ''))}\n")
            
            # Knowledge graph
            if search_data.get("knowledge_graph"):
                kg = search_data["knowledge_graph"]
                output.append(f"ℹ️ {kg.get('title', '')}: {kg.get('description', '')}\n")
            
            # Organic results
            output.append("🔍 Search Results:")
            for i, result in enumerate(search_data.get("organic_results", [])[:5], 1):
                output.append(f"\n{i}. {result['title']}")
                output.append(f"   {result['link']}")
                output.append(f"   {result.get('snippet', '')}")
        
        elif search_type == "news":
            output.append("📰 News Results:")
            for i, result in enumerate(search_data.get("news_results", [])[:5], 1):
                output.append(f"\n{i}. {result['title']}")
                output.append(f"   Source: {result.get('source', 'Unknown')}")
                output.append(f"   Date: {result.get('date', 'N/A')}")
                output.append(f"   {result['link']}")
        
        elif search_type == "places":
            output.append("📍 Places Results:")
            for i, result in enumerate(search_data.get("places_results", [])[:5], 1):
                rating_str = f"⭐ {result.get('rating', 'N/A')} ({result.get('reviews', 0)} reviews)" if result.get('rating') else ""
                output.append(f"\n{i}. {result['title']}")
                output.append(f"   {result.get('address', 'N/A')}")
                output.append(f"   {rating_str}")
        
        return "\n".join(output)


# Tool schemas for MCP/LLM integration
SERPER_SEARCH_TOOL_SCHEMA = {
    "name": "web_search",
    "description": "Search the web using Google Search API. Supports regular search, news, images, videos, places, and shopping.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (1-100)",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            },
            "search_type": {
                "type": "string",
                "enum": ["search", "news", "images", "videos", "places", "shopping"],
                "description": "Type of search to perform",
                "default": "search"
            },
            "location": {
                "type": "string",
                "description": "Geographic location for search (e.g., 'United States', 'London, UK')"
            },
            "time_range": {
                "type": "string",
                "enum": ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"],
                "description": "Time range filter: qdr:h (hour), qdr:d (day), qdr:w (week), qdr:m (month), qdr:y (year)"
            }
        },
        "required": ["query"]
    }
}

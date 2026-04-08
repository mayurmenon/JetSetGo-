import asyncio
from typing import List, Dict, Any
from autogen import AssistantAgent
from app.core.tools import run_tinyfish_scrape
from app.core.config import settings

class TravelSpecialistFactory:
    """Creates travel-specific specialist agents."""
    
    def __init__(self):
        self.llm_config = {
            "config_list": [{"model": "gpt-4", "api_key": settings.OPENAI_API_KEY or ""}]
        }
    
    def _create_flight_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="FlightSearchSpecialist",
            system_message="""You are a flight search specialist. Use TinyFish to navigate to Google Flights and find the best flight options.
                Extract: airline, departure time, arrival time, price, layover count and duration.
                Return as JSON array of flight options. Be thorough and find at least 3-5 options.""",
            llm_config=self.llm_config
        )
    
    def _create_hotel_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="HotelSearchSpecialist",
            system_message="""You are a hotel search specialist. Use TinyFish to search Booking.com for accommodations.
                Extract: hotel name, nightly price, rating (out of 10), distance to city center, and brief description.
                Filter by the budget level provided. Return as JSON array of 5-8 hotel options.""",
            llm_config=self.llm_config
        )
    
    def _create_attractions_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="LocalAttractionsSpecialist",
            system_message="""You are a local experiences specialist. Use TinyFish to find top-rated attractions, tours, and restaurants.
                Extract: name, category, estimated cost, and a one-sentence description.
                Return as JSON array of 8-10 recommendations.""",
            llm_config=self.llm_config
        )
    
    def _create_weather_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="WeatherSafetySpecialist",
            system_message="""You are a travel logistics agent. Use TinyFish to scrape weather forecasts and travel advisories.
                Extract: daily forecast for travel dates, temperature ranges, precipitation chance, and any safety warnings.
                Return as JSON object with weather summary and alerts.""",
            llm_config=self.llm_config
        )
    
    async def dispatch_specialists(self, destination: str, dates: Dict[str, str], budget: str, origin: str = None) -> Dict[str, Any]:
        """Run all specialists in parallel and return combined results."""
        agents = {
            "flights": self._create_flight_agent(),
            "hotels": self._create_hotel_agent(),
            "attractions": self._create_attractions_agent(),
            "weather": self._create_weather_agent()
        }
        
        # Construct search URLs for each specialist (these will be passed in context)
        tasks = []
        # In practice, you'd use the TinyFishTool directly within agent conversations
        # For brevity, we'll stub the parallel execution here
        
        # Return combined results from all agents
        return {"flights": [], "hotels": [], "attractions": [], "weather": {}}

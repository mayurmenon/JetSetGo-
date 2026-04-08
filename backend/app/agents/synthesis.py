from autogen import AssistantAgent
from app.core.config import settings

class SynthesisAgent:
    def __init__(self):
        self.llm_config = {
            "config_list": [{"model": "gpt-4", "api_key": settings.OPENAI_API_KEY or ""}]
        }
        self.agent = AssistantAgent(
            name="TravelSynthesizer",
            system_message="""You are an expert travel planner. Given flight options, hotel listings, attractions, and weather data,
                create a detailed day-by-day itinerary in Markdown format.
                
                Include:
                - A brief overview of the destination
                - Recommended flight (choose the best option)
                - Recommended hotel (based on budget)
                - Day-by-day plan with morning, afternoon, and evening activities
                - Weather considerations and packing tips
                - Total estimated cost breakdown
                
                Format beautifully with headings, bullet points, and emojis for readability.""",
            llm_config=self.llm_config
        )
    
    async def synthesize(self, validated_data: dict) -> str:
        # In a full implementation, this would call the agent with the data
        # For now, return a placeholder that we'll wire up with actual agent calls
        return "# Your Travel Itinerary\n\n*Itinerary will be generated here...*"

import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

# Set Groq API Key
os.environ["GROQ_API_KEY"] = "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"

# Agent for Flight Search
flight_agent = Agent(
    name="Flight Agent",
    role="Search for flights based on user preferences",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=["Find flights based on user input, include airlines, prices, and timings."],
    show_tool_calls=True,
    markdown=True,
)
# Agent for Hotel Booking
hotel_agent = Agent(
    name="Hotel Agent",
    role="Search for hotels based on location and budget",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=["Find hotels near the destination with user-specified amenities and budget."],
    show_tool_calls=True,
    markdown=True,
)
# Agent for Car Rentals
car_rental_agent = Agent(
    name="Car Rental Agent",
    role="Search for car rental options at the destination",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=["Provide car rental options with pricing and availability."],
    show_tool_calls=True,
    markdown=True,
)
places_agent = Agent(
    name="Places Agent",
    role="Recommend places and activities to visit based on the destination",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=[
        "Research the best places to visit at the given destination, including cultural sites, natural attractions, and local experiences."
    ],
    show_tool_calls=True,
    markdown=True,
)
# Combine agents into a team
travel_planner_team = Agent(
    team=[flight_agent, hotel_agent, car_rental_agent,places_agent],
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=[
        "Coordinate between agents to provide a complete travel plan.",
        "Avoid repeating information from other agents.",
        "Ensure all agents contribute unique insights."],
    show_tool_calls=True,
    markdown=True,
)
# Run the multi-agent system
if __name__ == "__main__":
    travel_planner_team.print_response(
        "Plan a trip from Delhi to kerala, departing on April 15th and returning on April 22nd. Include flights, hotels and car rentals."
    )

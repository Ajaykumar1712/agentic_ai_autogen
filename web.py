import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

# Step 1: Set the Groq API key as an environment variable
os.environ["GROQ_API_KEY"] = "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"

# Step 2: Define the Web Agent using Groq's Llama 3.3 model
web_agent = Agent(
    name="Web Agent",
    model=Groq(id="llama3-8b-8192"),  # Use a valid model ID (check Groq documentation for supported IDs)
    tools=[DuckDuckGo()],  # Add DuckDuckGo as a tool for web searches
    instructions=["Always include sources"],  # Ensure responses include citations
    show_tool_calls=True,  # Display tool calls for transparency
    markdown=True,  # Enable Markdown formatting for responses
)

# Step 3: Query the Web Agent and stream the response
try:
    response = web_agent.print_response("What's happening in France?", stream=True)
    print(response)
except Exception as e:
    print(f"Error: {e}")

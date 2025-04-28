from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv

agent = Agent(model=Groq(id="deepseek-r1-distill-llama-70b"))

agent.print_response("How are you?")

from phi.tools.youtube_tools import YouTubeTools

Youtube_agent = Agent(
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[YouTubeTools()],
    show_tool_calls=True,
    description="You are a YouTube agent. Obtain the details of a YouTube video and answer questions.",
)

Youtube_agent.print_response("Summarize this video https://youtu.be/ONMftqeKZRE?si=7KcALk8QFqlajizh and provide recently posted video from the channel", markdown=True)

from phi.tools.googlesearch import GoogleSearch

web_agent = Agent(
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[GoogleSearch()],
    description="You are a news agent that helps users find the latest news.",
    instructions=[
        "Given the channel name by the user, provide latest information about the channel.",
        "Search for 10 news items and select the top 4 unique items.",
        "Search in English and in Tamil.",
    ],
    show_tool_calls=True,
    #debug_mode=True,
)
agent.print_response("Karthik's Show", markdown=True)

team_Agents = Agent(
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    team=[Youtube_agent,web_agent],
    instruction = ("Summarise the video based on the URL provided by the user and gather latest information about the channel"),
    show_tool_calls = True,
)

team_Agents.print_response("Summarize this video https://youtu.be/ONMftqeKZRE?si=7KcALk8QFqlajizh and provide latest information about Karthik's Show channel")
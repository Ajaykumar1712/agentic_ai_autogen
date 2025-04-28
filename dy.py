from autogen import AssistantAgent # Assuming use of AutoGen library
import os
import sys
import logging

# --- Configuration (API Key, LLM Config - Keep as before) ---
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    api_key = "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" # Replace if needed for testing

if not api_key or api_key == "YOUR_GROQ_API_KEY":
    print("Error: GROQ_API_KEY environment variable not set.")
    sys.exit(1)

config_list = [{"model": "llama3-70b-8192", "api_key": api_key, "api_type": "groq"}]
llm_config = {"config_list": config_list, "temperature": 0.6, "timeout": 120}

def create_task_specific_agent(task_description, goal, constraints=None, output_format=None, agent_name="dynamic_agent"):
    """Dynamically creates an agent with a tailored system message."""

    # Start building the system message
    system_message = f"You are an AI assistant responsible for: {task_description}.\n"
    system_message += f"Your primary goal is: {goal}.\n"

    # Add optional constraints
    if constraints:
        system_message += f"You must adhere to the following constraints: {constraints}.\n"

    # Specify output format if needed
    if output_format:
        system_message += f"Ensure your final output is in {output_format} format.\n"

    # Add general instructions
    system_message += "Be precise, efficient, and focus only on the assigned task."

    print(f"--- Generated System Message for {agent_name} ---")
    print(system_message)
    print("-------------------------------------------------")

    # Create the agent instance
    agent = AssistantAgent(
        name=agent_name,
        system_message=system_message,
        llm_config=llm_config
    )
    return agent

# --- Example Usage ---

# # Example 1: Quiz Question Fetcher
# quiz_task = "fetching multiple-choice quiz questions about World War II"
# quiz_goal = "retrieve 5 distinct questions with 4 options each, clearly marking the correct answer"
# quiz_constraints = "Questions must be suitable for a high-school level audience. Avoid overly obscure facts."
# quiz_agent = create_task_specific_agent(quiz_task, quiz_goal, quiz_constraints, agent_name="quiz_agent")

# # Example 2: Data Scraper
# scrape_task = "scraping product names and prices from a specific e-commerce category page"
# scrape_goal = "extract the name and price for every product listed on the page"
# scrape_format = "JSON list of objects, where each object has 'name' and 'price' keys"
# scrape_agent = create_task_specific_agent(scrape_task, scrape_goal, output_format=scrape_format, agent_name="scraper_agent")

# Example 3: Summarizer
summary_task = '''Go to "https://www.artificialintelligence-news.com" and summarize the news '''
summary_goal = "produce a concise summary of no more than 100 words, capturing the main points"
summary_agent = create_task_specific_agent(summary_task, summary_goal, agent_name="summarizer_agent")
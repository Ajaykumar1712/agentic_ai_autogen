import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
import sys 

api_key = os.environ.get("GROQ_API_KEY", "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") 

if not api_key or api_key == "YOUR_GROQ_API_KEY":
    print("Error: GROQ_API_KEY environment variable not set.")
    print("Please set it before running the script:")
    print("export GROQ_API_KEY='your-actual-api-key'")
    sys.exit(1) # Exit if the key is not set

config_list = [{
    "model": "llama3-70b-8192", # Common identifier for Llama 3 70B on Groq
    "api_key": api_key,
    "api_type": "groq"
}]

# LLM configuration for agents
llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "timeout": 120, # Increased timeout for potentially longer responses
}

# --- Agent Definitions ---

quiz_agent = autogen.AssistantAgent(
    name="Quiz_Creator", 
    system_message="You are responsible for creating quiz questions on a given topic. For each round, provide ONE clear multiple-choice or short-answer question. Also provide a hint if the user asks for one, and the correct answer with a brief explanation AFTER the user has attempted the question and it has been evaluated.",
    llm_config=llm_config
)

evaluation_agent = autogen.AssistantAgent(
    name="Evaluator",
    system_message="You evaluate the user's answer to the quiz question provided by the Quiz_Creator. Determine if the answer is correct, partially correct, or incorrect. Provide a concise assessment (e.g., 'Correct!', 'Incorrect.', 'Partially Correct.'). Do not reveal the correct answer yourself; wait for the Quiz_Creator or Mentor.",
    llm_config=llm_config
)

mentor_agent = autogen.AssistantAgent(
    name="Mentor",
    system_message="After the Evaluator assesses the user's answer, you provide feedback and guidance based on the evaluation result and the user's answer. If the answer was incorrect or partially correct, explain the underlying concepts clearly. Offer tips for improvement and encourage learning. You can refer to the correct answer/explanation provided by the Quiz_Creator if needed.",
    llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="User", 
    human_input_mode="ALWAYS", # Prompt user for input every time this agent is selected
    # max_consecutive_auto_reply=3, # Keep this if you want some potential auto-replies, but ALWAYS mode makes it less relevant here. Can be removed or set to 0.
    max_consecutive_auto_reply=0, # Set to 0 to ensure user is always prompted when it's their turn.
    code_execution_config=False, # Disable code execution if not needed
    # Check for "TERMINATE" (case-insensitive) and strip whitespace
    is_termination_msg=lambda x: x.get("content", "").strip().upper() == "TERMINATE", 
    system_message="You are the student taking the quiz. Respond to the questions, ask for hints if needed, or type TERMINATE to end the session."
)


groupchat = GroupChat(
    agents=[user_proxy, quiz_agent, evaluation_agent, mentor_agent], 
    messages=[], 
    max_round=20
)

# It's often helpful to define speaker selection logic, but GroupChatManager's default round-robin can work for this setup.
# For more complex flows, consider `speaker_selection_method`.
chat_manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# --- Start the Chat ---

print("Starting the Basic Math Quiz Chat!")
print("Type 'TERMINATE' when you want to end the session.")

# Initiate the chat ONCE. 
# The user_proxy will prompt for input when necessary due to human_input_mode="ALWAYS".
user_proxy.initiate_chat(
    recipient=chat_manager,
    message="Test me on basic python programming language " # More specific initial topic
)

# --- End of Script ---
# The chat interaction is now handled within the initiate_chat call.
# No need for the manual while loop.
print("Chat session finished.") 
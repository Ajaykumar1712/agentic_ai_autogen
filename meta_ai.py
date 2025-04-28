import os
import autogen
import json # Needed for potential parsing if LLM adds extras
import sys
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    api_key = "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" # Replace if needed for testing

if not api_key or api_key == "YOUR_GROQ_API_KEY":
    print("Error: GROQ_API_KEY environment variable not set.")
    sys.exit(1)

config_list = [{"model": "llama3-70b-8192", "api_key": api_key, "api_type": "groq"}]
llm_config = {"config_list": config_list, "temperature": 0.6, "timeout": 120}
# Check if config_list is loaded correctly
if not config_list:
    raise ValueError("LLM configuration not found or empty. Please configure OAI_CONFIG_LIST or set the config_list manually.")


# Shared LLM configuration for all agents
llm_config = {
    "timeout": 600,
    "cache_seed": 42, # Use None for no caching
    "config_list": config_list,
    "temperature": 0,
}
# --- Meta-Prompting Function ---
def generate_system_message_with_autogen(high_level_task_description: str) -> str:
    """
    Uses a temporary AutoGen AssistantAgent (acting as a meta-agent)
    to generate a detailed system message for a worker agent.
    Relies entirely on the LLM configured in config_list.
    """
    print(f"\n--- Generating System Message via AutoGen Meta-Agent for task: '{high_level_task_description}' ---")

    meta_system_prompt = """You are an expert AI agent prompt engineer. Your sole task is to generate a comprehensive and effective system message for another AI agent (a 'worker agent'), based ONLY on the high-level task description provided in the user message.

The generated system message should:
1. Clearly define the worker agent's persona and role (e.g., "You are a helpful AI assistant specialized in...").
2. State the specific task the worker agent needs to perform, derived *directly* from the provided description.
3. Detail the primary goal or objective based on the description.
4. Include general best practices like "Think step-by-step" and "Be precise".
5. Specify the desired output format ONLY IF clearly implied or stated in the high-level task description.
6. **Crucially, instruct the worker agent to end its absolute final response, after completing the entire task, with the single word: TERMINATE**

Your output MUST ONLY be the system message text for the worker agent. Do NOT include any introductory phrases, explanations, or conversational text like "Here is the system message:". Just output the message itself, ready to be used.
"""

    # Create a temporary agent specifically for generating the prompt
    prompt_engineer_agent = autogen.AssistantAgent(
        name="Prompt_Engineer",
        system_message=meta_system_prompt,
        llm_config=llm_config.copy(), # Use the main config
    )

    # Create a temporary user proxy to send the task description and get the result
    # This proxy will not ask for human input and terminates after one exchange
    meta_user_proxy = autogen.UserProxyAgent(
        name="Meta_User_Proxy",
        human_input_mode="NEVER", # No human interaction needed for this step
        max_consecutive_auto_reply=0, # We only want the engineer's direct response
        code_execution_config=False, # No code execution needed
        llm_config=False, # This agent doesn't need to run generation itself
        default_auto_reply="Error: No response generated.", # Fallback message
    )

    try:
        # Initiate a chat for a single turn: User Proxy -> Prompt Engineer
        print("Sending task description to Prompt_Engineer agent...")
        meta_user_proxy.initiate_chat(
            recipient=prompt_engineer_agent,
            message=high_level_task_description,
            max_turns=1, # Ensure only one round-trip (User -> Assistant)
            clear_history=True,
            request_reply=True, # Explicitly request a reply
            silent=False # Show the interaction for debugging
        )

        # Extract the last message received by the meta_user_proxy, which should be the generated prompt
        last_msg = meta_user_proxy.last_message(prompt_engineer_agent)
        if last_msg and isinstance(last_msg, dict) and last_msg.get("content"):
             generated_message = last_msg["content"].strip()
             print("\n--- Received Response from Prompt_Engineer ---")
             # print(generated_message) # Print raw message for debug if needed
        else:
            # Attempt to get message from conversation history if direct last_message failed
            chat_messages = meta_user_proxy.chat_messages.get(prompt_engineer_agent.name, [])
            if chat_messages and chat_messages[-1].get("role") == "assistant":
                generated_message = chat_messages[-1]["content"].strip()
                print("\n--- Received Response from Prompt_Engineer (via history) ---")
            else:
                 raise ValueError("Failed to retrieve a valid response from the Prompt_Engineer agent.")


        # --- Validation ---
        if not generated_message:
            raise ValueError("Prompt_Engineer agent response for system message was empty.")
        if "TERMINATE" not in generated_message:
             print("\nWarning: Generated system message might be missing the 'TERMINATE' instruction. Appending manually.")
             # Append it manually if missing - crucial for workflow
             generated_message += "\n\nIMPORTANT: When the task is fully complete, end your final message with the single word: TERMINATE"
        # --- End Validation ---

        # Clean up potential introductory text if the LLM didn't follow instructions perfectly
        # (More robust parsing might be needed depending on the LLM's compliance)
        if "system message:" in generated_message.lower():
            generated_message = generated_message.split(":", 1)[-1].strip()


        print("\n--- Successfully Generated System Message ---")
        print(generated_message)
        print("-" * 45)
        return generated_message

    except Exception as e:
        print(f"\nError during AutoGen meta-prompting: {e}")
        import traceback
        traceback.print_exc()
        # Clean up temporary agents if needed (though usually garbage collection handles it)
        del prompt_engineer_agent
        del meta_user_proxy
        raise ValueError("Failed to generate system message using AutoGen meta-agent.") from e


# --- Main Execution Block (Worker Agent uses the same llm_config) ---
if __name__ == "__main__":
    print("--- Meta-Prompting (via AutoGen Agent) for Dynamic Configuration ---")
    print("Describe the high-level task for the AI agent.")

    # 1. Get High-Level Task from User
    task_desc_high_level = input("Enter the high-level task description:\n> ")

    if not task_desc_high_level.strip():
        print("\nError: High-level task description cannot be empty. Exiting.")
        exit()

    try:
        # 2. Generate System Message using AutoGen Meta-Agent
        worker_system_message = generate_system_message_with_autogen(task_desc_high_level)

        # 3. Get Agent Name
        agent_name_input = input("\nEnter a name for this worker agent (e.g., 'researcher', 'summarizer') (press Enter for 'worker_agent'):\n> ")
        worker_agent_name = agent_name_input.strip() if agent_name_input.strip() else "worker_agent"

        # 4. Create the Worker Agent using the generated message
        print(f"\nCreating worker agent '{worker_agent_name}'...")
        # Use a slightly different llm_config if needed (e.g., lower temperature for worker)
        worker_llm_config = llm_config.copy()
        worker_llm_config['temperature'] = 0 # Worker usually better with low temp

        worker_agent = autogen.AssistantAgent(
            name=worker_agent_name,
            system_message=worker_system_message,
            llm_config=worker_llm_config, # Use the potentially adjusted config
        )
        print(f"Successfully created worker agent: '{worker_agent.name}'")


        # 5. Setup User Proxy Agent (for the main chat)
        print("\nSetting up User Proxy Agent for main chat...")
        user_proxy = autogen.UserProxyAgent(
           name="User_Proxy",
           system_message="A human user providing initial instructions and feedback.",
           code_execution_config={
               "work_dir": "coding",
               "use_docker": False
            },
           human_input_mode="TERMINATE",
           max_consecutive_auto_reply=5,
           is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE")
        )

        # 6. Initiate a Direct Chat with the worker agent
        print("\n--- Starting Direct Chat with Dynamically Configured Agent ---")
        print(f"You will now chat directly with '{worker_agent.name}'. Type 'exit' to end the chat prematurely.")

        initial_message = input("\nEnter the specific initial instruction or starting point for the worker agent:\n> ")

        if not initial_message or initial_message.lower() == 'exit':
             print("No initial message provided or exit command given. Chat not started.")
        else:
            user_proxy.initiate_chat(
                recipient=worker_agent,
                message=initial_message,
                clear_history=True
            )

        print("\n--- Direct Chat Ended ---")

    except ValueError as ve:
        print(f"\nConfiguration or Execution Error: {ve}")
    except ImportError as ie:
        print(f"\nImport Error: {ie}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
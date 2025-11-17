from pydantic_ai import Agent
from dotenv import load_dotenv
import logfire
import os
import asyncio

load_dotenv()

# Configure Logfire
logfire.configure(
    token=os.environ["LOGFIRE_WRITE_TOKEN"],
    environment=os.environ["ENVIRONMENT"],
    service_name=os.environ["SERVICE_NAME"],
)
logfire.instrument_pydantic_ai()

model = "gemini-2.5-flash"
agent = Agent(
    model,
    system_prompt=(
        "You are a helpful and friendly assistant. Engage in natural conversation "
        "with users, answer their questions, and provide assistance on various topics. "
        "Be conversational, helpful, and concise in your responses."
    )
)

async def run_agent_with_logging(user_input: str, message_history: list):
    """Run the agent with Logfire logging for input and output."""
    with logfire.span('agent_interaction'):
        # Log user input
        logfire.info('User input received', user_input=user_input)
        
        # Run the agent with message history
        result = await agent.run(user_input, message_history=message_history)
        
        # Log agent output
        logfire.info('Agent output generated', agent_output=str(result.output))
        
    return result

async def main():
    message_history = []  # Initialize empty message history
    
    print("Chat with the agent (type 'exit', 'quit', or 'bye' to end)")
    print("-" * 60)
    
    while True:
        user_message = await asyncio.to_thread(input, "You: ")
        
        if user_message.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Run agent with logging
        result = await run_agent_with_logging(user_message, message_history)
        print(f"Agent: {result.output}")
        
        # Update message history with new messages from this run
        message_history = result.all_messages()

# if __name__ == "__main__":
#     asyncio.run(main())
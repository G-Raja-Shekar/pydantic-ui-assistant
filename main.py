from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import logfire
import os
import asyncio
import json
from typing import Any

load_dotenv()

# Configure Logfire
logfire.configure(
    token=os.environ["LOGFIRE_WRITE_TOKEN"],
    environment=os.environ["ENVIRONMENT"],
    service_name=os.environ["SERVICE_NAME"],
)
logfire.instrument_pydantic_ai()

# Available products (same as in UI)
AVAILABLE_PRODUCTS = [
    {"name": "Salt", "price": 2.50, "emoji": "🧂"},
    {"name": "Pepper", "price": 3.00, "emoji": "🌶️"},
    {"name": "Toothpaste", "price": 4.99, "emoji": "🦷"},
    {"name": "Toothbrush", "price": 3.50, "emoji": "🪥"},
    {"name": "Detergent", "price": 8.99, "emoji": "🧴"},
    {"name": "Soap", "price": 2.99, "emoji": "🧼"},
    {"name": "Shampoo", "price": 6.99, "emoji": "🧴"},
    {"name": "Paper Towels", "price": 5.49, "emoji": "🧻"},
]

async def manage_cart(ctx: RunContext[Any], product_name: str, action: str, quantity: int = 1) -> str:
    """
    Manage shopping cart - add, remove, or update product quantity.
    
    Args:
        ctx: The run context from pydantic-ai
        product_name: The name of the product
        action: Action to perform - 'add', 'remove', or 'update'
        quantity: Quantity to add or set (default: 1)
        
    Returns:
        JSON string with cart action details
    """
    with logfire.span('manage_cart', product_name=product_name, action=action):
        # Find product
        product = next(
            (p for p in AVAILABLE_PRODUCTS if p["name"].lower() == product_name.lower()),
            None
        )
        
        if not product and action != 'remove':
            logfire.warn('Product not found', product_name=product_name)
            available = ', '.join([p['name'] for p in AVAILABLE_PRODUCTS])
            return f"Sorry, '{product_name}' is not available. Available: {available}"
        
        logfire.info('Cart action', product=product_name, action=action, quantity=quantity)
        
        # Return structured response
        return json.dumps({
            "action": action,
            "product": product["name"] if product else product_name,
            "quantity": quantity,
            "price": product["price"] if product else 0,
            "emoji": product["emoji"] if product else ""
        })

model = "gemini-2.5-flash"
agent = Agent(
    model,
    tools=[manage_cart],
    system_prompt=(
        "You are a helpful shopping assistant. Use the manage_cart tool for all cart operations:\n"
        "- action='add' to add products (quantity defaults to 1)\n"
        "- action='remove' to remove products from cart\n"
        "- action='update' with quantity parameter to set specific quantity\n"
        "Available products: Salt, Pepper, Toothpaste, Toothbrush, Detergent, Soap, Shampoo, Paper Towels.\n"
        "Be friendly and conversational in responses."
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
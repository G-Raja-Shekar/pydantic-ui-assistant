from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import logfire
import os
import asyncio
import httpx
from typing import Any

load_dotenv()

# Configure Logfire
logfire.configure(
    token=os.environ["LOGFIRE_WRITE_TOKEN"],
    environment=os.environ["ENVIRONMENT"],
    service_name=os.environ["SERVICE_NAME"],
)
logfire.instrument_pydantic_ai()

# Research tool function
async def research_topic(ctx: RunContext[Any], topic: str) -> str:
    """
    Research a topic using web search or knowledge retrieval.
    
    Args:
        ctx: The run context from pydantic-ai
        topic: The topic to research
        
    Returns:
        Research findings as a string
    """
    with logfire.span('research_topic', topic=topic):
        logfire.info('Starting research', topic=topic)
        
        try:
            # Example using DuckDuckGo Instant Answer API (free, no API key needed)
            async with httpx.AsyncClient(follow_redirects=False) as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": topic,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1",
                        "no_redirect": "1"
                    },
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # print(data, "DAAATA")
                    # Compile research results
                    results = []
                    
                    if data.get("AbstractText"):
                        results.append(f"Summary: {data['AbstractText']}")
                    
                    if data.get("Definition"):
                        results.append(f"Definition: {data['Definition']}")
                    
                    if data.get("RelatedTopics"):
                        related = [
                            item.get("Text", "") 
                            for item in data["RelatedTopics"][:5] 
                            if isinstance(item, dict) and item.get("Text")
                        ]
                        if related:
                            related_info = "Related Information:\n" + "\n- ".join([""] + related)
                            results.append(related_info)
                    
                    if results:
                        research_output = f"Research findings for '{topic}':\n\n" + "\n\n".join(results)
                    else:
                        research_output = f"Limited information found for '{topic}' via DuckDuckGo Instant Answer API. The API may not have detailed information on this topic. Try rephrasing or searching for more general/specific terms."
                    
                    logfire.info('Research completed', findings_length=len(research_output))
                    return research_output
                elif response.status_code == 301 or response.status_code == 302:
                    error_msg = f"DuckDuckGo API returned redirect (status {response.status_code}). This usually means no instant answer is available for '{topic}'. Try a more general query or a well-known topic."
                    logfire.warn('Research redirect', error=error_msg, redirect_location=response.headers.get('location'))
                    return error_msg
                else:
                    error_msg = f"Research API returned status code: {response.status_code}. Response: {response.text[:200]}"
                    logfire.error('Research failed', error=error_msg)
                    return error_msg
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error during research: {str(e)}"
            logfire.error('Research HTTP exception', error=error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error during research: {str(e)}"
            logfire.error('Research exception', error=error_msg)
            return error_msg

model = "gemini-2.5-flash"
agent = Agent(
    model,
    tools=[research_topic],
    system_prompt=(
        "You are a helpful research assistant. When users ask you to research topics, "
        "use the research_topic tool to gather information. Provide comprehensive, "
        "well-structured answers based on the research findings."
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

if __name__ == "__main__":
    asyncio.run(main())

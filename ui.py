from fasthtml.common import *
import asyncio
from main import run_agent_with_logging

app, rt = fast_app()

# Store messages in memory
messages = []

# Store agent message history
agent_message_history = []

# Shopping cart - stores {product_name: quantity}
cart = {}

# Available products
products = [
    {"name": "Salt", "price": 2.50, "emoji": "🧂"},
    {"name": "Pepper", "price": 3.00, "emoji": "🌶️"},
    {"name": "Toothpaste", "price": 4.99, "emoji": "🦷"},
    {"name": "Toothbrush", "price": 3.50, "emoji": "🪥"},
    {"name": "Detergent", "price": 8.99, "emoji": "🧴"},
    {"name": "Soap", "price": 2.99, "emoji": "🧼"},
    {"name": "Shampoo", "price": 6.99, "emoji": "🧴"},
    {"name": "Paper Towels", "price": 5.49, "emoji": "🧻"},
]

def ProductCard(name, price, emoji):
    """Create a product card"""
    return Div(
        Div(emoji, style="font-size: 40px; margin-bottom: 10px;"),
        Div(name, style="font-weight: bold; font-size: 16px; margin-bottom: 5px;"),
        Div(f"${price:.2f}", style="color: #667eea; font-size: 14px;"),
        style="""
            background: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        """,
        onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'",
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'"
    )

def CartItem(name, price, emoji, quantity):
    """Create a cart item card with quantity controls"""
    return Div(
        Div(
            Div(emoji, style="font-size: 30px;"),
            Div(
                Div(name, style="font-weight: bold; font-size: 14px;"),
                Div(f"${price:.2f}", style="color: #667eea; font-size: 12px;"),
                style="flex: 1; text-align: left; margin-left: 10px;"
            ),
            style="display: flex; align-items: center; margin-bottom: 10px;"
        ),
        Div(
            Button("-", 
                hx_post=f"/cart/decrease/{name}",
                hx_target="#cart-items",
                hx_swap="innerHTML",
                style="padding: 5px 10px; background: #f0f0f0; border: none; border-radius: 5px; cursor: pointer;"
            ),
            Span(str(quantity), style="margin: 0 10px; font-weight: bold;"),
            Button("+",
                hx_post=f"/cart/increase/{name}",
                hx_target="#cart-items",
                hx_swap="innerHTML",
                style="padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;"
            ),
            style="display: flex; align-items: center; justify-content: center;"
        ),
        style="""
            background: white;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        """
    )

def ChatMessage(text, is_user=False):
    """Create a chat bubble"""
    alignment = "flex-end" if is_user else "flex-start"
    bg_color = "#667eea" if is_user else "#f0f0f0"
    text_color = "white" if is_user else "#333"
    border_radius = "18px 18px 4px 18px" if is_user else "18px 18px 18px 4px"
    
    return Div(
        text,
        style=f"""
            max-width: 70%;
            padding: 12px 16px;
            border-radius: {border_radius};
            background: {bg_color};
            color: {text_color};
            word-wrap: break-word;
            align-self: {alignment};
            margin-bottom: 10px;
            animation: fadeIn 0.3s;
        """
    )

@rt("/")
def get():
    """Main chat page"""
    return Html(
        Head(
            Title("E-Commerce Assistant"),
            Style("""
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                
                .main-container {
                    display: flex;
                    gap: 20px;
                    width: 100%;
                    max-width: 1400px;
                    height: 90vh;
                }
                
                .products-sidebar {
                    flex: 0 0 350px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 10px;
                    padding: 20px;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                }
                
                .products-header {
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .products-grid {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                
                .cart-sidebar {
                    flex: 0 0 300px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 10px;
                    padding: 20px;
                    overflow-y: auto;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                }
                
                .cart-header {
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .cart-empty {
                    text-align: center;
                    color: #999;
                    padding: 40px 20px;
                    font-size: 14px;
                }
                
                .chat-container {
                    flex: 1;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                    display: flex;
                    flex-direction: column;
                }
                
                .chat-header {
                    background: #667eea;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;
                }
                
                .chat-messages {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                }
                
                .chat-input {
                    padding: 20px;
                    border-top: 1px solid #e0e0e0;
                    display: flex;
                    gap: 10px;
                }
                
                .chat-input input {
                    flex: 1;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 25px;
                    outline: none;
                    font-size: 14px;
                }
                
                .chat-input input:focus {
                    border-color: #667eea;
                }
                
                .chat-input button {
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: background 0.3s;
                }
                
                .chat-input button:hover {
                    background: #5568d3;
                }
                
                .chat-input button:active {
                    transform: scale(0.95);
                }
                
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .chat-messages::-webkit-scrollbar {
                    width: 6px;
                }
                
                .chat-messages::-webkit-scrollbar-track {
                    background: #f1f1f1;
                }
                
                .chat-messages::-webkit-scrollbar-thumb {
                    background: #888;
                    border-radius: 3px;
                }
            """)
        ),
        Body(
            Div(
                # Left sidebar with products
                Div(
                    Div("Available Products", cls="products-header"),
                    Div(
                        *[ProductCard(p["name"], p["price"], p["emoji"]) for p in products],
                        cls="products-grid"
                    ),
                    cls="products-sidebar"
                ),
                # Middle chat container
                Div(
                    Div("E-Commerce Assistant", cls="chat-header"),
                    Div(
                        ChatMessage("Hello! How can I help you shop today?", is_user=False),
                        id="chat-messages",
                        cls="chat-messages",
                        hx_get="/messages",
                        hx_trigger="load",
                        hx_swap="innerHTML"
                    ),
                    Form(
                        Input(
                            type="text",
                            name="message",
                            placeholder="Ask about products...",
                            autocomplete="off",
                            id="message-input"
                        ),
                        Button("Send", type="submit"),
                        hx_post="/send",
                        hx_target="#chat-messages",
                        hx_swap="beforeend",
                        hx_on="htmx:configRequest: const input = document.getElementById('message-input'); if(input.value.trim()) { document.getElementById('chat-messages').insertAdjacentHTML('beforeend', `<div style=\"max-width: 70%; padding: 12px 16px; border-radius: 18px 18px 4px 18px; background: #667eea; color: white; word-wrap: break-word; align-self: flex-end; margin-bottom: 10px; animation: fadeIn 0.3s;\">${input.value}</div>`); input.value = ''; }",
                        cls="chat-input"
                    ),
                    cls="chat-container"
                ),
                # Right cart sidebar
                Div(
                    Div("Your Cart", cls="cart-header"),
                    Div(
                        Div("Cart is empty", cls="cart-empty"),
                        id="cart-items"
                    ),
                    cls="cart-sidebar"
                ),
                cls="main-container"
            ),
            Script(src="https://unpkg.com/htmx.org@1.9.10")
        )
    )

@rt("/messages")
def get():
    """Get all messages"""
    result = [ChatMessage("Hello! How can I help you shop today?", is_user=False)]
    for msg in messages:
        result.append(ChatMessage(msg['text'], is_user=msg['is_user']))
    return result

@rt("/send")
async def post(message: str):
    """Handle message submission"""
    global agent_message_history
    bot_response = ""
    
    if message.strip():
        messages.append({"text": message, "is_user": True})
        
        # Check for clear command
        if message.lower().strip() in ["clear", "clear chat", "reset"]:
            messages.clear()
            agent_message_history = []
            bot_response = "Chat cleared! How can I help you?"
            messages.append({"text": bot_response, "is_user": False})
        else:
            # Use Pydantic agent for response
            try:
                result = await run_agent_with_logging(message, agent_message_history)
                bot_response = result.output
                agent_message_history = result.all_messages()
                
                # Process tool calls for cart actions
                import json
                for msg in result.all_messages():
                    if hasattr(msg, 'parts'):
                        for part in msg.parts:
                            if part.__class__.__name__ == 'ToolReturnPart':
                                try:
                                    cart_action = json.loads(part.content)
                                    action = cart_action.get('action')
                                    product_name = cart_action.get('product')
                                    quantity = cart_action.get('quantity', 1)
                                    
                                    if action == 'add':
                                        cart[product_name] = cart.get(product_name, 0) + quantity
                                    elif action == 'remove':
                                        cart.pop(product_name, None)
                                    elif action == 'update':
                                        if quantity > 0:
                                            cart[product_name] = quantity
                                        else:
                                            cart.pop(product_name, None)
                                except (json.JSONDecodeError, AttributeError, KeyError):
                                    pass
                
                messages.append({"text": bot_response, "is_user": False})
            except Exception as e:
                bot_response = f"Sorry, I encountered an error: {str(e)}"
                messages.append({"text": bot_response, "is_user": False})
    
    # Return only bot response and cart update
    result = [ChatMessage(bot_response, is_user=False)]
    
    # Add OOB cart update
    cart_div = Div(*get_cart_items(), id="cart-items", **{"hx-swap-oob": "innerHTML"})
    result.append(cart_div)
    
    return result

def get_cart_items():
    """Generate cart items HTML"""
    if not cart:
        return [Div("Cart is empty", cls="cart-empty")]
    
    items = []
    for name, qty in cart.items():
        product = next((p for p in products if p["name"] == name), None)
        if product:
            items.append(CartItem(name, product["price"], product["emoji"], qty))
    return items

serve()

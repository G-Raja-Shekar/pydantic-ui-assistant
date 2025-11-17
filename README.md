# E-Commerce AI Assistant 🛒

An intelligent shopping assistant powered by Pydantic AI that enables natural language interactions for managing a shopping cart. Built with FastHTML for a modern, responsive web interface.

## Features

- 🤖 **AI-Powered Chat**: Conversational interface using Gemini 2.5 Flash model
- 🛍️ **Product Catalog**: Browse and shop from a curated selection of household items
- 🛒 **Smart Cart Management**: Add, remove, or update quantities using natural language
- 📊 **Observability**: Integrated Logfire logging for monitoring and debugging
- ⚡ **Real-time Updates**: HTMX-powered dynamic UI without page refreshes
- 💬 **Message History**: Context-aware conversations that remember your requests

## Available Products

- Salt 🧂 - $2.50
- Pepper 🌶️ - $3.00
- Toothpaste 🦷 - $4.99
- Toothbrush 🪥 - $3.50
- Detergent 🧴 - $8.99
- Soap 🧼 - $2.99
- Shampoo 🧴 - $6.99
- Paper Towels 🧻 - $5.49

## Prerequisites

- Python 3.11+
- Gemini API access
- Logfire account (for observability)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pydantic-ui-assistant
```

2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

3. Create a `.env` file with required credentials:

```env
LOGFIRE_WRITE_TOKEN=your_logfire_token
ENVIRONMENT=development
SERVICE_NAME=ecommerce-assistant
GEMINI_API_KEY=your_gemini_api_key
```

## Usage

### Web Interface

Start the FastHTML application:

```bash
python ui.py
```

The application will be available at `http://localhost:5001`

### Command Line Interface

Run the CLI version:

```bash
python main.py
```

## How It Works

### Architecture

- **Pydantic AI Agent**: Manages cart operations using structured tool calls
- **FastHTML**: Provides the web framework and UI components
- **Logfire**: Tracks agent interactions and tool executions
- **HTMX**: Enables dynamic updates without JavaScript frameworks

### Cart Operations

The AI assistant supports three cart actions:

- **Add**: "Add 2 bottles of shampoo to my cart"
- **Remove**: "Remove toothpaste from cart"
- **Update**: "Change salt quantity to 3"

### Example Interactions

```
User: Add salt and pepper to my cart
Assistant: I've added Salt and Pepper to your cart!

User: I need 3 bottles of shampoo
Assistant: Added 3 bottles of Shampoo to your cart!

User: Remove pepper
Assistant: Removed Pepper from your cart!
```

## Project Structure

```
pydantic-ui-assistant/
├── main.py              # Core agent logic and CLI
├── ui.py                # FastHTML web interface
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Key Components

### Agent (`main.py`)

- Configured with Gemini 2.5 Flash model
- Uses `manage_cart` tool for all cart operations
- Maintains conversation history for context
- Integrated Logfire instrumentation

### Web UI (`ui.py`)

- Three-panel layout: Products | Chat | Cart
- Real-time cart updates
- Responsive gradient design
- Message history persistence

## Technologies

- **[Pydantic AI](https://ai.pydantic.dev/)**: AI agent framework
- **[FastHTML](https://fastht.ml/)**: Python web framework
- **[Logfire](https://logfire.pydantic.dev/)**: Observability platform
- **[HTMX](https://htmx.org/)**: Dynamic HTML updates
- **Gemini 2.5 Flash**: Google's AI model

## Development

The application follows a 50-line code limit guideline for maintainability and clarity.

## License

MIT

## Contributing

Contributions are welcome! Please ensure code follows the project's style guidelines.

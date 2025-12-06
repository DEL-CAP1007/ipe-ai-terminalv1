# IPE AI Terminal

An AI-powered CLI assistant built with Python, OpenAI, and Notion integration.

## Features

- **Ask Questions**: Query the OpenAI API with natural language prompts
- **Generate Content**: Create tailored content for various topics
- **Notion Integration**: Interact with Notion databases (in development)
- **Streaming Responses**: Real-time response streaming for better UX
- **Environment Configuration**: Easy setup via `.env` file

## Requirements

- Python 3.9+
- OpenAI API key

## Setup

### 1. Clone or navigate to the project

```bash
cd /Volumes/T7/ipe-ai-terminal
```

### 2. Activate the virtual environment

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit the `.env` file with your API keys:

```bash
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
```

## Usage

### Ask a question

```bash
python src/main.py ask "What is machine learning?"
```

### Generate content

```bash
python src/main.py generate "A blog post about AI"
```

### Show help

```bash
python src/main.py help
```

### Notion integration

```bash
python src/main.py notion list
```

## Project Structure

```
.
├── src/
│   ├── main.py              # CLI entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── dispatcher.py    # Prompt routing
│   │   └── llm.py           # OpenAI client
│   └── commands/
│       ├── __init__.py
│       ├── help.py          # Help command
│       ├── generate.py      # Content generation
│       └── notion.py        # Notion integration
├── templates/               # Template files
├── data/                    # Data storage
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── venv/                    # Python virtual environment
```

## Development

To add a new command:

1. Create a file in `src/commands/` with your command logic
2. Import and register it in `src/main.py`
3. Update this README with usage instructions

## API Configuration

### OpenAI

Get your API key from [OpenAI](https://platform.openai.com/api-keys)

### Notion

Get your API key from [Notion Developers](https://www.notion.so/my-integrations)

## Troubleshooting

**ImportError: No module named 'src'**
- Ensure you're running from the project root: `/Volumes/T7/ipe-ai-terminal`
- Confirm the virtual environment is activated

**OPENAI_API_KEY not set**
- Check that your `.env` file has the correct API key
- Use `source venv/bin/activate` to ensure environment variables are loaded

## License

MIT

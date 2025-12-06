def run_help():
    print("""
AI TERMINAL COMMANDS

Usage:
    python src/main.py <command> <args>

Commands:
    help                    Show this help menu
    generate <topic>        Generate text or content with AI
    notion <action>         Create or modify Notion items
    
Examples:
    python src/main.py generate proposal
    python src/main.py notion create-database Speakers
    python src/main.py notion generate-pitchnight "IndigiRise Accelerator Pitch Night January 2026"
    """)

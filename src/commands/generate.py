from core.llm import ask_ai

def run_generate(args):
    if not args:
        print("Please provide a topic.")
        return

    topic = " ".join(args)
    prompt = f"Generate content for: {topic}"
    output = ask_ai(prompt)

    print("\n==== AI OUTPUT ====\n")
    print(output)

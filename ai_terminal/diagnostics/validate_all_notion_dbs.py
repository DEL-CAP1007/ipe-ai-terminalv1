import subprocess

db_names = [
    "INDIGIRISE_PARTICIPANTS",
    "INDIGIRISE",
    "COMM_LOG",
    "K12",
    "SPEAKERS",
    "CLIENTS",
    "EVENTS",
    "TASKS"
]

for name in db_names:
    print(f"\n--- Validating Notion database: {name} ---")
    proc = subprocess.run([
        "python3", "ai_terminal/diagnostics/get_notion_db_properties.py"],
        input=name.encode(),
        capture_output=True
    )
    print(proc.stdout.decode())
    if proc.stderr:
        print(proc.stderr.decode())

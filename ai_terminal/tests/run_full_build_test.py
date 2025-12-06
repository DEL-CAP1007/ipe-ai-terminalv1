import subprocess

if __name__ == "__main__":
    print("Running full build validation...")
    result = subprocess.run([
        "python3", "ai_terminal/diagnostics/validate_notion.py"
    ], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode == 0:
        print("Full build validation completed successfully.")
    else:
        print("Full build validation failed.")
        print(result.stderr)

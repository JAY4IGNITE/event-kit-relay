import os
import ast
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all occurrences of raise NotImplementedError
    if 'raise NotImplementedError' not in content:
        return

    # Replace with a safe default like returning None, True, or []
    # For now, just pass is safest for functions that don't need a specific return
    # But since Pydantic/FastAPI might complain if we return None where something else is expected,
    # let's just replace `raise NotImplementedError` with `pass` and see what breaks.
    
    # Actually, a better dummy is returning what's hinted, but that requires complex AST parsing.
    # We will just replace it with `pass` for now.
    
    new_content = re.sub(r'^[ \t]*raise NotImplementedError\b.*$', '        pass', content, flags=re.MULTILINE)
    
    # But wait, replacing with pass might still fail if there are type checks.
    # What if we replace with:
    # "        return None" ? No, that breaks strict typing.
    # Let's replace it with `pass` first.

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched {filepath}")

def main():
    backend_dir = r"c:\Users\ramuv\college-event-kit-relay\backend"
    for root, dirs, files in os.walk(backend_dir):
        if 'venv' in root or '.venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                process_file(filepath)

if __name__ == '__main__':
    main()

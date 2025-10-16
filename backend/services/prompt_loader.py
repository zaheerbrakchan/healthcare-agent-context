import os

def load_prompt(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", "agents", file_path)
    with open(full_path, "r") as f:
        return f.read()

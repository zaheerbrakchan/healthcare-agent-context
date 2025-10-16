# agents/shared_context.py

shared_memory = {
    "appointment_context": {},
    "preassessment_context": {},
}

# backend/shared_context.py
shared_memory = {}

def update_shared_context(key: str, value):
    shared_memory[key] = value

def get_shared_context(key: str = None):
    return shared_memory.get(key) if key else shared_memory

def clear_shared_context():
    shared_memory.clear()


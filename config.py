# Configuration constants for Vision Assistant

# Premium Colors (Dark Mode)
BG_COLOR = "#0f172a"    # Deep Navy
CARD_COLOR = "#1e293b"  # Slate Blue
PRIMARY_COLOR = "#38bdf8"     # Sky Blue
SUCCESS_COLOR = "#10b981"     # Emerald Green
DANGER_COLOR = "#f43f5e"      # Rose Red
WARNING_COLOR = "#fbbf24"     # Amber Yellow
TEXT_COLOR = "#f8fafc"        # Ghost White
TEXT_LIGHT_COLOR = "#94a3b8"  # Slate Gray

# Model paths
YOLO_MODEL_PATH = 'best.pt'
AGENT_MEMORY_PATH = 'agent_memory.json'

# Timings & Thresholds
CONFIRM_THRESHOLD = 3   # Must see object 3 times before speaking
COOLDOWN_TIME = 5.0     # Wait 5 seconds between same alerts

# Priorities
PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}

# Indoor Classes
INDOOR_CLASSES = {
    0: {'name': 'Person', 'priority': 'high', 'alert': 'Person'},
    56: {'name': 'Chair', 'priority': 'medium', 'alert': 'Chair'},
    57: {'name': 'Couch', 'priority': 'medium', 'alert': 'Couch'},
    59: {'name': 'Bed', 'priority': 'low', 'alert': 'Bed'},
    60: {'name': 'Table', 'priority': 'medium', 'alert': 'Table'},
    61: {'name': 'Toilet', 'priority': 'low', 'alert': 'Toilet'},
    62: {'name': 'TV', 'priority': 'low', 'alert': 'TV'},
    63: {'name': 'Laptop', 'priority': 'low', 'alert': 'Laptop'},
    67: {'name': 'Phone', 'priority': 'low', 'alert': 'Phone'},
    72: {'name': 'Fridge', 'priority': 'low', 'alert': 'Fridge'},
    73: {'name': 'Book', 'priority': 'low', 'alert': 'Book'},
    74: {'name': 'Clock', 'priority': 'low', 'alert': 'Clock'},
    75: {'name': 'Vase', 'priority': 'medium', 'alert': 'Vase'},
    76: {'name': 'Scissors', 'priority': 'high', 'alert': 'Scissors'},
    39: {'name': 'Bottle', 'priority': 'low', 'alert': 'Bottle'},
    44: {'name': 'Knife', 'priority': 'high', 'alert': 'Knife'},
    64: {'name': 'Mouse', 'priority': 'low', 'alert': 'Mouse'},
    65: {'name': 'Remote', 'priority': 'low', 'alert': 'Remote'},
    66: {'name': 'Keyboard', 'priority': 'low', 'alert': 'Keyboard'},
    41: {'name': 'Cup', 'priority': 'low', 'alert': 'Cup'},
    43: {'name': 'Fork', 'priority': 'medium', 'alert': 'Fork'},
    24: {'name': 'Backpack', 'priority': 'low', 'alert': 'Backpack'},
}

# Room Patterns
ROOM_PATTERNS = {
    'kitchen': ['fridge', 'refrigerator', 'oven', 'microwave', 'sink'],
    'bedroom': ['bed', 'pillow', 'wardrobe', 'dresser'],
    'bathroom': ['toilet', 'sink', 'shower', 'towel'],
    'living_room': ['couch', 'sofa', 'tv', 'television']
}

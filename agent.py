import json
import os
import config

class FastAgent:
    def __init__(self):
        self.memory = {
            'rooms': [],
            'current_room': 'unknown'
        }
        self.load_memory()
    
    def load_memory(self):
        if os.path.exists(config.AGENT_MEMORY_PATH):
            try:
                with open(config.AGENT_MEMORY_PATH, 'r') as f:
                    loaded = json.load(f)
                    self.memory['rooms'] = loaded.get('rooms', [])
                    self.memory['current_room'] = loaded.get('current_room', 'unknown')
            except:
                pass
    
    def save_memory(self):
        try:
            with open(config.AGENT_MEMORY_PATH, 'w') as f:
                json.dump(self.memory, f)
        except:
            pass
    
    def get_room(self, objects):
        for room, patterns in config.ROOM_PATTERNS.items():
            for p in patterns:
                if any(p in obj.lower() for obj in objects):
                    if room != self.memory.get('current_room', 'unknown'):
                        self.memory['current_room'] = room
                        if room not in self.memory['rooms']:
                            self.memory['rooms'].append(room)
                            self.save_memory()
                    return room
        return self.memory.get('current_room', 'unknown')
    
    def get_action(self, obj, dist, zone):
        if dist < 1.0:
            if zone == 'left':
                return f"Stop! {obj} very close on right"
            elif zone == 'right':
                return f"Stop! {obj} very close on left"
            else:
                return f"Stop! {obj} straight ahead"
        elif dist < 1.8:
            if zone == 'left':
                return f"{obj} left, move right"
            elif zone == 'right':
                return f"{obj} right, move left"
            else:
                return f"{obj} ahead, go slow"
        return None
    
    def get_report(self):
        report = "🤖 AGENT REPORT\n"
        report += "=" * 30 + "\n"
        report += f"📍 Room: {self.memory.get('current_room', 'unknown').upper()}\n"
        if self.memory.get('rooms'):
            report += f"🏠 Known: {', '.join(self.memory['rooms'])}\n"
        else:
            report += "🏠 Known: None yet\n"
        report += "=" * 30
        return report

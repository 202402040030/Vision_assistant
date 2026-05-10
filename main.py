import tkinter as tk
from agent import FastAgent
from voice import VoiceEngine
from detection import DetectionEngine
from gui import VisionAssistantGUI
from command_listener import VoiceCommandEngine as CommandListener

def main():
    print("="*50)
    print("Initializing Vision Assistant Pro...")
    print("="*50)
    
    root = tk.Tk()
    
    # Initialize Core Components
    voice_engine = VoiceEngine()
    agent = FastAgent()
    detection_engine = DetectionEngine()
    
    # Initialize GUI
    app = VisionAssistantGUI(root, detection_engine, voice_engine, agent)
    
    # Initialize Command Listener
    command_listener = CommandListener(app, logger=app.log)
    command_listener.start()
    
    # We pass the log function from the GUI into the components so they can output to the UI log panel
    voice_engine.logger = app.log
    detection_engine.logger = app.log
    detection_engine.depth_estimator.logger = app.log
    
    # Check Voice Availability
    from voice import SPEECH_AVAILABLE
    if not SPEECH_AVAILABLE:
        print("\n" + "="*50)
        print("⚠️ For voice, install pywin32:")
        print("   pip install pywin32")
        print("="*50 + "\n")
        
    # Shutdown hook for command listener
    def on_closing():
        command_listener.stop()
        app.stop_camera()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()

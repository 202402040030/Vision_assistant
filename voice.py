import threading

# Windows built-in speech
try:
    import win32com.client
    import pythoncom
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

# Fallback speech
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class VoiceEngine:
    def __init__(self, logger=None):
        self.logger = logger
        self.enabled = True
        self.init_speech()

    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(f"[VoiceEngine] {message}")

    def init_speech(self):
        if SPEECH_AVAILABLE or PYTTSX3_AVAILABLE:
            engine_name = "SAPI (Windows Native)" if SPEECH_AVAILABLE else "pyttsx3"
            self.log(f"✅ Voice engine ready ({engine_name})")
        else:
            self.log("⚠️ Voice engine not found. Install pyttsx3 or pywin32.")

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled

    def set_enabled(self, enabled):
        self.enabled = enabled

    def is_enabled(self):
        return self.enabled

    def speak(self, text):
        if not self.enabled:
            return
        
        def _speak():
            # Try SAPI (Windows Native) with Interrupt Flag
            if SPEECH_AVAILABLE:
                try:
                    pythoncom.CoInitialize()
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Rate = 3
                    speaker.Volume = 100
                    # Flag 2 = Purge (Interrupts previous speech)
                    speaker.Speak(text, 2) 
                    return
                except Exception as e:
                    self.log(f"SAPI Error: {e}")
            
            # Fallback to pyttsx3
            if PYTTSX3_AVAILABLE:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 200)
                    engine.say(text)
                    engine.runAndWait()
                    return
                except Exception as e:
                    self.log(f"pyttsx3 Error: {e}")
            
            # Console fallback
            print(f"📢 [VOICE] {text}")
            
        threading.Thread(target=_speak, daemon=True).start()

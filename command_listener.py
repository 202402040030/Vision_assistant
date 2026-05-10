import threading
import time
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import queue

class SoundDeviceMic(sr.AudioSource):
    """A custom AudioSource for SpeechRecognition that uses sounddevice instead of PyAudio."""
    def __init__(self, device_index=None, sample_rate=16000, chunk_size=1024):
        self.device_index = device_index
        self.SAMPLE_WIDTH = 2  # 16-bit
        self.SAMPLE_RATE = sample_rate
        self.CHUNK = chunk_size
        self._sd_stream = None
        self.stream = None
        
    def __enter__(self):
        self.q = queue.Queue()
        def callback(indata, frames, time, status):
            if status:
                pass # Optionally log status like overflow
            self.q.put(bytes(indata))
            
        self._sd_stream = sd.RawInputStream(
            device=self.device_index,
            channels=1,
            samplerate=self.SAMPLE_RATE,
            dtype='int16',
            blocksize=self.CHUNK,
            callback=callback
        )
        self._sd_stream.start()
        
        class SDStream:
            def __init__(self, q):
                self.q = q
            def read(self, size):
                return self.q.get()
                
        self.stream = SDStream(self.q)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._sd_stream:
            self._sd_stream.stop()
            self._sd_stream.close()
        self.stream = None


class VoiceCommandEngine:
    def __init__(self, app, logger=None):
        self.app = app
        self.logger = logger
        self.recognizer = sr.Recognizer()
        
        # Adjust recognizer thresholds for better speed
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.non_speaking_duration = 0.5  # Standard default
        self.recognizer.pause_threshold = 0.8  # Wait longer to avoid chopping phrases in half
        
        self.device_id = self.find_best_mic()
        self.stop_listening_fn = None
        
    def find_best_mic(self):
        try:
            default_in = sd.default.device[0]
            devices = sd.query_devices()
            best_device = default_in
            
            # Try to find a better microphone than an empty "Jack Mic"
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = dev['name'].lower()
                    if 'array' in name or 'usb' in name or 'headset' in name:
                        best_device = i
                        break
                        
            if best_device is not None:
                dev_info = sd.query_devices(best_device)
                self.log(f"🎤 Using mic: {dev_info['name']}")
                return best_device
        except Exception as e:
            self.log(f"Microphone selection error: {e}")
        return None
        
    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(f"[CommandListener] {message}")

    def start(self):
        self.log("🎤 Voice Command Listener Started.")
        
        source = SoundDeviceMic(device_index=self.device_id)
        
        # Calibrate ambient noise
        with source as s:
            self.recognizer.adjust_for_ambient_noise(s, duration=1)
            
        # This spawns a background thread that uses Voice Activity Detection (VAD)
        # It never misses a word because it listens continuously and only extracts spoken phrases
        self.stop_listening_fn = self.recognizer.listen_in_background(source, self.on_speech_received)

    def stop(self):
        if self.stop_listening_fn:
            self.stop_listening_fn(wait_for_stop=False)
        self.log("🛑 Voice Command Listener Stopped.")

    def on_speech_received(self, recognizer, audio_data):
        """Callback fired automatically by listen_in_background when a phrase is spoken."""
        try:
            # We process this in the background thread immediately
            text = recognizer.recognize_google(audio_data).lower()
            if text:
                self.process_command(text)
        except sr.UnknownValueError:
            pass # Did not understand the audio (e.g., just a cough)
        except sr.RequestError as e:
            self.log(f"⚠️ Speech API error (check internet): {e}")

    def process_command(self, text):
        self.log(f"🗣️ Heard: '{text}'")
        
        # Schedule GUI updates safely on the main thread
        if "start engine" in text or "start camera" in text:
            self.app.root.after(0, self.app.start_camera)
        elif "stop engine" in text or "shutdown" in text or "stop camera" in text:
            self.app.root.after(0, self.app.stop_camera)
        elif "report" in text or "status" in text:
            self.app.root.after(0, self.app.show_report)
        elif "emergency" in text or "help me" in text:
            self.app.root.after(0, self.app.emergency_alert)
        elif "voice off" in text or "mute" in text:
            if self.app.voice_var.get():
                self.app.root.after(0, self.app.toggle_voice)
        elif "voice on" in text or "unmute" in text:
            if not self.app.voice_var.get():
                self.app.root.after(0, self.app.toggle_voice)
        elif "save log" in text:
            self.app.root.after(0, self.app.save_log)
        elif "test" in text:
            self.app.root.after(0, self.app.test_voice)
        else:
            self.log(f"❓ Command not recognized: {text}")
            self.app.root.after(0, lambda: self.app.voice_engine.speak("Command not recognized"))


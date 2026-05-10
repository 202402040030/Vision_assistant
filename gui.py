import cv2
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import time
import threading
import config

class VisionAssistantGUI:
    def __init__(self, root, detection_engine, voice_engine, agent):
        self.root = root
        self.detection_engine = detection_engine
        self.voice_engine = voice_engine
        self.agent = agent
        
        self.root.title("⚡ ULTRA-FAST Vision Assistant")
        self.root.geometry("1000x750")
        self.root.configure(bg=config.BG_COLOR)
        
        self.cap = None
        self.running = False
        self.voice_var = tk.BooleanVar(value=True)
        
        # State Tracking
        self.current_objects = {}  # name -> data
        self.last_spoken = {}       # name -> last spoken time
        self.persistence_counters = {} # name -> count
        
        self.setup_ui()
    
    def create_styled_button(self, parent, text, command, bg_color, fg_color="white", width=12):
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=fg_color,
                        font=('Segoe UI', 10, 'bold'),
                        relief=tk.FLAT, bd=0,
                        padx=15, pady=8, width=width,
                        cursor='hand2',
                        activebackground=bg_color,
                        activeforeground=fg_color)
        
        def on_enter(e):
            btn.config(background=self.adjust_color(bg_color, -20))
        def on_leave(e):
            btn.config(background=bg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

    def setup_ui(self):
        main = tk.Frame(self.root, bg=config.BG_COLOR)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header (Glassmorphism look)
        header = tk.Frame(main, bg=config.CARD_COLOR, height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="✨ VISION ASSISTANT PRO", 
                font=('Segoe UI', 22, 'bold'), bg=config.CARD_COLOR, fg=config.PRIMARY_COLOR).pack(pady=(12, 0))
        tk.Label(header, text="AI-Powered Spatial Intelligence | Real-Time Guidance", 
                font=('Segoe UI', 9), bg=config.CARD_COLOR, fg=config.TEXT_LIGHT_COLOR).pack()
        
        # Upper Section: Camera and Stats
        content_frame = tk.Frame(main, bg=config.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Camera Card (Left)
        cam_card = tk.Frame(content_frame, bg=config.CARD_COLOR, padx=2, pady=2)
        cam_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.video_container = tk.Frame(cam_card, bg='#020617')
        self.video_container.pack(fill=tk.BOTH, expand=True)
        
        self.video_label = tk.Label(self.video_container, bg='#020617')
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        self.placeholder = tk.Label(self.video_container, 
                                    text="📷 CAMERA OFFLINE\nClick 'START ENGINE'",
                                    font=('Segoe UI', 12, 'bold'), bg='#020617', fg=config.TEXT_LIGHT_COLOR)
        self.placeholder.place(relx=0.5, rely=0.5, anchor='center')

        # Stats Card (Right)
        stats_card = tk.Frame(content_frame, bg=config.CARD_COLOR, width=280, padx=20, pady=20)
        stats_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        stats_card.pack_propagate(False)
        
        tk.Label(stats_card, text="SYSTEM STATUS", font=('Segoe UI', 10, 'bold'),
                bg=config.CARD_COLOR, fg=config.PRIMARY_COLOR).pack(anchor='w', pady=(0, 15))
        
        # Guidance Sub-card
        guidance_frame = tk.Frame(stats_card, bg='#334155', padx=10, pady=10)
        guidance_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(guidance_frame, text="🧭 GUIDANCE", font=('Segoe UI', 8, 'bold'),
                bg='#334155', fg=config.PRIMARY_COLOR).pack(anchor='w')
        self.nav_label = tk.Label(guidance_frame, text="System Standby", font=('Segoe UI', 11, 'bold'),
                                  bg='#334155', fg=config.TEXT_COLOR)
        self.nav_label.pack(anchor='w', pady=(5, 0))
        
        # Distance Sub-card
        dist_frame = tk.Frame(stats_card, bg='#334155', padx=10, pady=10)
        dist_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(dist_frame, text="📏 DISTANCE", font=('Segoe UI', 8, 'bold'),
                bg='#334155', fg=config.PRIMARY_COLOR).pack(anchor='w')
        self.distance_label = tk.Label(dist_frame, text="--", font=('Segoe UI', 11, 'bold'),
                                       bg='#334155', fg=config.TEXT_COLOR)
        self.distance_label.pack(anchor='w', pady=(5, 0))
        
        # Mode Sub-card
        mode_frame = tk.Frame(stats_card, bg='#334155', padx=10, pady=10)
        mode_frame.pack(fill=tk.X)
        tk.Label(mode_frame, text="📊 ENGINE", font=('Segoe UI', 8, 'bold'),
                bg='#334155', fg=config.PRIMARY_COLOR).pack(anchor='w')
        self.status_label = tk.Label(mode_frame, text="● IDLE", font=('Segoe UI', 11, 'bold'),
                                     bg='#334155', fg=config.SUCCESS_COLOR)
        self.status_label.pack(anchor='w', pady=(5, 0))
        
        # Controls Section
        ctrl_card = tk.Frame(main, bg=config.CARD_COLOR, padx=20, pady=15)
        ctrl_card.pack(fill=tk.X, pady=20)
        
        btn_row = tk.Frame(ctrl_card, bg=config.CARD_COLOR)
        btn_row.pack(fill=tk.X)
        
        self.start_btn = self.create_styled_button(btn_row, "▶ START ENGINE", self.start_camera, config.SUCCESS_COLOR)
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_btn = self.create_styled_button(btn_row, "⏹ SHUTDOWN", self.stop_camera, config.DANGER_COLOR)
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.save_log_btn = self.create_styled_button(btn_row, "💾 SAVE LOG", self.save_log, config.PRIMARY_COLOR)
        self.save_log_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.emergency_btn = self.create_styled_button(btn_row, "🆘 EMERGENCY", self.emergency_alert, "#f97316")
        self.emergency_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Secondary Controls
        sec_row = tk.Frame(ctrl_card, bg=config.CARD_COLOR)
        sec_row.pack(fill=tk.X, pady=(15, 0))
        
        self.voice_btn = self.create_styled_button(sec_row, "🔊 VOICE: ON", self.toggle_voice, "#475569", width=10)
        self.voice_btn.pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(sec_row, "🧪 TEST VOICE", self.test_voice, "#475569", width=10).pack(side=tk.LEFT, padx=5)
        
        self.create_styled_button(sec_row, "🤖 REPORT", self.show_report, "#8b5cf6", width=10).pack(side=tk.LEFT, padx=5)
        
        # Camera ID
        cam_frame = tk.Frame(sec_row, bg=config.CARD_COLOR)
        cam_frame.pack(side=tk.RIGHT, padx=5)
        tk.Label(cam_frame, text="CAM ID:", font=('Segoe UI', 9, 'bold'), bg=config.CARD_COLOR, fg=config.TEXT_LIGHT_COLOR).pack(side=tk.LEFT)
        self.cam_id = tk.StringVar(value="0")
        tk.Spinbox(cam_frame, from_=0, to=5, width=3, textvariable=self.cam_id, 
                  font=('Segoe UI', 10), bg='#334155', fg='white', buttonbackground='#1e293b', bd=0).pack(side=tk.LEFT, padx=5)

        # Voice Command Indicator
        self.mic_label = tk.Label(sec_row, text="🎙️ LISTENING", font=('Segoe UI', 9, 'bold'), bg=config.CARD_COLOR, fg=config.SUCCESS_COLOR)
        self.mic_label.pack(side=tk.RIGHT, padx=15)

        # Log Section
        log_card = tk.Frame(main, bg=config.CARD_COLOR, padx=15, pady=15)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_card, text="📜 SYSTEM TERMINAL", font=('Segoe UI', 9, 'bold'),
                bg=config.CARD_COLOR, fg=config.PRIMARY_COLOR).pack(anchor='w', pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(log_card, height=6,
                                                   font=('Consolas', 9),
                                                   bg='#020617', fg='#10b981',
                                                   insertbackground='white',
                                                   relief=tk.FLAT, bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        tk.Label(main, text="🔴 HIGH ALERT (Knife, Person)  🟡 CAUTION (Furniture)  🟢 CLEAR (Accessories)", 
                font=('Segoe UI', 8, 'bold'), bg=config.BG_COLOR, fg=config.TEXT_LIGHT_COLOR).pack(pady=(10, 0))

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        print(f"[{timestamp}] {message}")
        
    def show_report(self):
        report = self.agent.get_report()
        messagebox.showinfo("Agent Report", report)
    
    def toggle_voice(self):
        self.voice_var.set(not self.voice_var.get())
        self.voice_engine.set_enabled(self.voice_var.get())
        if self.voice_var.get():
            self.voice_btn.config(text="🔊 VOICE: ON", bg="#475569")
        else:
            self.voice_btn.config(text="🔇 VOICE: OFF", bg=config.DANGER_COLOR)
            
    def test_voice(self):
        self.voice_engine.speak("Voice working. System test successful.")
        
    def save_log(self):
        try:
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vision_log_{ts}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f"💾 Log saved: {filename}")
            self.voice_engine.speak("Log saved")
            messagebox.showinfo("Success", f"Log saved as {filename}")
        except Exception as e:
            self.log(f"❌ Save error: {e}")
            messagebox.showerror("Error", f"Could not save log: {e}")

    def emergency_alert(self):
        import winsound
        def play_beeps():
            for i in range(3):
                winsound.Beep(1500, 400)
                time.sleep(0.1)
        threading.Thread(target=play_beeps, daemon=True).start()
        self.voice_engine.speak("EMERGENCY! Help alerted!")
        self.log("🆘 EMERGENCY")
        
        def flash():
            for _ in range(3):
                self.root.configure(bg='#f8d7da')
                time.sleep(0.1)
                self.root.configure(bg=config.BG_COLOR)
                time.sleep(0.1)
        threading.Thread(target=flash, daemon=True).start()

    def start_camera(self):
        idx = int(self.cam_id.get())
        self.log(f"Starting camera {idx}...")
        
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(idx)
        
        if not self.cap.isOpened():
            self.log("❌ Camera not found!")
            self.voice_engine.speak("Camera not found")
            return
        
        self.running = True
        self.current_objects = {}
        self.last_spoken = {}
        
        self.detection_engine.start()
        
        self.voice_engine.speak("Ready")
        self.log("✅ Camera started! Priority: Person always speaks first")
        self.update_loop()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.detection_engine.stop()
        
        self.voice_engine.speak("Assistant off")
        self.log("⏹ Stopped")
        self.status_label.config(text="● READY", fg=config.SUCCESS_COLOR)
        self.nav_label.config(text="Ready")
        self.distance_label.config(text="--")
        self.video_label.config(image='')
        
        if not hasattr(self, 'placeholder') or not self.placeholder:
            self.placeholder = tk.Label(self.video_container, 
                                       text="🎥 Camera feed here\n\nClick 'START'",
                                       font=('Segoe UI', 13), bg='#1a1a2e', fg='#888888')
            self.placeholder.place(relx=0.5, rely=0.5, anchor='center')
        
        self.current_objects.clear()
        self.last_spoken.clear()
        self.agent.save_memory()

    def update_loop(self):
        if self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Provide frame to inference engine
                self.detection_engine.update_frame(frame)
                
                if hasattr(self, 'placeholder') and self.placeholder:
                    self.placeholder.destroy()
                    delattr(self, 'placeholder')
                
                # Retrieve current detection results
                current = self.detection_engine.get_results()
                
                # Draw boxes
                processed = frame.copy()
                h, w = processed.shape[:2]
                zone_w = w // 3
                cv2.rectangle(processed, (0, 0), (zone_w, h), (255, 255, 255), 1)
                cv2.rectangle(processed, (w-zone_w, 0), (w, h), (255, 255, 255), 1)
                
                if current:
                    for name, data in current.items():
                        x1, y1, x2, y2 = data['box']
                        obj = data['obj']
                        color = (0, 0, 255) if obj['priority'] == 'high' else (0, 255, 255) if obj['priority'] == 'medium' else (0, 255, 0)
                        
                        cv2.rectangle(processed, (x1, y1), (x2, y2), color, 2)
                        label = f"{obj['name']} {data['dist']:.1f}m"
                        cv2.putText(processed, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        
                # Display
                rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img = img.resize((750, 450), Image.Resampling.BILINEAR)
                imgtk = ImageTk.PhotoImage(img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                
                current_names = set(current.keys())
                now = time.time()
                
                # ===== FIND HIGHEST PRIORITY OBJECT =====
                best_object = None
                best_priority = 999
                best_distance = 999
                
                for name, data in current.items():
                    p = config.PRIORITY_ORDER.get(data['priority'], 2)
                    if p < best_priority:
                        best_priority = p
                        best_object = data
                        best_distance = data['dist']
                    elif p == best_priority and data['dist'] < best_distance:
                        best_object = data
                        best_distance = data['dist']
                
                # ===== DETECT NEW OBJECTS =====
                best_new = None
                best_new_priority = 999
                
                for name in current_names:
                    self.persistence_counters[name] = self.persistence_counters.get(name, 0) + 1
                    
                    if self.persistence_counters[name] >= config.CONFIRM_THRESHOLD:
                        last_time = self.last_spoken.get(name, 0)
                        if now - last_time > config.COOLDOWN_TIME:
                            data = current[name]
                            p = config.PRIORITY_ORDER.get(data['priority'], 2)
                            if p < best_new_priority:
                                best_new_priority = p
                                best_new = data

                if best_new:
                    obj = best_new['obj']
                    dist = best_new['dist']
                    zone = best_new['zone']
                    
                    msg = f"{obj['alert']}, {dist:.0f}m, {zone}"
                    self.voice_engine.speak(msg)
                    self.log(f"🔔 ALERT: {obj['name']} ({dist:.0f}m)")
                    self.last_spoken[obj['name']] = now
                
                if best_object:
                    obj = best_object['obj']
                    dist = best_object['dist']
                    zone = best_object['zone']
                    
                    action = self.agent.get_action(obj['name'], dist, zone)
                    if action:
                        self.nav_label.config(text=action, fg=config.WARNING_COLOR)
                    
                    self.distance_label.config(text=f"{obj['name']}: {dist:.1f}m", fg=config.TEXT_COLOR)
                    
                    st_color = config.DANGER_COLOR if obj['priority'] == 'high' else config.WARNING_COLOR if obj['priority'] == 'medium' else config.SUCCESS_COLOR
                    self.status_label.config(text=f"● {obj['name'].upper()}", fg=st_color)
                
                left_objects = set(self.persistence_counters.keys()) - current_names
                for name in left_objects:
                    self.persistence_counters[name] = 0
                    if name in self.current_objects:
                        self.log(f"👋 {name} left")
                
                if not current_names:
                    self.nav_label.config(text="Path Clear", fg=config.SUCCESS_COLOR)
                    self.distance_label.config(text="--", fg=config.TEXT_COLOR)
                    self.status_label.config(text="● SCANNING", fg=config.PRIMARY_COLOR)
                
                self.current_objects = current
                
                if current_names:
                    room = self.agent.get_room(list(current_names))
                    if room != 'unknown':
                        self.status_label.config(text=f"📍 {room.upper()}", fg=config.PRIMARY_COLOR)
        
        if self.running:
            self.root.after(20, self.update_loop)


import threading
import time
from ultralytics import YOLO
import config
from depth_estimator import DepthEstimator

class DetectionEngine:
    def __init__(self, logger=None):
        self.logger = logger
        self.model = None
        self.running = False
        self.latest_frame = None
        self.detection_results = {}
        self.processing_lock = threading.Lock()
        
        # Initialize Depth Estimator
        self.depth_estimator = DepthEstimator(logger=logger)
        
    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(f"[DetectionEngine] {message}")
            
    def load_model(self):
        try:
            self.log("Loading YOLOv8 model...")
            self.model = YOLO(config.YOLO_MODEL_PATH)
            # Warm up
            import numpy as np
            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            self.model(dummy, verbose=False)
            self.log("✅ YOLOv8 model loaded successfully.")
            return True
        except Exception as e:
            self.log(f"❌ Error loading YOLO model: {e}")
            return False

    def start(self):
        if not self.model:
            if not self.load_model():
                return
        self.running = True
        threading.Thread(target=self.inference_worker, daemon=True).start()

    def stop(self):
        self.running = False

    def update_frame(self, frame):
        with self.processing_lock:
            self.latest_frame = frame

    def get_results(self):
        with self.processing_lock:
            return self.detection_results

    def get_zone(self, x_center, width):
        if x_center < width * 0.3:
            return "left"
        elif x_center > width * 0.7:
            return "right"
        return "center"

    def inference_worker(self):
        self.log("🚀 Inference Engine Started")
        while self.running:
            frame_to_process = None
            with self.processing_lock:
                if self.latest_frame is not None:
                    frame_to_process = self.latest_frame.copy()
            
            if frame_to_process is not None:
                h, w = frame_to_process.shape[:2]
                
                # RUN YOLO at lower resolution for massive CPU speedup
                results = self.model(frame_to_process, imgsz=320, verbose=False)
                
                current = {}
                needs_depth = False
                
                # First pass: check if we actually need to run depth estimation
                for box in results[0].boxes:
                    cid = int(box.cls[0])
                    conf = float(box.conf[0])
                    if cid in config.INDOOR_CLASSES and conf > 0.4:
                        needs_depth = True
                        break
                        
                depth_map = None
                if needs_depth:
                    # Lazy evaluation: Only run heavy MiDaS model if there's a priority object
                    depth_map = self.depth_estimator.estimate_depth(frame_to_process)
                
                for box in results[0].boxes:
                    cid = int(box.cls[0])
                    conf = float(box.conf[0])
                    if cid in config.INDOOR_CLASSES and conf > 0.4:
                        obj = config.INDOOR_CLASSES[cid]
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        dist = self.depth_estimator.get_object_distance(depth_map, (x1, y1, x2, y2))
                        
                        x_center = (x1+x2)/2
                        zone = self.get_zone(x_center, w)
                        
                        if obj['name'] not in current or dist < current[obj['name']]['dist']:
                            current[obj['name']] = {
                                'obj': obj, 'dist': dist, 'zone': zone, 
                                'priority': obj['priority'],
                                'box': (x1, y1, x2, y2), 'conf': conf
                            }
                
                with self.processing_lock:
                    self.detection_results = current
            
            time.sleep(0.2) # Throttled inference frees up CPU for Voice Commands

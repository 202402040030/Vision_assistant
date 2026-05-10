import torch
import cv2
import numpy as np

class DepthEstimator:
    def __init__(self, logger=None):
        self.logger = logger
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.log(f"Initializing MiDaS Depth Estimator on {self.device}...")
        
        try:
            # Load MiDaS Small for fast inference
            self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
            self.model.to(self.device)
            self.model.eval()

            # Load transforms to resize and normalize the image
            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
            self.transform = midas_transforms.small_transform
            
            self.log("✅ MiDaS Depth Estimator loaded successfully.")
            self.available = True
        except Exception as e:
            self.log(f"❌ Failed to load MiDaS model: {e}")
            self.available = False

    def log(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(f"[DepthEstimator] {message}")

    def estimate_depth(self, frame):
        """
        Calculates a depth map for the given frame.
        Returns the depth map as a numpy array, or None if failed.
        """
        if not self.available:
            return None
        
        try:
            # Convert BGR (OpenCV) to RGB
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Apply transforms
            input_batch = self.transform(img).to(self.device)
            
            # Prediction
            with torch.no_grad():
                prediction = self.model(input_batch)
                
                # Resize the prediction to match the original image resolution
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            
            # Return as numpy array
            output = prediction.cpu().numpy()
            return output
            
        except Exception as e:
            self.log(f"Depth estimation error: {e}")
            return None

    def get_object_distance(self, depth_map, box):
        """
        Given a bounding box (x1, y1, x2, y2), calculate the estimated real-world distance.
        Note: MiDaS outputs relative inverse depth.
        Higher value = closer. Lower value = further.
        We convert it to a pseudo-distance in meters for our logic.
        """
        if depth_map is None:
            return 6.0 # Default fallback distance
        
        x1, y1, x2, y2 = map(int, box)
        
        # Ensure coordinates are within bounds
        h, w = depth_map.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w-1, x2), min(h-1, y2)
        
        if x1 >= x2 or y1 >= y2:
            return 6.0
            
        # Get the ROI in the depth map
        roi_depth = depth_map[y1:y2, x1:x2]
        
        # Get median inverse depth to ignore outliers
        median_inv_depth = np.median(roi_depth)
        
        if median_inv_depth <= 0:
            return 6.0
            
        # Convert relative inverse depth to pseudo-meters
        # This is a heuristic calibration constant.
        # It needs tuning based on the camera, but provides consistent relative depth.
        CALIBRATION_CONSTANT = 500.0 
        distance = CALIBRATION_CONSTANT / median_inv_depth
        
        # Clamp between 0.1m and 10m
        distance = max(0.1, min(10.0, float(distance)))
        
        return distance

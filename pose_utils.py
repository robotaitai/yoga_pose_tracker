import json
import os
import numpy as np
import cv2
import mediapipe as mp
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class PoseDetector:
    """Handle pose detection using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def extract_keypoints(self, image: np.ndarray) -> Optional[Dict]:
        """
        Extract pose keypoints from image using MediaPipe
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary with keypoint coordinates or None if no pose detected
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.pose.process(rgb_image)
        
        if results.pose_landmarks:
            keypoints = {}
            
            # MediaPipe pose landmark indices
            landmark_names = [
                "nose", "left_eye_inner", "left_eye", "left_eye_outer",
                "right_eye_inner", "right_eye", "right_eye_outer",
                "left_ear", "right_ear", "mouth_left", "mouth_right",
                "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                "left_wrist", "right_wrist", "left_pinky", "right_pinky",
                "left_index", "right_index", "left_thumb", "right_thumb",
                "left_hip", "right_hip", "left_knee", "right_knee",
                "left_ankle", "right_ankle", "left_heel", "right_heel",
                "left_foot_index", "right_foot_index"
            ]
            
            # Extract coordinates (normalized 0-1)
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                if i < len(landmark_names):
                    keypoints[landmark_names[i]] = [landmark.x, landmark.y]
                    
            return keypoints
        
        return None
    
    def draw_landmarks(self, image: np.ndarray, keypoints: Dict) -> np.ndarray:
        """
        Draw pose landmarks on image for visualization
        
        Args:
            image: Input image
            keypoints: Dictionary of keypoints
            
        Returns:
            Image with landmarks drawn
        """
        # This is a simplified drawing - MediaPipe's built-in drawing is more comprehensive
        for name, coords in keypoints.items():
            if coords:
                x = int(coords[0] * image.shape[1])
                y = int(coords[1] * image.shape[0])
                cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
                
        return image


class PoseComparator:
    """Handle pose comparison and similarity calculations"""
    
    def __init__(self, similarity_threshold: float = 0.15):
        """
        Initialize pose comparator
        
        Args:
            similarity_threshold: Threshold for determining valid pose matches (lower = more strict)
        """
        self.similarity_threshold = similarity_threshold
        
        # Key joints for pose comparison (focusing on main body structure)
        self.key_joints = [
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ]
    
    def normalize_pose(self, keypoints: Dict) -> Dict:
        """
        Normalize pose by centering around hip midpoint and scaling
        
        Args:
            keypoints: Raw keypoints dictionary
            
        Returns:
            Normalized keypoints dictionary
        """
        if not keypoints or "left_hip" not in keypoints or "right_hip" not in keypoints:
            return keypoints
            
        # Calculate hip center as reference point
        left_hip = np.array(keypoints["left_hip"])
        right_hip = np.array(keypoints["right_hip"])
        hip_center = (left_hip + right_hip) / 2
        
        # Calculate torso length for scaling
        if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            left_shoulder = np.array(keypoints["left_shoulder"])
            right_shoulder = np.array(keypoints["right_shoulder"])
            shoulder_center = (left_shoulder + right_shoulder) / 2
            
            torso_length = np.linalg.norm(shoulder_center - hip_center)
            if torso_length == 0:
                torso_length = 1.0
        else:
            torso_length = 1.0
        
        # Normalize all keypoints
        normalized = {}
        for joint, coords in keypoints.items():
            if coords:
                normalized_coords = (np.array(coords) - hip_center) / torso_length
                normalized[joint] = normalized_coords.tolist()
            else:
                normalized[joint] = coords
                
        return normalized
    
    def calculate_pose_similarity(self, pose1: Dict, pose2: Dict) -> float:
        """
        Calculate similarity between two poses using joint distances
        
        Args:
            pose1: First pose keypoints
            pose2: Second pose keypoints
            
        Returns:
            Similarity score (lower = more similar)
        """
        if not pose1 or not pose2:
            return float('inf')
        
        # Normalize both poses
        norm_pose1 = self.normalize_pose(pose1)
        norm_pose2 = self.normalize_pose(pose2)
        
        distances = []
        
        for joint in self.key_joints:
            if joint in norm_pose1 and joint in norm_pose2:
                if norm_pose1[joint] and norm_pose2[joint]:
                    p1 = np.array(norm_pose1[joint])
                    p2 = np.array(norm_pose2[joint])
                    distance = np.linalg.norm(p1 - p2)
                    distances.append(distance)
        
        if not distances:
            return float('inf')
            
        # Return mean squared error
        return np.mean(np.array(distances) ** 2)
    
    def find_best_pose_match(self, current_pose: Dict, reference_poses: Dict) -> Tuple[str, float]:
        """
        Find the best matching reference pose
        
        Args:
            current_pose: Current detected pose keypoints
            reference_poses: Dictionary of reference poses {pose_name: [pose_variations]}
            
        Returns:
            Tuple of (best_pose_name, similarity_score)
        """
        best_pose = "unknown"
        best_score = float('inf')
        
        for pose_name, pose_variations in reference_poses.items():
            for variation in pose_variations:
                if "keypoints" in variation:
                    score = self.calculate_pose_similarity(current_pose, variation["keypoints"])
                    if score < best_score:
                        best_score = score
                        best_pose = pose_name
        
        # Check if similarity is good enough
        if best_score > self.similarity_threshold:
            return "unknown", best_score
            
        return best_pose, best_score


class PoseDataManager:
    """Handle loading and saving pose data"""
    
    def __init__(self, positions_dir: str = "positions", sessions_dir: str = "sessions"):
        self.positions_dir = positions_dir
        self.sessions_dir = sessions_dir
        
        # Ensure directories exist
        os.makedirs(positions_dir, exist_ok=True)
        os.makedirs(sessions_dir, exist_ok=True)
    
    def load_reference_poses(self) -> Dict:
        """
        Load all reference poses from positions directory
        
        Returns:
            Dictionary of reference poses {pose_name: [pose_variations]}
        """
        reference_poses = {}
        
        if not os.path.exists(self.positions_dir):
            return reference_poses
            
        for pose_folder in os.listdir(self.positions_dir):
            pose_path = os.path.join(self.positions_dir, pose_folder)
            
            if os.path.isdir(pose_path):
                pose_variations = []
                
                for json_file in os.listdir(pose_path):
                    if json_file.endswith('.json'):
                        json_path = os.path.join(pose_path, json_file)
                        try:
                            with open(json_path, 'r') as f:
                                pose_data = json.load(f)
                                pose_variations.append(pose_data)
                        except Exception as e:
                            print(f"Error loading {json_path}: {e}")
                
                if pose_variations:
                    reference_poses[pose_folder] = pose_variations
        
        return reference_poses
    
    def save_session_data(self, session_data: Dict) -> str:
        """
        Save session data to JSON file
        
        Args:
            session_data: Session data to save
            
        Returns:
            Filename of saved session
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"session_{timestamp}.json"
        filepath = os.path.join(self.sessions_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"Session data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving session data: {e}")
            return ""
    
    def save_reference_pose(self, pose_name: str, keypoints: Dict, filename: str = "ref1.json") -> bool:
        """
        Save a reference pose to the positions directory
        
        Args:
            pose_name: Name of the pose
            keypoints: Keypoints dictionary
            filename: Name of the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        pose_dir = os.path.join(self.positions_dir, pose_name)
        os.makedirs(pose_dir, exist_ok=True)
        
        pose_data = {
            "pose_name": pose_name,
            "keypoints": keypoints
        }
        
        filepath = os.path.join(pose_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(pose_data, f, indent=2)
            print(f"Reference pose saved: {pose_name}/{filename}")
            return True
        except Exception as e:
            print(f"Error saving reference pose: {e}")
            return False


def capture_reference_pose(pose_name: str, data_manager: PoseDataManager) -> bool:
    """
    Helper function to capture a reference pose from webcam
    
    Args:
        pose_name: Name of the pose to capture
        data_manager: PoseDataManager instance
        
    Returns:
        True if pose was captured successfully
    """
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False
    
    print(f"Capturing reference pose: {pose_name}")
    print("Position yourself in the pose and press SPACE to capture, or ESC to cancel")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Extract keypoints
        keypoints = detector.extract_keypoints(frame)
        
        if keypoints:
            # Draw landmarks
            frame = detector.draw_landmarks(frame, keypoints)
            cv2.putText(frame, f"Pose: {pose_name} - Press SPACE to capture", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No pose detected", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow("Capture Reference Pose", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and keypoints:  # Space to capture
            success = data_manager.save_reference_pose(pose_name, keypoints)
            cap.release()
            cv2.destroyAllWindows()
            return success
        elif key == 27:  # ESC to cancel
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return False 
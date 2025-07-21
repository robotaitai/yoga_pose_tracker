#!/usr/bin/env python3
"""
Yoga Pose Database - Optimized Pose Reference System

Fast pose lookup system for real-time yoga pose tracking.
Loads processed pose data and provides efficient similarity matching.
"""

import json
import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import time


class OptimizedPoseDatabase:
    """
    Optimized pose database for fast lookup during live tracking
    
    Features:
    - Pre-computed normalized poses for faster comparison
    - Indexed keypoints for quick access
    - Cached similarity calculations
    - Multiple reference poses per pose type
    """
    
    def __init__(self, database_path: str = "pose_database/pose_database.json", 
                 similarity_threshold: float = 0.15):
        """
        Initialize the optimized pose database
        
        Args:
            database_path: Path to the consolidated pose database JSON
            similarity_threshold: Threshold for pose matching
        """
        self.database_path = database_path
        self.similarity_threshold = similarity_threshold
        
        # Key joints for comparison (focusing on main body structure)
        self.key_joints = [
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_hip", "right_hip",
            "left_knee", "right_knee", "left_ankle", "right_ankle"
        ]
        
        # Storage for processed poses
        self.pose_database = {}
        self.normalized_poses = {}
        self.pose_stats = {}
        
        # Performance tracking
        self.lookup_count = 0
        self.total_lookup_time = 0.0
        
        # Load the database
        self.load_database()
    
    def load_database(self) -> bool:
        """
        Load and preprocess the pose database
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.database_path):
                print(f"⚠️  Database file not found: {self.database_path}")
                print("Run: python process_images.py to create the database")
                return False
            
            print(f"📖 Loading pose database from: {self.database_path}")
            
            with open(self.database_path, 'r') as f:
                database_info = json.load(f)
            
            if "pose_data" not in database_info:
                print("❌ Invalid database format")
                return False
            
            self.pose_database = database_info["pose_data"]
            
            # Preprocess all poses for faster lookup
            self._preprocess_poses()
            
            # Print database info
            total_variations = sum(len(variations) for variations in self.pose_database.values())
            print(f"✅ Loaded {len(self.pose_database)} pose types")
            print(f"✅ Total variations: {total_variations}")
            
            # Print pose statistics
            for pose_name, stats in self.pose_stats.items():
                print(f"  - {pose_name}: {stats['count']} variations, "
                      f"avg {stats['avg_keypoints']:.1f} keypoints")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return False
    
    def _preprocess_poses(self):
        """Preprocess poses for faster matching"""
        print("🔧 Preprocessing poses for optimal performance...")
        
        self.normalized_poses = {}
        self.pose_stats = {}
        
        for pose_name, variations in self.pose_database.items():
            normalized_variations = []
            keypoint_counts = []
            
            for variation in variations:
                if "keypoints" in variation:
                    # Normalize the pose
                    normalized = self._normalize_pose(variation["keypoints"])
                    if normalized:
                        normalized_variations.append({
                            "normalized_keypoints": normalized,
                            "source": variation.get("source_image", "unknown"),
                            "keypoint_count": variation.get("keypoint_count", 0)
                        })
                        keypoint_counts.append(variation.get("keypoint_count", 0))
            
            if normalized_variations:
                self.normalized_poses[pose_name] = normalized_variations
                self.pose_stats[pose_name] = {
                    "count": len(normalized_variations),
                    "avg_keypoints": np.mean(keypoint_counts) if keypoint_counts else 0
                }
        
        print(f"✅ Preprocessed {len(self.normalized_poses)} pose types")
    
    def _normalize_pose(self, keypoints: Dict) -> Optional[Dict]:
        """
        Normalize pose by centering around hip midpoint and scaling
        
        Args:
            keypoints: Raw keypoints dictionary
            
        Returns:
            Normalized keypoints dictionary or None if invalid
        """
        if not keypoints or "left_hip" not in keypoints or "right_hip" not in keypoints:
            return None
        
        # Check if hip keypoints are valid
        left_hip = keypoints.get("left_hip")
        right_hip = keypoints.get("right_hip")
        
        if not left_hip or not right_hip:
            return None
        
        # Calculate hip center as reference point
        left_hip = np.array(left_hip)
        right_hip = np.array(right_hip)
        hip_center = (left_hip + right_hip) / 2
        
        # Calculate torso length for scaling
        left_shoulder = keypoints.get("left_shoulder")
        right_shoulder = keypoints.get("right_shoulder")
        
        if left_shoulder and right_shoulder:
            left_shoulder = np.array(left_shoulder)
            right_shoulder = np.array(right_shoulder)
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
                normalized[joint] = None
                
        return normalized
    
    def _calculate_pose_similarity(self, pose1: Dict, pose2: Dict) -> float:
        """
        Calculate similarity between two normalized poses
        
        Args:
            pose1: First normalized pose keypoints
            pose2: Second normalized pose keypoints
            
        Returns:
            Similarity score (lower = more similar)
        """
        if not pose1 or not pose2:
            return float('inf')
        
        distances = []
        
        for joint in self.key_joints:
            if joint in pose1 and joint in pose2:
                if pose1[joint] and pose2[joint]:
                    p1 = np.array(pose1[joint])
                    p2 = np.array(pose2[joint])
                    distance = np.linalg.norm(p1 - p2)
                    distances.append(distance)
        
        if not distances:
            return float('inf')
            
        # Return mean squared error
        return np.mean(np.array(distances) ** 2)
    
    def find_best_pose_match(self, current_keypoints: Dict) -> Tuple[str, float, Dict]:
        """
        Find the best matching pose from the database
        
        Args:
            current_keypoints: Current detected pose keypoints
            
        Returns:
            Tuple of (pose_name, similarity_score, match_info)
        """
        start_time = time.time()
        
        # Normalize current pose
        normalized_current = self._normalize_pose(current_keypoints)
        if not normalized_current:
            return "unknown", float('inf'), {}
        
        best_pose = "unknown"
        best_score = float('inf')
        best_match_info = {}
        
        # Compare against all poses in database
        for pose_name, variations in self.normalized_poses.items():
            for variation in variations:
                score = self._calculate_pose_similarity(
                    normalized_current, 
                    variation["normalized_keypoints"]
                )
                
                if score < best_score:
                    best_score = score
                    best_pose = pose_name
                    best_match_info = {
                        "source_image": variation["source"],
                        "reference_keypoints": variation["keypoint_count"],
                        "detected_keypoints": len([k for k, v in current_keypoints.items() if v is not None])
                    }
        
        # Check if similarity is good enough
        if best_score > self.similarity_threshold:
            best_pose = "unknown"
        
        # Update performance stats
        lookup_time = time.time() - start_time
        self.lookup_count += 1
        self.total_lookup_time += lookup_time
        
        return best_pose, best_score, best_match_info
    
    def get_pose_info(self, pose_name: str) -> Dict:
        """
        Get information about a specific pose
        
        Args:
            pose_name: Name of the pose
            
        Returns:
            Dictionary with pose information
        """
        if pose_name not in self.pose_stats:
            return {}
        
        return {
            "name": pose_name,
            "variations": self.pose_stats[pose_name]["count"],
            "avg_keypoints": self.pose_stats[pose_name]["avg_keypoints"],
            "available": True
        }
    
    def get_all_pose_names(self) -> List[str]:
        """Get list of all available pose names"""
        return list(self.pose_database.keys())
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        avg_lookup_time = (self.total_lookup_time / self.lookup_count 
                          if self.lookup_count > 0 else 0)
        
        return {
            "total_lookups": self.lookup_count,
            "total_time": self.total_lookup_time,
            "avg_lookup_time_ms": avg_lookup_time * 1000,
            "lookups_per_second": self.lookup_count / self.total_lookup_time if self.total_lookup_time > 0 else 0
        }
    
    def is_loaded(self) -> bool:
        """Check if database is loaded"""
        return len(self.pose_database) > 0


def load_fallback_poses(positions_dir: str = "positions") -> Dict:
    """
    Fallback function to load poses from individual JSON files
    (compatible with original system)
    
    Args:
        positions_dir: Directory containing pose folders
        
    Returns:
        Dictionary of poses in the original format
    """
    reference_poses = {}
    
    if not os.path.exists(positions_dir):
        return reference_poses
        
    for pose_folder in os.listdir(positions_dir):
        pose_path = os.path.join(positions_dir, pose_folder)
        
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
                        print(f"Warning: Error loading {json_path}: {e}")
            
            if pose_variations:
                reference_poses[pose_folder] = pose_variations
    
    return reference_poses


# Example usage and testing
if __name__ == "__main__":
    print("🧘 Testing Optimized Pose Database")
    print("=" * 40)
    
    # Initialize database
    db = OptimizedPoseDatabase()
    
    if db.is_loaded():
        print(f"\n📊 Database Statistics:")
        print(f"Available poses: {', '.join(db.get_all_pose_names())}")
        
        # Test performance
        print(f"\n🔬 Performance Test:")
        dummy_keypoints = {
            "left_shoulder": [0.4, 0.3],
            "right_shoulder": [0.6, 0.3],
            "left_hip": [0.43, 0.52],
            "right_hip": [0.57, 0.52],
            "left_knee": [0.42, 0.7],
            "right_knee": [0.58, 0.7]
        }
        
        # Run multiple lookups to test performance
        for i in range(10):
            pose, score, info = db.find_best_pose_match(dummy_keypoints)
        
        stats = db.get_performance_stats()
        print(f"Average lookup time: {stats['avg_lookup_time_ms']:.2f}ms")
        print(f"Lookups per second: {stats['lookups_per_second']:.1f}")
    else:
        print("❌ Database not loaded. Run process_images.py first.") 
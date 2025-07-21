#!/usr/bin/env python3
"""
Image Processing Script for Yoga Pose Database

This script processes static images in the positions/ directory to create
reference pose data for the yoga tracker system.

Usage:
    python scripts/process_images.py
    
Features:
- Processes all images in positions/ subdirectories
- Extracts pose keypoints using MediaPipe
- Creates individual JSON files for each pose
- Builds optimized pose database for fast lookup
- Validates pose quality and provides feedback
"""

import os
import sys
import cv2
import json
import numpy as np
from datetime import datetime

# Add parent directory to path to import yoga modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mediapipe as mp
from pose_utils import PoseDetector


class PoseImageProcessor:
    """Process static images to extract pose keypoints"""
    
    def __init__(self):
        # Initialize MediaPipe with static image settings for better accuracy
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,          # Process static images
            model_complexity=2,              # Highest accuracy model
            enable_segmentation=False,       # Don't need segmentation
            min_detection_confidence=0.7,    # Higher confidence threshold
            min_tracking_confidence=0.5
        )
        self.detector = PoseDetector()
        
    def process_image(self, image_path):
        """Extract keypoints from a single image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Could not load image: {image_path}")
                return None
            
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                # Extract keypoints in our standard format
                keypoints = {}
                for idx, landmark in enumerate(results.pose_landmarks.landmark):
                    keypoints[idx] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
                
                # Calculate pose quality metrics
                quality_score = self._calculate_pose_quality(keypoints)
                
                print(f"✅ Processed {os.path.basename(image_path)}: {len(keypoints)} keypoints, quality: {quality_score:.2f}")
                
                return {
                    "keypoints": keypoints,
                    "image_path": image_path,
                    "quality_score": quality_score,
                    "timestamp": datetime.now().isoformat(),
                    "image_dimensions": {
                        "width": image.shape[1],
                        "height": image.shape[0]
                    }
                }
            else:
                print(f"⚠️  No pose detected in {os.path.basename(image_path)}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            return None
    
    def _calculate_pose_quality(self, keypoints):
        """Calculate pose quality based on visibility and completeness"""
        if not keypoints:
            return 0.0
        
        # Count visible keypoints (visibility > 0.5)
        visible_count = sum(1 for kp in keypoints.values() if kp['visibility'] > 0.5)
        total_count = len(keypoints)
        
        # Calculate average visibility
        avg_visibility = sum(kp['visibility'] for kp in keypoints.values()) / total_count
        
        # Quality score combines completeness and visibility
        completeness = visible_count / total_count
        quality = (completeness * 0.7) + (avg_visibility * 0.3)
        
        return quality


def process_poses_directory(base_dir="positions"):
    """Process all pose images in the positions directory"""
    
    if not os.path.exists(base_dir):
        print(f"❌ Directory '{base_dir}' not found!")
        print("💡 Make sure you have a 'positions' directory with pose images")
        return
    
    processor = PoseImageProcessor()
    all_poses = {}
    
    print("🔍 Scanning for pose images...")
    
    # Process each pose type directory
    for pose_dir in os.listdir(base_dir):
        pose_path = os.path.join(base_dir, pose_dir)
        
        if not os.path.isdir(pose_path):
            continue
        
        print(f"\n📁 Processing pose: {pose_dir}")
        
        pose_variations = []
        image_files = [f for f in os.listdir(pose_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        
        if not image_files:
            print(f"⚠️  No image files found in {pose_path}")
            continue
        
        for image_file in sorted(image_files):
            image_path = os.path.join(pose_path, image_file)
            print(f"   Processing: {image_file}")
            
            pose_data = processor.process_image(image_path)
            if pose_data:
                pose_variations.append(pose_data)
                
                # Save individual JSON file
                json_filename = os.path.splitext(image_file)[0] + '.json'
                json_path = os.path.join(pose_path, json_filename)
                
                with open(json_path, 'w') as f:
                    json.dump(pose_data, f, indent=2)
                
                print(f"   💾 Saved: {json_filename}")
        
        if pose_variations:
            all_poses[pose_dir] = pose_variations
            print(f"✅ {pose_dir}: {len(pose_variations)} variations processed")
        else:
            print(f"❌ {pose_dir}: No valid poses found")
    
    return all_poses


def create_optimized_database(all_poses):
    """Create optimized pose database for fast lookup"""
    
    if not all_poses:
        print("❌ No pose data to create database")
        return
    
    print("\n🔧 Creating optimized pose database...")
    
    # Create database directory
    db_dir = "pose_database"
    os.makedirs(db_dir, exist_ok=True)
    
    # Prepare database structure
    database = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "total_poses": len(all_poses),
            "total_variations": sum(len(variations) for variations in all_poses.values())
        },
        "poses": all_poses
    }
    
    # Save consolidated database
    db_path = os.path.join(db_dir, "pose_database.json")
    with open(db_path, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"💾 Database saved: {db_path}")
    
    # Print statistics
    print("\n📊 Database Statistics:")
    for pose_name, variations in all_poses.items():
        avg_quality = sum(v['quality_score'] for v in variations) / len(variations)
        avg_keypoints = sum(len(v['keypoints']) for v in variations) / len(variations)
        print(f"   {pose_name}: {len(variations)} variations, avg quality: {avg_quality:.2f}, avg keypoints: {avg_keypoints:.1f}")
    
    return db_path


def main():
    """Main image processing function"""
    
    print("=" * 60)
    print("🧘 YOGA POSE DATABASE BUILDER")
    print("=" * 60)
    print("📸 Processing reference images to create pose database")
    print("🎯 Extracting keypoints for pose recognition")
    print("=" * 60)
    
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Process all pose images
    all_poses = process_poses_directory()
    
    if all_poses:
        # Create optimized database
        db_path = create_optimized_database(all_poses)
        
        print("\n🎉 Pose database creation completed!")
        print(f"✅ Total pose types: {len(all_poses)}")
        print(f"✅ Total variations: {sum(len(variations) for variations in all_poses.values())}")
        print(f"💾 Database location: {db_path}")
        print("\n🚀 Ready to use with yoga_coach.py!")
        
    else:
        print("\n❌ No pose data was processed")
        print("💡 Make sure you have:")
        print("   1. A 'positions' directory")
        print("   2. Subdirectories for each pose type")
        print("   3. Image files in each pose subdirectory")
        print("\nExample structure:")
        print("positions/")
        print("├── tree_pose/")
        print("│   ├── tree1.jpg")
        print("│   └── tree2.png")
        print("├── warrior_2/")
        print("│   ├── warrior1.jpg")
        print("│   └── warrior2.png")
        print("└── downward_dog/")
        print("    ├── dog1.jpg")
        print("    └── dog2.png")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Debug Tool for Pose Recognition Issues

This tool helps diagnose why poses might not be recognized properly.
It checks the pose database, analyzes image quality, and provides
troubleshooting information.

Usage:
    python tests/debug_poses.py
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import yoga modules  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from pose_database import OptimizedPoseDatabase
    from pose_utils import PoseDataManager
    from angle_analyzer import PostureAnalyzer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the project root directory")
    sys.exit(1)


def check_pose_database():
    """Check if pose database exists and is valid"""
    print("🔍 Checking pose database...")
    
    # Check for optimized database
    optimized_db = OptimizedPoseDatabase()
    if optimized_db.is_loaded():
        print("✅ Optimized pose database found and loaded")
        
        # Get database info
        pose_types = optimized_db.get_pose_types()
        print(f"📊 Available pose types: {len(pose_types)}")
        for pose_type in pose_types:
            count = len(optimized_db.poses[pose_type])
            print(f"   - {pose_type}: {count} variations")
        
        return True
    else:
        print("❌ Optimized pose database not found")
        
        # Check for fallback system
        print("🔍 Checking fallback pose system...")
        data_manager = PoseDataManager()
        reference_poses = data_manager.load_reference_poses()
        
        if reference_poses:
            print("✅ Fallback reference poses found")
            print(f"📊 Available poses: {len(reference_poses)}")
            for pose_name, pose_data in reference_poses.items():
                print(f"   - {pose_name}: {len(pose_data)} variations")
            return True
        else:
            print("❌ No reference poses found")
            return False


def check_positions_directory():
    """Check the positions directory structure"""
    print("\n🔍 Checking positions directory...")
    
    positions_dir = Path("positions")
    if not positions_dir.exists():
        print("❌ 'positions' directory not found")
        print("💡 Create a 'positions' directory and add pose images")
        return False
    
    print("✅ 'positions' directory found")
    
    # Check subdirectories
    pose_dirs = [d for d in positions_dir.iterdir() if d.is_dir()]
    if not pose_dirs:
        print("❌ No pose subdirectories found in 'positions'")
        print("💡 Create subdirectories for each pose type (e.g., tree_pose, warrior_2)")
        return False
    
    print(f"📁 Found {len(pose_dirs)} pose directories:")
    
    total_images = 0
    for pose_dir in pose_dirs:
        # Count image files
        image_files = list(pose_dir.glob("*.jpg")) + list(pose_dir.glob("*.png")) + \
                     list(pose_dir.glob("*.jpeg")) + list(pose_dir.glob("*.bmp"))
        
        json_files = list(pose_dir.glob("*.json"))
        
        print(f"   📁 {pose_dir.name}:")
        print(f"      🖼️  Images: {len(image_files)}")
        print(f"      📄 JSON files: {len(json_files)}")
        
        if len(image_files) == 0:
            print(f"      ⚠️  No images found in {pose_dir.name}")
        elif len(json_files) == 0:
            print(f"      💡 Images found but no JSON files - run 'python scripts/process_images.py'")
        
        total_images += len(image_files)
    
    print(f"\n📊 Total images: {total_images}")
    return total_images > 0


def check_angle_analyzer():
    """Check if angle analyzer is working"""
    print("\n🔍 Checking angle analyzer...")
    
    try:
        analyzer = PostureAnalyzer()
        print("✅ PostureAnalyzer initialized successfully")
        
        # Check available pose types
        available_poses = ["tree_pose", "warrior_2", "downward_dog"]
        supported_poses = []
        
        for pose in available_poses:
            # Create dummy keypoints to test
            dummy_keypoints = {i: {'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 0.9} for i in range(33)}
            
            try:
                analyses = analyzer.analyze_pose(pose, dummy_keypoints)
                if analyses:
                    supported_poses.append(pose)
                    print(f"   ✅ {pose}: {len(analyses)} angle checks available")
            except Exception as e:
                print(f"   ❌ {pose}: Error - {e}")
        
        print(f"\n📊 Supported poses: {len(supported_poses)}/{len(available_poses)}")
        return len(supported_poses) > 0
        
    except Exception as e:
        print(f"❌ PostureAnalyzer error: {e}")
        return False


def analyze_pose_quality():
    """Analyze quality of processed poses"""
    print("\n🔍 Analyzing pose quality...")
    
    # Check if pose database exists
    db_path = Path("pose_database/pose_database.json")
    if not db_path.exists():
        print("❌ Pose database not found")
        print("💡 Run 'python scripts/process_images.py' to create database")
        return
    
    try:
        with open(db_path, 'r') as f:
            database = json.load(f)
        
        poses = database.get('poses', {})
        if not poses:
            print("❌ No poses found in database")
            return
        
        print("✅ Pose database loaded")
        print("\n📊 Quality Analysis:")
        
        for pose_name, variations in poses.items():
            if not variations:
                continue
            
            qualities = [v.get('quality_score', 0) for v in variations]
            keypoint_counts = [len(v.get('keypoints', {})) for v in variations]
            
            avg_quality = sum(qualities) / len(qualities)
            avg_keypoints = sum(keypoint_counts) / len(keypoint_counts)
            
            quality_status = "🟢" if avg_quality > 0.8 else "🟡" if avg_quality > 0.6 else "🔴"
            
            print(f"   {quality_status} {pose_name}:")
            print(f"      Variations: {len(variations)}")
            print(f"      Avg Quality: {avg_quality:.2f}")
            print(f"      Avg Keypoints: {avg_keypoints:.1f}")
            
            # Identify low quality variations
            low_quality = [i for i, q in enumerate(qualities) if q < 0.6]
            if low_quality:
                print(f"      ⚠️  Low quality variations: {len(low_quality)}")
    
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")


def provide_recommendations():
    """Provide recommendations for improving pose recognition"""
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 50)
    
    # Check if database exists
    if not Path("pose_database/pose_database.json").exists():
        print("1. 🔧 CREATE POSE DATABASE:")
        print("   Run: python scripts/process_images.py")
        print("")
    
    # Check positions directory
    if not Path("positions").exists():
        print("2. 📁 CREATE POSITIONS DIRECTORY:")
        print("   mkdir positions")
        print("   mkdir positions/tree_pose")
        print("   mkdir positions/warrior_2")
        print("   mkdir positions/downward_dog")
        print("")
    
    print("3. 📸 IMAGE QUALITY TIPS:")
    print("   - Use clear, well-lit photos")
    print("   - Ensure full body is visible")
    print("   - Avoid cluttered backgrounds")
    print("   - Include multiple angles/variations")
    print("")
    
    print("4. 🎯 IMPROVE RECOGNITION:")
    print("   - Add more reference images per pose")
    print("   - Remove low-quality images")
    print("   - Ensure poses are performed correctly")
    print("")
    
    print("5. 🚀 RUN THE SYSTEM:")
    print("   python yoga_coach.py")


def main():
    """Main debug function"""
    print("=" * 60)
    print("🧘 YOGA POSE RECOGNITION DEBUG TOOL")
    print("=" * 60)
    print("🔍 Diagnosing pose recognition issues...")
    print("=" * 60)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Run all checks
    database_ok = check_pose_database()
    positions_ok = check_positions_directory() 
    analyzer_ok = check_angle_analyzer()
    
    if database_ok:
        analyze_pose_quality()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS SUMMARY:")
    print("=" * 60)
    
    print(f"Pose Database: {'✅' if database_ok else '❌'}")
    print(f"Positions Directory: {'✅' if positions_ok else '❌'}")
    print(f"Angle Analyzer: {'✅' if analyzer_ok else '❌'}")
    
    if database_ok and positions_ok and analyzer_ok:
        print("\n🎉 All systems appear to be working!")
        print("🚀 Ready to run: python yoga_coach.py")
    else:
        print(f"\n⚠️  Issues detected - see recommendations below")
    
    provide_recommendations()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
🧘 PERFORMANCE-FOCUSED YOGA COACH 🧘

Your Personal AI Yoga Instructor with Performance Tracking

Features:
- Real-time pose detection with confidence thresholds
- Performance-focused narrator (only speaks on achievements)
- Historical angle comparison and tracking
- Personal best and daily best tracking
- Data-driven feedback based on your progress
- YAML configuration for customization

Usage:
    python yoga_coach_performance.py

The narrator will only speak when:
- Pose is detected with high confidence (configurable)
- You achieve a personal best angle
- You achieve a daily best angle  
- You show significant improvement vs your average
"""

import cv2
import time
import yaml
from datetime import datetime
from pose_utils import PoseDetector, PoseComparator, PoseDataManager
from pose_database import OptimizedPoseDatabase
from angle_analyzer import PostureAnalyzer
from performance_narrator import PerformanceNarrator


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found, using defaults")
        return default_config()


def default_config() -> dict:
    """Default configuration"""
    return {
        'pose_detection': {
            'similarity_threshold': 0.20,
            'confidence_threshold': 0.85,
            'min_hold_time': 3.0
        },
        'narrator': {
            'enabled': True,
            'speech_rate': 180,
            'feedback_cooldown': 10.0
        }
    }


def main():
    """Main application - Performance-Focused Yoga Coach"""
    
    print("=" * 70)
    print("🧘 PERFORMANCE-FOCUSED YOGA COACH 🧘")
    print("=" * 70)
    print("🎯 Data-driven feedback based on your progress")
    print("📊 Tracks personal bests and improvements")
    print("🔊 Only speaks on achievements and milestones")
    print("📐 Measures critical angles vs your history")
    print("=" * 70)
    
    # Load configuration
    config = load_config()
    print("⚙️  Loading configuration...")
    
    # Initialize core components
    print("Initializing yoga coaching system...")
    detector = PoseDetector()
    data_manager = PoseDataManager()
    posture_analyzer = PostureAnalyzer()
    
    # Initialize performance narrator
    print("🔊 Initializing performance narrator...")
    narrator = PerformanceNarrator()
    
    # Load pose database with configured threshold
    print("📖 Loading pose database...")
    similarity_threshold = config['pose_detection']['similarity_threshold']
    optimized_db = OptimizedPoseDatabase(similarity_threshold=similarity_threshold)
    use_optimized = optimized_db.is_loaded()
    
    if use_optimized:
        print("✅ Using optimized pose database")
        reference_poses = None
        comparator = None
    else:
        print("⚠️  Using fallback reference system")
        comparator = PoseComparator(similarity_threshold=similarity_threshold)
        reference_poses = data_manager.load_reference_poses()
        
        if not reference_poses:
            print("❌ No reference poses found!")
            print("💡 Run 'python scripts/process_images.py' to create pose database")
            return
    
    # Initialize webcam
    print("📹 Starting webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open webcam!")
        return
    
    # Configure webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Session initialization
    session_start = datetime.now()
    session_data = {
        "session_start": session_start.strftime("%Y-%m-%d %H:%M:%S"),
        "frames": []
    }
    
    frame_count = 0
    last_pose = ""
    last_pose_time = time.time()
    
    print("\n🚀 STARTING PERFORMANCE-TRACKING SESSION")
    print("=" * 70)
    print("📹 Position yourself in front of the camera")
    print("🎯 Hold poses confidently to trigger performance analysis")
    print("🏆 Narrator will celebrate your improvements and personal bests")
    print("⌨️  Press 'q' in the camera window to finish")
    print("=" * 70)
    print(f"🔧 Configuration:")
    print(f"   - Confidence threshold: {config['pose_detection']['confidence_threshold']:.0%}")
    print(f"   - Min hold time: {config['pose_detection']['min_hold_time']}s")
    print(f"   - Feedback cooldown: {config['narrator']['feedback_cooldown']}s")
    print("=" * 70)
    print()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read from camera")
                break
            
            # Mirror the frame for natural movement
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            # Initialize frame variables
            detected_pose = "unknown"
            similarity_score = float('inf')
            analyses = None
            
            # Extract pose keypoints
            keypoints = detector.extract_keypoints(frame)
            
            current_time = time.time()
            elapsed_minutes = int((current_time - time.mktime(session_start.timetuple())) // 60)
            elapsed_seconds = int((current_time - time.mktime(session_start.timetuple())) % 60)
            
            # Pose detection and analysis
            if keypoints and (reference_poses or use_optimized):
                # Find best matching pose
                if use_optimized:
                    detected_pose, similarity_score, match_info = optimized_db.find_best_pose_match(keypoints)
                elif reference_poses and comparator:
                    detected_pose, similarity_score = comparator.find_best_pose_match(keypoints, reference_poses)
                else:
                    detected_pose = "unknown"
                    similarity_score = float('inf')
                
                # Draw pose landmarks on video
                frame = detector.draw_landmarks(frame, keypoints)
                
                # Calculate confidence for display
                confidence = 1.0 - similarity_score if similarity_score != float('inf') else 0.0
                
                # Display pose information with confidence
                pose_text = f"Pose: {detected_pose}"
                if detected_pose != "unknown":
                    pose_text += f" (Confidence: {confidence:.0%})"
                
                # Color code based on confidence threshold
                conf_threshold = config['pose_detection']['confidence_threshold']
                color = (0, 255, 0) if confidence >= conf_threshold else (0, 255, 255)
                
                cv2.putText(frame, pose_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Analyze pose for angle measurements
                if detected_pose != "unknown" and keypoints:
                    analyses = posture_analyzer.analyze_pose(detected_pose, keypoints)
                    if analyses:
                        # Calculate overall form score
                        score, grade = posture_analyzer.get_overall_score(analyses)
                        
                        # Display form score on video
                        score_text = f"Form: {score:.1f}% ({grade})"
                        cv2.putText(frame, score_text, (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Performance narrator analysis (only speaks on achievements)
                        feedback_given = narrator.analyze_pose(
                            detected_pose, similarity_score, analyses, keypoints
                        )
                        
                        # Show feedback indicator on screen
                        if feedback_given:
                            cv2.putText(frame, "🎯 ACHIEVEMENT!", (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Console output (simplified - focus on performance)
                if detected_pose != last_pose or (current_time - last_pose_time) > 10.0:
                    timestamp_str = f"[{elapsed_minutes:02d}:{elapsed_seconds:02d}]"
                    if detected_pose != "unknown":
                        conf_indicator = "🎯" if confidence >= conf_threshold else "📊"
                        print(f"{timestamp_str} {conf_indicator} {detected_pose.replace('_', ' ').title()} - Confidence: {confidence:.0%}")
                        
                        # Show angle details only for high confidence
                        if confidence >= conf_threshold and analyses:
                            for analysis in analyses:
                                if analysis.feedback_level.value in ['perfect', 'good']:
                                    print(f"   ✅ {analysis.angle_name}: {analysis.measured_angle:.1f}°")
                    else:
                        print(f"{timestamp_str} ❓ Unknown pose")
                    
                    last_pose = detected_pose
                    last_pose_time = current_time
                
                # Save frame data (only high confidence frames)
                if frame_count % 10 == 0 and confidence >= conf_threshold:
                    frame_data = {
                        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "frame_number": frame_count,
                        "detected_pose": detected_pose,
                        "similarity_score": float(similarity_score),
                        "confidence": confidence,
                        "keypoints": keypoints
                    }
                    session_data["frames"].append(frame_data)
            
            else:
                # Handle cases with no pose detection
                if not keypoints:
                    cv2.putText(frame, "No person detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Loading pose database...", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    frame = detector.draw_landmarks(frame, keypoints)
            
            # Display session info
            timer_text = f"Session: {elapsed_minutes:02d}:{elapsed_seconds:02d}"
            cv2.putText(frame, timer_text, (10, frame.shape[0] - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display performance tracking status
            perf_summary = narrator.get_performance_summary()
            achievements = perf_summary['personal_bests'] + perf_summary['daily_bests'] + perf_summary['improvements']
            
            status_text = f"Achievements: {achievements}"
            cv2.putText(frame, status_text, (10, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Show the video feed
            cv2.imshow("🧘 Performance Yoga Coach - Press 'q' to finish", frame)
            
            # Check for quit command
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n⏹️  Finishing session...")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️  Session interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during session: {e}")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Finalize session data
        session_data["session_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_data["total_frames"] = frame_count
        session_data["duration_seconds"] = int(time.time() - time.mktime(session_start.timetuple()))
        
        # Save session data
        if session_data["frames"]:
            filename = data_manager.save_session_data(session_data)
            print(f"\n🎉 Session completed successfully!")
            print(f"⏱️  Duration: {session_data['duration_seconds']} seconds")
            print(f"🎞️  Frames processed: {frame_count}")
            print(f"💾 Session saved: sessions/{filename}")
        
        # Get and display performance summary
        perf_summary = narrator.get_performance_summary()
        print(f"\n📊 PERFORMANCE SUMMARY:")
        print(f"   🏆 Personal bests: {perf_summary['personal_bests']}")
        print(f"   🎯 Daily bests: {perf_summary['daily_bests']}")
        print(f"   📈 Improvements: {perf_summary['improvements']}")
        print(f"   📐 Measurements taken: {perf_summary['measurements_taken']}")
        
        # Provide spoken session summary
        narrator.provide_session_summary()
        
        print(f"\n✨ Thank you for using Performance Yoga Coach!")
        print("📈 Your progress data has been saved for future comparison!")
        
        # Stop narrator and save performance data
        narrator.stop()


if __name__ == "__main__":
    main() 
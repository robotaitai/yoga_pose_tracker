#!/usr/bin/env python3
"""
🧘 SIMPLE PERFORMANCE YOGA COACH 🧘
Quick version without YAML dependency - works immediately!
"""

import cv2
import time
import subprocess
import threading
import json
import os
from datetime import datetime
from queue import Queue, Empty
from pathlib import Path
from pose_utils import PoseDetector, PoseComparator, PoseDataManager
from pose_database import OptimizedPoseDatabase
from angle_analyzer import PostureAnalyzer

class SimplePerformanceNarrator:
    """Simple performance narrator with real data saving"""
    
    def __init__(self):
        # Hardcoded settings (no YAML needed)
        self.confidence_threshold = 0.85
        self.min_hold_time = 3.0
        self.feedback_cooldown = 10.0
        
        # Create data directory
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Data files
        self.simple_history_file = self.data_dir / "simple_history.json"
        self.simple_bests_file = self.data_dir / "simple_bests.json"
        
        # Load existing data
        self.angle_history = self._load_history()
        self.personal_bests = self._load_bests()
        
        # Speech setup
        self.speech_queue = Queue()
        self.is_running = True
        self.speech_thread = threading.Thread(target=self._process_speech, daemon=True)
        self.speech_thread.start()
        
        # Tracking
        self.last_feedback_time = {}
        self.pose_hold_start = {}
        self.current_pose = ""
        self.achievements = 0
        
        print(f"🔊 Simple performance narrator ready!")
        print(f"💾 Data will be saved to: {self.data_dir.absolute()}")
    
    def _load_history(self):
        """Load angle measurement history"""
        if self.simple_history_file.exists():
            try:
                with open(self.simple_history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _load_bests(self):
        """Load personal bests"""
        if self.simple_bests_file.exists():
            try:
                with open(self.simple_bests_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_data(self):
        """Save data to files"""
        try:
            # Save history
            with open(self.simple_history_file, 'w') as f:
                json.dump(self.angle_history, f, indent=2)
            
            # Save bests
            with open(self.simple_bests_file, 'w') as f:
                json.dump(self.personal_bests, f, indent=2)
                
            print(f"💾 Data saved to {self.data_dir}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
    
    def _record_angle(self, pose_name, angle_name, angle_value):
        """Record an angle measurement"""
        timestamp = datetime.now().isoformat()
        
        # Add to history
        measurement = {
            "pose": pose_name,
            "angle_name": angle_name,
            "value": angle_value,
            "timestamp": timestamp
        }
        self.angle_history.append(measurement)
        
        # Check if it's a personal best
        key = f"{pose_name}_{angle_name}"
        is_personal_best = False
        
        if key not in self.personal_bests or angle_value > self.personal_bests[key]["value"]:
            self.personal_bests[key] = {
                "value": angle_value,
                "timestamp": timestamp
            }
            is_personal_best = True
        
        # Save data immediately
        self._save_data()
        
        return is_personal_best
    
    def _process_speech(self):
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text:
                    subprocess.run(['say', '-r', '180', text], check=True, timeout=10)
            except Empty:
                continue
            except:
                pass
    
    def speak(self, text):
        print(f"🎙️ NARRATOR: {text}")
        self.speech_queue.put(text)
    
    def analyze_pose(self, pose_name, similarity_score, analyses, keypoints):
        if pose_name == "unknown":
            return False
            
        current_time = datetime.now().timestamp()
        confidence = 1.0 - similarity_score
        
        # Check confidence
        if confidence < self.confidence_threshold:
            return False
        
        # Track hold time
        if pose_name != self.current_pose:
            self.pose_hold_start[pose_name] = current_time
            self.current_pose = pose_name
            return False
            
        hold_time = current_time - self.pose_hold_start.get(pose_name, current_time)
        if hold_time < self.min_hold_time:
            return False
            
        # Check cooldown
        last_feedback = self.last_feedback_time.get(pose_name, 0)
        if current_time - last_feedback < self.feedback_cooldown:
            return False
        
        # Analyze actual angles and SAVE REAL DATA
        if analyses and len(analyses) > 0:
            # Get the best angle measurement from analyses
            best_analysis = max(analyses, key=lambda a: a.score if hasattr(a, 'score') else 0)
            angle_value = best_analysis.measured_angle
            angle_name = best_analysis.angle_name.replace('_', ' ')
            clean_pose = pose_name.replace('_', ' ').title()
            
            # SAVE THE REAL ANGLE DATA
            is_personal_best = self._record_angle(pose_name, best_analysis.angle_name, angle_value)
            
            # Get historical data for comparison
            key = f"{pose_name}_{best_analysis.angle_name}"
            historical_angles = [m["value"] for m in self.angle_history 
                               if m["pose"] == pose_name and m["angle_name"] == best_analysis.angle_name]
            
            # Provide feedback based on real data
            target_angle = getattr(best_analysis, 'target_angle', angle_value)
            angle_diff = abs(angle_value - target_angle)
            
            message = ""
            
            if is_personal_best:
                if len(historical_angles) > 1:
                    prev_best = self.personal_bests[key]["value"] if key in self.personal_bests else angle_value
                    improvement = angle_value - prev_best
                    message = f"New personal best {angle_name} in {clean_pose}! {angle_value:.1f} degrees! "
                    message += f"That's {improvement:.1f} degrees better than your previous best!"
                else:
                    message = f"First recorded {angle_name} in {clean_pose}: {angle_value:.1f} degrees!"
            
            elif len(historical_angles) > 1:
                avg_angle = sum(historical_angles[:-1]) / len(historical_angles[:-1])  # Exclude current
                improvement = angle_value - avg_angle
                if improvement > 1.0:
                    message = f"Great improvement! Your {angle_name} is {improvement:.1f} degrees better "
                    message += f"than your average of {avg_angle:.1f}. Current: {angle_value:.1f} degrees!"
                elif angle_diff < 5:
                    message = f"Excellent form! {angle_name} in {clean_pose}: {angle_value:.1f} degrees - very precise!"
            
            if message:
                self.speak(message)
                self.achievements += 1
                self.last_feedback_time[pose_name] = current_time
                
                # Show REAL angle data in console
                print(f"\n📐 REAL ANGLE DATA SAVED:")
                print(f"   🎯 {angle_name}: {angle_value:.1f}°")
                print(f"   🏆 Personal best: {self.personal_bests.get(key, {}).get('value', 'None'):.1f}°" if key in self.personal_bests else "   🏆 Personal best: First measurement!")
                print(f"   📊 Total {pose_name} measurements: {len([m for m in self.angle_history if m['pose'] == pose_name])}")
                print(f"   💾 Saved to: {self.simple_history_file}")
                print()
                
                return True
        
        return False
    
    def get_summary(self):
        return {
            'achievements': self.achievements,
            'total_measurements': len(self.angle_history),
            'poses_measured': len(set([m['pose'] for m in self.angle_history])),
            'personal_bests': len(self.personal_bests)
        }
    
    def stop(self):
        self.is_running = False
        self._save_data()  # Final save
        print(f"\n💾 Final data save completed!")
        print(f"📊 Session summary:")
        summary = self.get_summary()
        print(f"   • Total measurements: {summary['total_measurements']}")
        print(f"   • Personal bests: {summary['personal_bests']}")
        print(f"   • Poses measured: {summary['poses_measured']}")
        print(f"📁 Data saved in: {self.data_dir.absolute()}")

def main():
    """Simple Performance Yoga Coach - No YAML required"""
    
    print("=" * 50)
    print("🧘 SIMPLE PERFORMANCE YOGA COACH 🧘")
    print("=" * 50)
    print("🎯 Quick version - no configuration needed!")
    print("🔊 Achievement-focused feedback")
    print("=" * 50)
    
    # Initialize components
    detector = PoseDetector()
    data_manager = PoseDataManager()
    posture_analyzer = PostureAnalyzer()
    narrator = SimplePerformanceNarrator()
    
    # Load poses
    optimized_db = OptimizedPoseDatabase(similarity_threshold=0.20)
    use_optimized = optimized_db.is_loaded()
    
    if use_optimized:
        print("✅ Using optimized pose database")
        reference_poses = None
        comparator = None
    else:
        print("⚠️  Using fallback system")
        comparator = PoseComparator(similarity_threshold=0.20)
        reference_poses = data_manager.load_reference_poses()
        if not reference_poses:
            print("❌ No reference poses! Run: python scripts/process_images.py")
            return
    
    # Start camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n🚀 STARTING SESSION")
    print("🔊 Narrator will celebrate your achievements!")
    print("⌨️  Press 'q' to finish\n")
    
    session_start = time.time()
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            keypoints = detector.extract_keypoints(frame)
            
            if keypoints:
                # Detect pose
                if use_optimized:
                    detected_pose, similarity_score, _ = optimized_db.find_best_pose_match(keypoints)
                elif reference_poses and comparator:
                    detected_pose, similarity_score = comparator.find_best_pose_match(keypoints, reference_poses)
                else:
                    detected_pose, similarity_score = "unknown", float('inf')
                
                frame = detector.draw_landmarks(frame, keypoints)
                confidence = 1.0 - similarity_score if similarity_score != float('inf') else 0.0
                
                # Display info
                pose_text = f"Pose: {detected_pose}"
                if detected_pose != "unknown":
                    pose_text += f" ({confidence:.0%})"
                
                color = (0, 255, 0) if confidence >= 0.85 else (0, 255, 255)
                cv2.putText(frame, pose_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Analyze for achievements
                if detected_pose != "unknown":
                    analyses = posture_analyzer.analyze_pose(detected_pose, keypoints)
                    if analyses:
                        score, grade = posture_analyzer.get_overall_score(analyses)
                        cv2.putText(frame, f"Form: {score:.1f}% ({grade})", (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        feedback_given = narrator.analyze_pose(detected_pose, similarity_score, analyses, keypoints)
                        if feedback_given:
                            cv2.putText(frame, "🎯 ACHIEVEMENT!", (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Session info
            elapsed = int(time.time() - session_start)
            cv2.putText(frame, f"Session: {elapsed//60:02d}:{elapsed%60:02d}", 
                       (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            summary = narrator.get_summary()
            cv2.putText(frame, f"Achievements: {summary['achievements']}", 
                       (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow("🧘 Simple Performance Coach - Press 'q' to finish", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        narrator.stop()
        
        print(f"\n🎉 Session complete!")
        summary = narrator.get_summary()
        print(f"🏆 Total achievements: {summary['achievements']}")
        if summary['achievements'] > 0:
            narrator.speak(f"Great session! You achieved {summary['achievements']} milestones today!")

if __name__ == "__main__":
    main() 
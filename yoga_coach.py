#!/usr/bin/env python3
"""
🧘 YOGA POSE TRACKER WITH VOICE COACHING 🧘

Your Personal AI Yoga Instructor with Real-time Voice Feedback

Features:
- Real-time pose detection (Tree, Warrior 2, Downward Dog)
- Voice coaching with macOS text-to-speech
- Critical angle analysis and form correction
- Smart feedback based on pose quality
- Session tracking and performance statistics

Usage:
    python yoga_coach.py

Requirements:
    - macOS with built-in text-to-speech
    - Webcam
    - Python environment with required packages
"""

import cv2
import time
import subprocess
import threading
from datetime import datetime
from queue import Queue, Empty
from pose_utils import PoseDetector, PoseComparator, PoseDataManager
from pose_database import OptimizedPoseDatabase, load_fallback_poses
from angle_analyzer import PostureAnalyzer


class YogaVoiceCoach:
    """Voice coaching system using macOS built-in text-to-speech"""
    
    def __init__(self, speech_rate=180):
        self.rate = speech_rate
        self.speech_queue = Queue()
        self.is_running = True
        self.speech_thread = threading.Thread(target=self._process_speech, daemon=True)
        self.speech_thread.start()
        
        # Test voice system
        self._test_voice()
        
        # Tracking variables
        self.current_pose = ""
        self.pose_start_time = 0
        self.last_feedback_time = {}
        self.feedback_cooldown = 5.0
        
    def _test_voice(self):
        """Test if voice synthesis works"""
        try:
            subprocess.run(['say', 'Voice coaching ready'], 
                         check=True, capture_output=True, timeout=3)
            print(f"🔊 Voice coach ready! Using macOS built-in voice")
        except Exception as e:
            print(f"⚠️  Voice test failed: {e}")
            print("📱 Voice feedback will be shown as text instead")
    
    def speak(self, text):
        """Add text to speech queue for background processing"""
        if self.is_running:
            self.speech_queue.put(text)
    
    def speak_immediately(self, text):
        """Speak text immediately (blocking)"""
        try:
            subprocess.run(['say', '-r', str(self.rate), text], 
                         check=True, timeout=10)
        except:
            print(f"🎙️ COACH: {text}")
    
    def _process_speech(self):
        """Background speech processing"""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text:
                    subprocess.run(['say', '-r', str(self.rate), text], 
                                 check=True, timeout=15)
            except Empty:
                continue
            except Exception:
                pass
    
    def on_pose_detected(self, pose_name, analyses=None, score=None):
        """Handle pose detection and provide intelligent feedback"""
        current_time = time.time()
        
        # Announce new poses
        if pose_name != self.current_pose and pose_name != "unknown":
            clean_name = pose_name.replace('_', ' ').title()
            self.speak(f"Entering {clean_name}. Focus on your alignment.")
            self.current_pose = pose_name
            self.pose_start_time = current_time
        
        # Provide form feedback (with cooldown to avoid spam)
        if (pose_name != "unknown" and analyses and 
            current_time - self.last_feedback_time.get(pose_name, 0) > self.feedback_cooldown):
            
            self.last_feedback_time[pose_name] = current_time
            
            # Analyze issues by priority
            critical_issues = [a for a in analyses if a.feedback_level.value == 'poor']
            major_issues = [a for a in analyses if a.feedback_level.value == 'needs_adjustment']
            
            if critical_issues:
                issue = critical_issues[0]
                self.speak(f"Critical adjustment: {issue.improvement_tip}")
            elif major_issues and score and score < 75:
                issue = major_issues[0]
                self.speak(f"Small adjustment: {issue.improvement_tip}")
            elif score and score >= 90:
                pose_duration = current_time - self.pose_start_time
                if pose_duration > 8:  # Only praise if held for a while
                    self.speak("Excellent form! Beautiful pose.")
    
    def breathing_reminder(self):
        """Provide breathing guidance"""
        self.speak("Remember to breathe deeply. Inhale strength, exhale tension.")
    
    def session_summary(self, poses_count, avg_score, best_pose):
        """Provide spoken session summary"""
        summary = f"Session complete! You practiced {poses_count} poses with an average score of {avg_score:.0f} percent."
        if best_pose:
            summary += f" Your best pose was {best_pose.replace('_', ' ')}."
        summary += " Excellent work! Keep practicing to improve your form. Namaste."
        self.speak_immediately(summary)
    
    def stop(self):
        """Stop the voice coaching system"""
        self.is_running = False
        try:
            subprocess.run(['pkill', 'say'], check=False)
        except:
            pass


def main():
    """Main application - Voice-Enabled Yoga Pose Tracker"""
    
    print("=" * 70)
    print("🧘 YOGA POSE TRACKER WITH VOICE COACHING 🧘")
    print("=" * 70)
    print("🎙️ Your Personal AI Yoga Instructor")
    print("🔊 Real-time voice feedback and form analysis")
    print("📐 Critical angle coaching with audio guidance")
    print("🎯 Intelligent pose recognition and scoring")
    print("=" * 70)
    
    # Initialize core components
    print("Initializing yoga coaching system...")
    detector = PoseDetector()
    data_manager = PoseDataManager()
    posture_analyzer = PostureAnalyzer()
    
    # Initialize voice coaching
    print("🔊 Initializing voice coaching...")
    voice_coach = YogaVoiceCoach(speech_rate=180)
    
    # Load pose database
    print("📖 Loading pose database...")
    optimized_db = OptimizedPoseDatabase(similarity_threshold=0.25)
    use_optimized = optimized_db.is_loaded()
    
    if use_optimized:
        print("✅ Using optimized pose database")
        reference_poses = None
        comparator = None
    else:
        print("⚠️  Using fallback reference system")
        comparator = PoseComparator(similarity_threshold=0.25)
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
    
    # Session statistics
    session_stats = {
        'poses_practiced': set(),
        'scores': [],
        'best_pose': '',
        'best_score': 0
    }
    
    frame_count = 0
    last_pose = ""
    last_pose_time = time.time()
    breathing_reminder_time = time.time()
    
    print("\n🚀 STARTING YOUR VOICE-COACHED YOGA SESSION")
    print("=" * 70)
    print("📹 Position yourself in front of the camera")
    print("🧘 Listen for voice guidance as you practice")
    print("📐 Your form will be analyzed in real-time")
    print("⌨️  Press 'q' in the camera window to finish")
    print("=" * 70)
    print()
    
    # Welcome message
    voice_coach.speak_immediately("Welcome to your personal yoga coaching session! Position yourself in front of the camera and begin your practice. I'll guide you through proper form and alignment.")
    
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
            score = None
            
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
                
                # Display pose information
                pose_text = f"Pose: {detected_pose}"
                if detected_pose != "unknown":
                    pose_text += f" (Match: {similarity_score:.3f})"
                
                cv2.putText(frame, pose_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Analyze pose for detailed feedback
                if detected_pose != "unknown" and keypoints:
                    analyses = posture_analyzer.analyze_pose(detected_pose, keypoints)
                    if analyses:
                        score, grade = posture_analyzer.get_overall_score(analyses)
                        
                        # Update session statistics
                        session_stats['poses_practiced'].add(detected_pose)
                        session_stats['scores'].append(score)
                        if score > session_stats['best_score']:
                            session_stats['best_score'] = score
                            session_stats['best_pose'] = detected_pose
                        
                        # Display form score on video
                        score_text = f"Form: {score:.1f}% ({grade})"
                        cv2.putText(frame, score_text, (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Provide voice coaching
                voice_coach.on_pose_detected(detected_pose, analyses, score)
                
                # Console feedback for detailed analysis
                if detected_pose != last_pose or (current_time - last_pose_time) > 5.0:
                    timestamp_str = f"[{elapsed_minutes:02d}:{elapsed_seconds:02d}]"
                    if detected_pose != "unknown":
                        if analyses and score:
                            print(f"\n{timestamp_str} 🧘 {detected_pose.replace('_', ' ').title()}")
                            print(f"   📊 Detection: {similarity_score:.3f} | Form: {score:.1f}% ({grade})")
                            
                            # Show critical angle feedback
                            for analysis in analyses:
                                if analysis.feedback_level.value in ['needs_adjustment', 'poor']:
                                    emoji = "🔴" if analysis.feedback_level.value == 'poor' else "🟡"
                                    print(f"   {emoji} {analysis.angle_name}: {analysis.measured_angle:.1f}° - {analysis.message}")
                                elif analysis.feedback_level.value == 'perfect':
                                    print(f"   🟢 {analysis.angle_name}: {analysis.measured_angle:.1f}° - Perfect!")
                        else:
                            print(f"{timestamp_str} 🧘 {detected_pose}")
                    else:
                        print(f"{timestamp_str} ❓ Unknown pose")
                    
                    last_pose = detected_pose
                    last_pose_time = current_time
                
                # Periodic breathing reminders
                if current_time - breathing_reminder_time > 45:  # Every 45 seconds
                    voice_coach.breathing_reminder()
                    breathing_reminder_time = current_time
                
                # Save frame data for session tracking
                if frame_count % 10 == 0:  # Save every 10th frame
                    frame_data = {
                        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "frame_number": frame_count,
                        "detected_pose": detected_pose,
                        "similarity_score": float(similarity_score) if similarity_score != float('inf') else None,
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
            
            # Display session timer
            timer_text = f"Session: {elapsed_minutes:02d}:{elapsed_seconds:02d}"
            cv2.putText(frame, timer_text, (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display frame count
            frame_text = f"Frames: {frame_count}"
            cv2.putText(frame, frame_text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show the video feed
            cv2.imshow("🧘 Yoga Coach - Press 'q' to finish session", frame)
            
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
        
        # Save session and provide summary
        if session_data["frames"]:
            filename = data_manager.save_session_data(session_data)
            print(f"\n🎉 Session completed successfully!")
            print(f"⏱️  Duration: {session_data['duration_seconds']} seconds")
            print(f"🎞️  Frames processed: {frame_count}")
            print(f"💾 Session saved: sessions/{filename}")
            
            # Spoken session summary
            poses_practiced = len(session_stats['poses_practiced'])
            avg_score = sum(session_stats['scores']) / len(session_stats['scores']) if session_stats['scores'] else 0
            voice_coach.session_summary(poses_practiced, avg_score, session_stats['best_pose'])
            
            # Detailed performance report
            print(f"\n📊 YOUR YOGA SESSION PERFORMANCE:")
            print(f"   🧘 Poses practiced: {poses_practiced}")
            print(f"   📈 Average form score: {avg_score:.1f}%")
            if session_stats['best_pose']:
                print(f"   🏆 Best pose: {session_stats['best_pose'].replace('_', ' ').title()} ({session_stats['best_score']:.1f}%)")
            print(f"   📈 Total improvements detected: {len([s for s in session_stats['scores'] if s > 75])}")
        else:
            print("⚠️  No session data to save")
        
        print(f"\n✨ Thank you for practicing with Yoga Coach!")
        print("🧘 Keep practicing regularly to improve your form and flexibility!")
        
        # Stop voice coaching
        voice_coach.stop()


if __name__ == "__main__":
    main() 
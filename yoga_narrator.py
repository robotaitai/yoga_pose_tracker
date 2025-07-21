#!/usr/bin/env python3
"""
Yoga Narrator - Voice Feedback System

Provides real-time voice feedback for yoga poses using text-to-speech.
Analyzes poses and gives coaching guidance with natural language.
"""

import time
import threading
import queue
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import random

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 not available. Install with: pip install pyttsx3")

from angle_analyzer import PostureAnalyzer, AngleAnalysis, AngleFeedback


class FeedbackPriority(Enum):
    """Priority levels for feedback messages"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class FeedbackMessage:
    """A feedback message to be spoken"""
    text: str
    priority: FeedbackPriority
    timestamp: float
    pose_name: str = ""
    angle_name: str = ""


class YogaNarrator:
    """Main narrator class for providing voice feedback"""
    
    def __init__(self, enable_tts: bool = True, speech_rate: int = 180, volume: float = 0.8):
        """
        Initialize the yoga narrator
        
        Args:
            enable_tts: Whether to enable text-to-speech
            speech_rate: Words per minute for speech
            volume: Volume level (0.0 to 1.0)
        """
        self.enable_tts = enable_tts and TTS_AVAILABLE
        self.speech_rate = speech_rate
        self.volume = volume
        
        # Initialize TTS engine
        self.tts_engine = None
        if self.enable_tts:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', speech_rate)
                self.tts_engine.setProperty('volume', volume)
                
                # Set voice (prefer female voice if available)
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
            except Exception as e:
                print(f"TTS initialization failed: {e}")
                self.enable_tts = False
        
        # Feedback management
        self.feedback_queue = queue.Queue()
        self.last_feedback_time = {}  # Track when we last gave feedback for each type
        self.feedback_cooldown = 3.0  # Minimum seconds between similar feedback
        
        # Threading for non-blocking speech
        self.speech_thread = None
        self.is_speaking = False
        self.stop_speaking = False
        
        # Pose tracking
        self.current_pose = ""
        self.pose_start_time = 0
        self.last_score = 0
        self.score_trend = []  # Track score changes
        
        # Encouragement system
        self.encouragement_phrases = [
            "Great work!", "Keep it up!", "You're doing well!", 
            "Nice improvement!", "Excellent form!", "Beautiful pose!",
            "Stay focused!", "Breathe deeply!", "Feel the strength!"
        ]
        
        self.correction_phrases = [
            "Let's adjust that", "Try to", "Focus on", "Remember to",
            "Gently", "Slowly", "Take your time to"
        ]
        
        # Start the speech processing thread
        self._start_speech_thread()
    
    def _start_speech_thread(self):
        """Start the background thread for processing speech"""
        if self.enable_tts:
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
    
    def _speech_worker(self):
        """Background worker to process speech queue"""
        while not self.stop_speaking:
            try:
                # Get next message with timeout
                message = self.feedback_queue.get(timeout=1.0)
                
                if message and self.enable_tts and self.tts_engine:
                    self.is_speaking = True
                    print(f"🗣️  Narrator: {message.text}")
                    
                    try:
                        self.tts_engine.say(message.text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        print(f"TTS error: {e}")
                    finally:
                        self.is_speaking = False
                
                self.feedback_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Speech worker error: {e}")
    
    def speak(self, text: str, priority: FeedbackPriority = FeedbackPriority.MEDIUM, 
              pose_name: str = "", angle_name: str = ""):
        """
        Add text to speech queue
        
        Args:
            text: Text to speak
            priority: Priority level
            pose_name: Associated pose name
            angle_name: Associated angle name
        """
        # Check cooldown for similar feedback
        feedback_key = f"{pose_name}_{angle_name}"
        current_time = time.time()
        
        if feedback_key in self.last_feedback_time:
            if current_time - self.last_feedback_time[feedback_key] < self.feedback_cooldown:
                return  # Skip to avoid repetitive feedback
        
        self.last_feedback_time[feedback_key] = current_time
        
        message = FeedbackMessage(
            text=text,
            priority=priority,
            timestamp=current_time,
            pose_name=pose_name,
            angle_name=angle_name
        )
        
        # Add to queue (higher priority messages replace lower priority ones)
        if priority.value >= FeedbackPriority.HIGH.value:
            # Clear queue for high priority messages
            try:
                while True:
                    old_msg = self.feedback_queue.get_nowait()
                    if old_msg.priority.value >= FeedbackPriority.HIGH.value:
                        self.feedback_queue.put(old_msg)  # Keep high priority
                        break
            except queue.Empty:
                pass
        
        self.feedback_queue.put(message)
        
        # Also print to console
        if not self.enable_tts:
            print(f"🗣️  Narrator: {text}")
    
    def analyze_and_speak(self, pose_name: str, analyses: List[AngleAnalysis], 
                         overall_score: float, grade: str):
        """
        Analyze pose and provide appropriate voice feedback
        
        Args:
            pose_name: Name of current pose
            analyses: List of angle analyses
            overall_score: Overall pose score (0-100)
            grade: Grade text
        """
        # Track pose changes
        if pose_name != self.current_pose:
            if pose_name != "unknown":
                self.speak(f"Entering {pose_name.replace('_', ' ')}", 
                          FeedbackPriority.HIGH, pose_name)
            self.current_pose = pose_name
            self.pose_start_time = time.time()
            self.score_trend = []
        
        if pose_name == "unknown":
            return
        
        # Track score trend
        self.score_trend.append(overall_score)
        if len(self.score_trend) > 10:  # Keep last 10 scores
            self.score_trend = self.score_trend[-10:]
        
        # Determine feedback type based on pose duration and performance
        pose_duration = time.time() - self.pose_start_time
        
        # Initial pose feedback (first few seconds)
        if pose_duration < 3:
            self._provide_initial_feedback(analyses, overall_score)
        
        # Ongoing feedback (after settling into pose)
        elif pose_duration > 5:
            self._provide_ongoing_feedback(analyses, overall_score, grade)
        
        # Track last score for comparison
        self.last_score = overall_score
    
    def _provide_initial_feedback(self, analyses: List[AngleAnalysis], score: float):
        """Provide initial feedback when entering a pose"""
        
        # Find most critical issues
        critical_issues = [a for a in analyses if a.feedback_level == AngleFeedback.POOR]
        major_issues = [a for a in analyses if a.feedback_level == AngleFeedback.NEEDS_ADJUSTMENT]
        
        if critical_issues:
            # Address most critical issue first
            issue = critical_issues[0]
            correction = random.choice(self.correction_phrases)
            self.speak(f"{correction} {issue.message.lower()}", 
                      FeedbackPriority.HIGH, self.current_pose, issue.angle_name)
        
        elif major_issues and score < 75:
            # Address major issue with gentle guidance
            issue = major_issues[0]
            self.speak(issue.message, FeedbackPriority.MEDIUM, 
                      self.current_pose, issue.angle_name)
        
        elif score >= 85:
            # Positive reinforcement for good initial positioning
            encouragement = random.choice(self.encouragement_phrases)
            self.speak(f"{encouragement} Good {self.current_pose.replace('_', ' ')}!", 
                      FeedbackPriority.LOW, self.current_pose)
    
    def _provide_ongoing_feedback(self, analyses: List[AngleAnalysis], score: float, grade: str):
        """Provide ongoing feedback during pose hold"""
        
        # Calculate score trend
        if len(self.score_trend) >= 3:
            recent_trend = sum(self.score_trend[-3:]) / 3
            earlier_trend = sum(self.score_trend[-6:-3]) / 3 if len(self.score_trend) >= 6 else recent_trend
            improvement = recent_trend - earlier_trend
        else:
            improvement = 0
        
        # Provide feedback based on performance and trend
        if score >= 90:
            if improvement > 5:
                self.speak("Excellent improvement! Hold this beautiful pose.", 
                          FeedbackPriority.LOW, self.current_pose)
            elif random.random() < 0.3:  # Occasional encouragement
                self.speak(f"Perfect {self.current_pose.replace('_', ' ')}! {random.choice(self.encouragement_phrases)}", 
                          FeedbackPriority.LOW, self.current_pose)
        
        elif score >= 75:
            # Look for specific improvements to suggest
            major_issues = [a for a in analyses if a.feedback_level == AngleFeedback.NEEDS_ADJUSTMENT]
            if major_issues and random.random() < 0.5:
                issue = major_issues[0]
                self.speak(f"Try to {issue.improvement_tip.lower()}", 
                          FeedbackPriority.MEDIUM, self.current_pose, issue.angle_name)
        
        else:  # score < 75
            # Focus on biggest improvement opportunity
            poor_angles = [a for a in analyses if a.feedback_level == AngleFeedback.POOR]
            if poor_angles:
                issue = poor_angles[0]
                self.speak(f"Focus on {issue.message.lower()}", 
                          FeedbackPriority.MEDIUM, self.current_pose, issue.angle_name)
    
    def provide_breathing_cue(self):
        """Provide breathing reminders"""
        breathing_cues = [
            "Remember to breathe deeply",
            "Take slow, deep breaths",
            "Don't forget to breathe",
            "Inhale strength, exhale tension",
            "Let your breath guide you"
        ]
        self.speak(random.choice(breathing_cues), FeedbackPriority.LOW)
    
    def provide_transition_cue(self, next_pose: str):
        """Provide transition guidance"""
        self.speak(f"Great work! Now let's transition to {next_pose.replace('_', ' ')}", 
                  FeedbackPriority.HIGH, next_pose)
    
    def provide_session_summary(self, session_stats: Dict):
        """Provide end-of-session summary"""
        poses_practiced = session_stats.get('poses_practiced', 0)
        avg_score = session_stats.get('average_score', 0)
        best_pose = session_stats.get('best_pose', 'unknown')
        
        summary = f"Great session! You practiced {poses_practiced} poses with an average score of {avg_score:.0f}."
        if best_pose != 'unknown':
            summary += f" Your best pose was {best_pose.replace('_', ' ')}."
        summary += " Keep up the excellent work!"
        
        self.speak(summary, FeedbackPriority.HIGH)
    
    def set_speech_rate(self, rate: int):
        """Adjust speech rate"""
        self.speech_rate = rate
        if self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Adjust volume"""
        self.volume = volume
        if self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
    
    def stop(self):
        """Stop the narrator and cleanup"""
        self.stop_speaking = True
        if self.speech_thread:
            self.speech_thread.join(timeout=2.0)
        
        # Clear the queue
        try:
            while True:
                self.feedback_queue.get_nowait()
        except queue.Empty:
            pass


class SmartFeedbackManager:
    """Manages intelligent feedback timing and content"""
    
    def __init__(self, narrator: YogaNarrator):
        self.narrator = narrator
        self.posture_analyzer = PostureAnalyzer()
        
        # Feedback timing
        self.last_analysis_time = 0
        self.analysis_interval = 2.0  # Analyze every 2 seconds
        
        # Session tracking
        self.session_stats = {
            'poses_practiced': set(),
            'scores': [],
            'pose_durations': {},
            'best_pose': '',
            'best_score': 0
        }
    
    def process_frame(self, pose_name: str, keypoints: Dict, timestamp: float):
        """
        Process a frame and provide intelligent feedback
        
        Args:
            pose_name: Current pose name
            keypoints: Pose keypoints
            timestamp: Current timestamp
        """
        # Only analyze periodically to avoid overwhelming feedback
        if timestamp - self.last_analysis_time < self.analysis_interval:
            return
        
        self.last_analysis_time = timestamp
        
        if pose_name == "unknown":
            return
        
        # Analyze the pose
        analyses = self.posture_analyzer.analyze_pose(pose_name, keypoints)
        if not analyses:
            return
        
        score, grade = self.posture_analyzer.get_overall_score(analyses)
        
        # Update session stats
        self.session_stats['poses_practiced'].add(pose_name)
        self.session_stats['scores'].append(score)
        
        if score > self.session_stats['best_score']:
            self.session_stats['best_score'] = score
            self.session_stats['best_pose'] = pose_name
        
        # Provide feedback through narrator
        self.narrator.analyze_and_speak(pose_name, analyses, score, grade)
        
        # Occasional breathing reminders
        if random.random() < 0.1:  # 10% chance
            self.narrator.provide_breathing_cue()
    
    def get_session_summary(self) -> Dict:
        """Get session summary statistics"""
        return {
            'poses_practiced': len(self.session_stats['poses_practiced']),
            'average_score': sum(self.session_stats['scores']) / len(self.session_stats['scores']) if self.session_stats['scores'] else 0,
            'best_pose': self.session_stats['best_pose'],
            'best_score': self.session_stats['best_score']
        }


# Example usage and testing
if __name__ == "__main__":
    print("🎙️ Testing Yoga Narrator")
    print("=" * 40)
    
    # Test TTS availability
    if TTS_AVAILABLE:
        print("✅ Text-to-speech available")
    else:
        print("⚠️  Text-to-speech not available (install pyttsx3)")
    
    # Create narrator
    narrator = YogaNarrator(enable_tts=True)
    
    # Test basic speech
    narrator.speak("Welcome to your yoga practice session!", FeedbackPriority.HIGH)
    
    # Simulate pose analysis
    sample_keypoints = {
        "left_shoulder": [0.35, 0.25],
        "right_shoulder": [0.65, 0.25],
        "left_hip": [0.42, 0.50],
        "right_hip": [0.58, 0.50],
        "left_knee": [0.40, 0.70],
        "right_knee": [0.60, 0.70],
        "left_ankle": [0.38, 0.90],
        "right_ankle": [0.62, 0.90]
    }
    
    # Create feedback manager
    feedback_manager = SmartFeedbackManager(narrator)
    
    # Simulate several frames
    for i in range(5):
        feedback_manager.process_frame("warrior_2", sample_keypoints, time.time())
        time.sleep(1)
    
    # Test session summary
    summary = feedback_manager.get_session_summary()
    narrator.provide_session_summary(summary)
    
    print("\n✅ Narrator test completed!")
    
    # Cleanup
    time.sleep(3)  # Let speech finish
    narrator.stop() 
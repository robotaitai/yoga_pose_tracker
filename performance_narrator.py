#!/usr/bin/env python3
"""
Performance-Focused Narrator for Yoga Coach

Only speaks when poses are detected with high confidence and provides
data-driven feedback comparing current performance to historical data.
"""

import yaml
import subprocess
import threading
from datetime import datetime
from queue import Queue, Empty
from typing import Optional, Dict, Any
from performance_tracker import PerformanceTracker, PerformanceStats


class PerformanceNarrator:
    """Performance-focused narrator that compares current angles to history"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.performance_tracker = PerformanceTracker(config_path)
        
        # Narrator settings
        narrator_config = self.config.get('narrator', {})
        self.enabled = narrator_config.get('enabled', True)
        self.speech_rate = narrator_config.get('speech_rate', 180)
        self.volume = narrator_config.get('volume', 0.8)
        
        # Feedback settings
        self.speak_on_performance = narrator_config.get('speak_on_performance', True)
        self.speak_on_improvement = narrator_config.get('speak_on_improvement', True)
        self.speak_on_personal_best = narrator_config.get('speak_on_personal_best', True)
        self.feedback_cooldown = narrator_config.get('feedback_cooldown', 10.0)
        
        # Detection thresholds
        detection_config = self.config.get('pose_detection', {})
        self.confidence_threshold = detection_config.get('confidence_threshold', 0.85)
        self.min_hold_time = detection_config.get('min_hold_time', 3.0)
        
        # Voice messages
        self.voice_messages = self.config.get('voice_messages', {})
        
        # Speech queue and threading
        self.speech_queue = Queue()
        self.is_running = True
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()
        
        # Tracking state
        self.last_feedback_time = {}
        self.pose_hold_start = {}
        self.current_pose = ""
        
        # Test voice system
        self._test_voice()
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Default configuration"""
        return {
            'narrator': {'enabled': True, 'speech_rate': 180},
            'pose_detection': {'confidence_threshold': 0.85, 'min_hold_time': 3.0},
            'voice_messages': {
                'personal_best': "Excellent! New personal best for {pose} {angle}: {current_angle:.1f} degrees!",
                'improvement': "Great progress! Your {angle} is {improvement:.1f} degrees better than your average.",
                'daily_best': "That's your best {angle} today - {current_angle:.1f} degrees!",
                'session_summary': "Session complete! You achieved {num_improvements} improvements today."
            }
        }
    
    def _test_voice(self):
        """Test if voice synthesis works"""
        if not self.enabled:
            return
            
        try:
            subprocess.run(['say', 'Performance tracking ready'], 
                         check=True, capture_output=True, timeout=3)
            print("🔊 Performance narrator ready!")
        except Exception as e:
            print(f"⚠️  Voice test failed: {e}")
            print("📱 Will show feedback as text instead")
    
    def _speak(self, text: str, priority: bool = False):
        """Add text to speech queue"""
        if not self.enabled:
            print(f"🎙️ NARRATOR: {text}")
            return
        
        if priority:
            # Clear queue for high priority messages
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                except Empty:
                    break
        
        self.speech_queue.put(text)
    
    def _process_speech_queue(self):
        """Process speech queue in background thread"""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text:
                    subprocess.run(['say', '-r', str(self.speech_rate), text], 
                                 check=True, timeout=15)
            except Empty:
                continue
            except Exception:
                pass
    
    def analyze_pose(self, pose_name: str, similarity_score: float, analyses: list, keypoints: dict) -> bool:
        """
        Analyze pose and provide performance feedback if criteria are met
        
        Returns: True if feedback was given, False otherwise
        """
        
        if not self.enabled or pose_name == "unknown":
            return False
        
        current_time = datetime.now().timestamp()
        
        # Check confidence threshold
        confidence = 1.0 - similarity_score  # Convert similarity to confidence
        if confidence < self.confidence_threshold:
            return False
        
        # Track pose hold time
        if pose_name != self.current_pose:
            self.pose_hold_start[pose_name] = current_time
            self.current_pose = pose_name
            return False
        
        # Check minimum hold time
        hold_time = current_time - self.pose_hold_start.get(pose_name, current_time)
        if hold_time < self.min_hold_time:
            return False
        
        # Check feedback cooldown
        last_feedback = self.last_feedback_time.get(pose_name, 0)
        if current_time - last_feedback < self.feedback_cooldown:
            return False
        
        # Analyze angles and provide performance feedback
        feedback_given = False
        
        if analyses:
            for analysis in analyses:
                angle_name = analysis.angle_name
                angle_value = analysis.measured_angle
                
                # Record measurement and get performance stats
                stats = self.performance_tracker.record_measurement(pose_name, angle_name, angle_value)
                
                if stats:
                    # Determine if feedback should be provided
                    should_speak, feedback_type = self.performance_tracker.should_provide_feedback(
                        pose_name, angle_name, angle_value
                    )
                    
                    if should_speak:
                        message = self._generate_feedback_message(
                            feedback_type, pose_name, angle_name, angle_value, stats
                        )
                        if message:
                            self._speak(message, priority=True)
                            feedback_given = True
                            
                            # Show detailed angle analysis in console
                            print(f"\n📐 ANGLE ANALYSIS - {pose_name.replace('_', ' ').title()}")
                            print(f"   🎯 {angle_name.replace('_', ' ')}: {angle_value:.1f}°")
                            if stats.historical_average:
                                print(f"   📊 30-day average: {stats.historical_average:.1f}°")
                                if stats.improvement_vs_average:
                                    print(f"   📈 Improvement: +{stats.improvement_vs_average:.1f}°")
                            if stats.personal_best:
                                print(f"   🏆 Personal best: {stats.personal_best:.1f}°")
                            if stats.daily_best:
                                print(f"   🌟 Today's best: {stats.daily_best:.1f}°")
                            print(f"   🎉 Achievement: {feedback_type.replace('_', ' ').title()}!")
                            print()
                            
                            break  # Only give one piece of feedback per analysis
        
        if feedback_given:
            self.last_feedback_time[pose_name] = current_time
        
        return feedback_given
    
    def _generate_feedback_message(self, feedback_type: str, pose_name: str, 
                                 angle_name: str, current_angle: float, 
                                 stats: PerformanceStats) -> Optional[str]:
        """Generate appropriate feedback message based on performance stats"""
        
        # Clean up names for speech
        clean_pose = pose_name.replace('_', ' ')
        clean_angle = angle_name.replace('_', ' ')
        
        if feedback_type == "personal_best":
            if stats.personal_best:
                improvement = current_angle - stats.personal_best
                message = f"Outstanding! New personal best {clean_angle} in {clean_pose}: {current_angle:.1f} degrees! "
                message += f"That's {improvement:.1f} degrees better than your previous best of {stats.personal_best:.1f}!"
            else:
                message = f"Excellent! First recorded {clean_angle} in {clean_pose}: {current_angle:.1f} degrees!"
            return message
        
        elif feedback_type == "daily_best":
            if stats.daily_best:
                improvement = current_angle - stats.daily_best
                message = f"Great work! Best {clean_angle} today: {current_angle:.1f} degrees in {clean_pose}! "
                message += f"That's {improvement:.1f} degrees better than your previous best today."
            else:
                message = f"Nice! First {clean_angle} measurement today: {current_angle:.1f} degrees in {clean_pose}!"
            return message
        
        elif feedback_type == "improvement":
            if stats.improvement_vs_average and stats.historical_average:
                message = f"Excellent progress! Your {clean_angle} is {stats.improvement_vs_average:.1f} degrees better "
                message += f"than your 30-day average of {stats.historical_average:.1f} degrees. "
                message += f"Current measurement: {current_angle:.1f} degrees!"
                return message
        
        return None
    
    def provide_session_summary(self):
        """Provide spoken session summary"""
        if not self.enabled:
            return
        
        summary = self.performance_tracker.get_session_summary()
        
        # Generate summary message
        total_achievements = summary['personal_bests'] + summary['daily_bests'] + summary['improvements']
        
        if total_achievements > 0:
            message_parts = []
            
            if summary['personal_bests'] > 0:
                message_parts.append(f"{summary['personal_bests']} personal best{'s' if summary['personal_bests'] > 1 else ''}")
            
            if summary['daily_bests'] > 0:
                message_parts.append(f"{summary['daily_bests']} daily best{'s' if summary['daily_bests'] > 1 else ''}")
            
            if summary['improvements'] > 0:
                message_parts.append(f"{summary['improvements']} improvement{'s' if summary['improvements'] > 1 else ''}")
            
            achievements_text = ", ".join(message_parts)
            message = f"Excellent session! You achieved {achievements_text} today."
            
            # Add duration if significant
            if summary['session_duration'] > 5:
                message += f" Session time: {summary['session_duration']:.1f} minutes."
        
        else:
            message = "Session complete. Keep practicing to build your performance history!"
        
        self._speak(message, priority=True)
    
    def get_performance_summary(self) -> dict:
        """Get current session performance summary"""
        return self.performance_tracker.get_session_summary()
    
    def save_performance_data(self):
        """Save performance data to files"""
        self.performance_tracker.save_data()
    
    def stop(self):
        """Stop the narrator and save data"""
        self.is_running = False
        self.save_performance_data()
        
        # Clear any pending speech
        try:
            subprocess.run(['pkill', 'say'], check=False)
        except:
            pass


# Test the performance narrator
if __name__ == "__main__":
    print("🧘 Testing Performance Narrator...")
    
    narrator = PerformanceNarrator()
    
    # Simulate some test data
    test_analyses = []  # Would normally come from angle_analyzer
    
    print("✅ Performance narrator initialized successfully!")
    print("🎯 Ready to track your yoga performance improvements!")
    
    narrator.stop() 
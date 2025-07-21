#!/usr/bin/env python3
"""
Performance Tracking System for Yoga Coach

Tracks angle measurements over time, compares current performance to history,
identifies improvements and personal bests, and provides data-driven feedback.
"""

import os
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AngleMeasurement:
    """Individual angle measurement"""
    pose: str
    angle_name: str
    value: float
    timestamp: datetime
    session_id: str
    
    def to_dict(self):
        return {
            'pose': self.pose,
            'angle_name': self.angle_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            pose=data['pose'],
            angle_name=data['angle_name'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            session_id=data['session_id']
        )


@dataclass
class PerformanceStats:
    """Performance statistics for an angle"""
    current_value: float
    daily_best: Optional[float]
    historical_average: Optional[float]
    personal_best: Optional[float]
    improvement_vs_average: Optional[float]
    is_daily_best: bool
    is_personal_best: bool
    
    
class PerformanceTracker:
    """Tracks yoga pose performance over time"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.performance_file = self.data_dir / "performance_history.json"
        self.daily_stats_file = self.data_dir / "daily_stats.json"
        self.personal_bests_file = self.data_dir / "personal_bests.json"
        
        # Load existing data
        self.performance_history = self._load_performance_history()
        self.daily_stats = self._load_daily_stats()
        self.personal_bests = self._load_personal_bests()
        
        # Current session
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_measurements = []
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> dict:
        """Default configuration if file not found"""
        return {
            'performance': {
                'track_angles': True,
                'compare_to_history': True,
                'history_days': 30,
                'improvement_threshold': 2.0,
                'tracked_angles': {
                    'tree_pose': ['standing_leg', 'lifted_leg', 'spine_vertical'],
                    'warrior_2': ['front_knee', 'back_leg', 'hip_alignment'],
                    'downward_dog': ['shoulder_angle', 'hip_angle', 'leg_extension']
                }
            }
        }
    
    def _load_performance_history(self) -> List[AngleMeasurement]:
        """Load historical performance data"""
        if not self.performance_file.exists():
            return []
        
        try:
            with open(self.performance_file, 'r') as f:
                data = json.load(f)
            return [AngleMeasurement.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error loading performance history: {e}")
            return []
    
    def _load_daily_stats(self) -> dict:
        """Load daily statistics"""
        if not self.daily_stats_file.exists():
            return {}
        
        try:
            with open(self.daily_stats_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading daily stats: {e}")
            return {}
    
    def _load_personal_bests(self) -> dict:
        """Load personal best records"""
        if not self.personal_bests_file.exists():
            return {}
        
        try:
            with open(self.personal_bests_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading personal bests: {e}")
            return {}
    
    def record_measurement(self, pose: str, angle_name: str, value: float) -> Optional[PerformanceStats]:
        """Record a new angle measurement and return performance stats"""
        
        # Only track configured angles
        tracked_angles = self.config.get('performance', {}).get('tracked_angles', {})
        if pose not in tracked_angles or angle_name not in tracked_angles[pose]:
            return None
        
        # Create measurement
        measurement = AngleMeasurement(
            pose=pose,
            angle_name=angle_name,
            value=value,
            timestamp=datetime.now(),
            session_id=self.session_id
        )
        
        # Add to session and history
        self.session_measurements.append(measurement)
        self.performance_history.append(measurement)
        
        # Calculate performance stats
        stats = self._calculate_performance_stats(pose, angle_name, value)
        
        # Update records if needed
        self._update_daily_stats(pose, angle_name, value, stats.is_daily_best)
        self._update_personal_bests(pose, angle_name, value, stats.is_personal_best)
        
        return stats
    
    def _calculate_performance_stats(self, pose: str, angle_name: str, current_value: float) -> PerformanceStats:
        """Calculate performance statistics for current measurement"""
        
        today = datetime.now().date()
        history_days = self.config.get('performance', {}).get('history_days', 30)
        cutoff_date = datetime.now() - timedelta(days=history_days)
        
        # Filter relevant measurements
        relevant_measurements = [
            m for m in self.performance_history
            if m.pose == pose and m.angle_name == angle_name and m.timestamp >= cutoff_date
        ]
        
        # Today's measurements
        today_measurements = [
            m for m in relevant_measurements
            if m.timestamp.date() == today
        ]
        
        # Calculate stats
        daily_best = max([m.value for m in today_measurements], default=None) if today_measurements else None
        historical_average = sum([m.value for m in relevant_measurements]) / len(relevant_measurements) if relevant_measurements else None
        
        # Personal best (all time)
        all_measurements = [
            m for m in self.performance_history
            if m.pose == pose and m.angle_name == angle_name
        ]
        personal_best = max([m.value for m in all_measurements], default=None) if all_measurements else None
        
        # Determine if this is a record
        is_daily_best = daily_best is None or current_value > daily_best
        is_personal_best = personal_best is None or current_value > personal_best
        
        # Calculate improvement
        improvement_vs_average = None
        if historical_average is not None:
            improvement_vs_average = current_value - historical_average
        
        return PerformanceStats(
            current_value=current_value,
            daily_best=daily_best,
            historical_average=historical_average,
            personal_best=personal_best,
            improvement_vs_average=improvement_vs_average,
            is_daily_best=is_daily_best,
            is_personal_best=is_personal_best
        )
    
    def _update_daily_stats(self, pose: str, angle_name: str, value: float, is_best: bool):
        """Update daily statistics"""
        today_str = datetime.now().date().isoformat()
        
        if today_str not in self.daily_stats:
            self.daily_stats[today_str] = {}
        
        key = f"{pose}_{angle_name}"
        if key not in self.daily_stats[today_str] or is_best:
            self.daily_stats[today_str][key] = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_personal_bests(self, pose: str, angle_name: str, value: float, is_best: bool):
        """Update personal best records"""
        if not is_best:
            return
        
        key = f"{pose}_{angle_name}"
        self.personal_bests[key] = {
            'value': value,
            'date': datetime.now().date().isoformat(),
            'session_id': self.session_id
        }
    
    def get_session_summary(self) -> dict:
        """Get summary of current session performance"""
        improvements = 0
        personal_bests = 0
        daily_bests = 0
        
        improvement_threshold = self.config.get('performance', {}).get('improvement_threshold', 2.0)
        
        for measurement in self.session_measurements:
            stats = self._calculate_performance_stats(
                measurement.pose, 
                measurement.angle_name, 
                measurement.value
            )
            
            if stats.is_personal_best:
                personal_bests += 1
            elif stats.is_daily_best:
                daily_bests += 1
            elif stats.improvement_vs_average and stats.improvement_vs_average >= improvement_threshold:
                improvements += 1
        
        return {
            'measurements_taken': len(self.session_measurements),
            'improvements': improvements,
            'daily_bests': daily_bests,
            'personal_bests': personal_bests,
            'session_duration': self._get_session_duration(),
            'poses_practiced': list(set([m.pose for m in self.session_measurements]))
        }
    
    def _get_session_duration(self) -> float:
        """Get session duration in minutes"""
        if not self.session_measurements:
            return 0
        
        start_time = min([m.timestamp for m in self.session_measurements])
        end_time = max([m.timestamp for m in self.session_measurements])
        return (end_time - start_time).total_seconds() / 60
    
    def should_provide_feedback(self, pose: str, angle_name: str, current_value: float) -> Tuple[bool, str]:
        """Determine if feedback should be provided and what type"""
        
        stats = self._calculate_performance_stats(pose, angle_name, current_value)
        improvement_threshold = self.config.get('performance', {}).get('improvement_threshold', 2.0)
        
        if stats.is_personal_best:
            return True, "personal_best"
        elif stats.is_daily_best:
            return True, "daily_best"
        elif stats.improvement_vs_average and stats.improvement_vs_average >= improvement_threshold:
            return True, "improvement"
        
        return False, "none"
    
    def save_data(self):
        """Save all performance data to files"""
        try:
            # Save performance history
            with open(self.performance_file, 'w') as f:
                json.dump([m.to_dict() for m in self.performance_history], f, indent=2)
            
            # Save daily stats
            with open(self.daily_stats_file, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
            
            # Save personal bests
            with open(self.personal_bests_file, 'w') as f:
                json.dump(self.personal_bests, f, indent=2)
                
            print(f"💾 Performance data saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving performance data: {e}")
    
    def get_trend_analysis(self, pose: str, angle_name: str, days: int = 7) -> dict:
        """Get trend analysis for a specific angle over recent days"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_measurements = [
            m for m in self.performance_history
            if m.pose == pose and m.angle_name == angle_name and m.timestamp >= cutoff_date
        ]
        
        if len(recent_measurements) < 2:
            return {"trend": "insufficient_data"}
        
        # Group by day and get daily averages
        daily_averages = {}
        for measurement in recent_measurements:
            day = measurement.timestamp.date()
            if day not in daily_averages:
                daily_averages[day] = []
            daily_averages[day].append(measurement.value)
        
        daily_avg_values = [
            sum(values) / len(values) 
            for values in daily_averages.values()
        ]
        
        # Calculate trend
        if len(daily_avg_values) < 2:
            return {"trend": "insufficient_data"}
        
        first_half = daily_avg_values[:len(daily_avg_values)//2]
        second_half = daily_avg_values[len(daily_avg_values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        improvement = second_avg - first_avg
        
        return {
            "trend": "improving" if improvement > 1 else "declining" if improvement < -1 else "stable",
            "improvement": improvement,
            "recent_average": second_avg,
            "days_analyzed": days,
            "data_points": len(recent_measurements)
        } 
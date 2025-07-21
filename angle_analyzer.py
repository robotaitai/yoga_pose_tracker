#!/usr/bin/env python3
"""
Yoga Pose Angle Analyzer - Critical Angle Analysis and Feedback System

Analyzes body angles and provides coaching feedback for yoga poses.
Calculates joint angles, alignment, and posture quality metrics.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
from dataclasses import dataclass
from enum import Enum


class AngleFeedback(Enum):
    """Types of angle feedback"""
    PERFECT = "perfect"
    GOOD = "good"
    NEEDS_ADJUSTMENT = "needs_adjustment"
    POOR = "poor"


@dataclass
class AngleRequirement:
    """Defines angle requirements for a specific measurement"""
    name: str
    min_angle: float
    max_angle: float
    optimal_angle: float
    tolerance: float = 10.0
    description: str = ""
    feedback_messages: Dict[str, str] = None


@dataclass
class AngleAnalysis:
    """Result of angle analysis"""
    angle_name: str
    measured_angle: float
    required_angle: float
    deviation: float
    feedback_level: AngleFeedback
    message: str
    improvement_tip: str


class BodyAngleCalculator:
    """Calculate various body angles from pose keypoints"""
    
    @staticmethod
    def calculate_angle_3_points(p1: List[float], p2: List[float], p3: List[float]) -> float:
        """
        Calculate angle at point p2 formed by p1-p2-p3
        
        Args:
            p1, p2, p3: Points as [x, y] coordinates
            
        Returns:
            Angle in degrees (0-180)
        """
        if not all([p1, p2, p3]):
            return -1  # Invalid measurement
        
        # Convert to numpy arrays
        p1, p2, p3 = np.array(p1), np.array(p2), np.array(p3)
        
        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
        # Clamp to avoid numerical errors
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        # Convert to degrees
        angle = math.degrees(math.acos(cos_angle))
        return angle
    
    @staticmethod
    def calculate_line_angle(p1: List[float], p2: List[float]) -> float:
        """
        Calculate angle of line from horizontal
        
        Args:
            p1, p2: Points as [x, y] coordinates
            
        Returns:
            Angle in degrees (-90 to 90)
        """
        if not all([p1, p2]):
            return -999  # Invalid measurement
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        angle = math.degrees(math.atan2(dy, dx))
        return angle
    
    def calculate_pose_angles(self, keypoints: Dict) -> Dict[str, float]:
        """
        Calculate all important angles from pose keypoints
        
        Args:
            keypoints: Dictionary of pose keypoints
            
        Returns:
            Dictionary of calculated angles
        """
        angles = {}
        
        # Knee angles
        angles['left_knee'] = self.calculate_angle_3_points(
            keypoints.get('left_hip'), 
            keypoints.get('left_knee'), 
            keypoints.get('left_ankle')
        )
        
        angles['right_knee'] = self.calculate_angle_3_points(
            keypoints.get('right_hip'), 
            keypoints.get('right_knee'), 
            keypoints.get('right_ankle')
        )
        
        # Elbow angles
        angles['left_elbow'] = self.calculate_angle_3_points(
            keypoints.get('left_shoulder'), 
            keypoints.get('left_elbow'), 
            keypoints.get('left_wrist')
        )
        
        angles['right_elbow'] = self.calculate_angle_3_points(
            keypoints.get('right_shoulder'), 
            keypoints.get('right_elbow'), 
            keypoints.get('right_wrist')
        )
        
        # Hip angles (thigh to torso)
        angles['left_hip'] = self.calculate_angle_3_points(
            keypoints.get('left_shoulder'), 
            keypoints.get('left_hip'), 
            keypoints.get('left_knee')
        )
        
        angles['right_hip'] = self.calculate_angle_3_points(
            keypoints.get('right_shoulder'), 
            keypoints.get('right_hip'), 
            keypoints.get('right_knee')
        )
        
        # Shoulder alignment
        angles['shoulder_line'] = self.calculate_line_angle(
            keypoints.get('left_shoulder'), 
            keypoints.get('right_shoulder')
        )
        
        # Hip alignment
        angles['hip_line'] = self.calculate_line_angle(
            keypoints.get('left_hip'), 
            keypoints.get('right_hip')
        )
        
        # Spine angle (simplified as shoulder to hip center)
        if (keypoints.get('left_shoulder') and keypoints.get('right_shoulder') and 
            keypoints.get('left_hip') and keypoints.get('right_hip')):
            
            shoulder_center = [
                (keypoints['left_shoulder'][0] + keypoints['right_shoulder'][0]) / 2,
                (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
            ]
            hip_center = [
                (keypoints['left_hip'][0] + keypoints['right_hip'][0]) / 2,
                (keypoints['left_hip'][1] + keypoints['right_hip'][1]) / 2
            ]
            
            angles['spine_vertical'] = abs(self.calculate_line_angle(hip_center, shoulder_center) - 90)
        
        # Arm angles (arm to torso)
        if (keypoints.get('left_shoulder') and keypoints.get('left_elbow') and 
            keypoints.get('left_hip')):
            angles['left_arm_torso'] = self.calculate_angle_3_points(
                keypoints.get('left_hip'), 
                keypoints.get('left_shoulder'), 
                keypoints.get('left_elbow')
            )
        
        if (keypoints.get('right_shoulder') and keypoints.get('right_elbow') and 
            keypoints.get('right_hip')):
            angles['right_arm_torso'] = self.calculate_angle_3_points(
                keypoints.get('right_hip'), 
                keypoints.get('right_shoulder'), 
                keypoints.get('right_elbow')
            )
        
        # Filter out invalid measurements
        valid_angles = {k: v for k, v in angles.items() if v >= 0 and v <= 180}
        
        return valid_angles


class CriticalAngleDatabase:
    """Database of critical angles for different yoga poses"""
    
    def __init__(self):
        self.pose_requirements = self._load_default_requirements()
    
    def _load_default_requirements(self) -> Dict[str, List[AngleRequirement]]:
        """Load default angle requirements for common poses"""
        
        return {
            "warrior_2": [
                AngleRequirement(
                    name="front_knee",
                    min_angle=85,
                    max_angle=95,
                    optimal_angle=90,
                    tolerance=5,
                    description="Front leg should be bent at 90 degrees",
                    feedback_messages={
                        "perfect": "Perfect 90-degree front knee! Excellent warrior pose.",
                        "good": "Good knee angle, very close to 90 degrees.",
                        "needs_adjustment": "Bend your front knee more to reach 90 degrees.",
                        "poor": "Front knee needs significant adjustment - aim for 90 degrees."
                    }
                ),
                AngleRequirement(
                    name="back_leg",
                    min_angle=160,
                    max_angle=180,
                    optimal_angle=175,
                    tolerance=10,
                    description="Back leg should be straight",
                    feedback_messages={
                        "perfect": "Back leg perfectly straight! Great foundation.",
                        "good": "Back leg looking good, nearly straight.",
                        "needs_adjustment": "Straighten your back leg more.",
                        "poor": "Back leg needs to be much straighter."
                    }
                ),
                AngleRequirement(
                    name="hip_alignment",
                    min_angle=-5,
                    max_angle=5,
                    optimal_angle=0,
                    tolerance=3,
                    description="Hips should be level",
                    feedback_messages={
                        "perfect": "Hips perfectly level! Excellent alignment.",
                        "good": "Hip alignment is good.",
                        "needs_adjustment": "Adjust your hips to be more level.",
                        "poor": "Focus on leveling your hips."
                    }
                )
            ],
            
            "tree_pose": [
                AngleRequirement(
                    name="standing_leg",
                    min_angle=170,
                    max_angle=180,
                    optimal_angle=175,
                    tolerance=5,
                    description="Standing leg should be straight and strong",
                    feedback_messages={
                        "perfect": "Standing leg perfectly straight! Solid foundation.",
                        "good": "Standing leg looks stable.",
                        "needs_adjustment": "Straighten your standing leg more.",
                        "poor": "Focus on keeping your standing leg straight."
                    }
                ),
                AngleRequirement(
                    name="lifted_leg",
                    min_angle=45,
                    max_angle=90,
                    optimal_angle=70,
                    tolerance=15,
                    description="Lifted leg should create good angle",
                    feedback_messages={
                        "perfect": "Perfect leg lift angle! Great tree pose.",
                        "good": "Good leg position.",
                        "needs_adjustment": "Try lifting your leg higher.",
                        "poor": "Lift your leg higher for better tree pose."
                    }
                ),
                AngleRequirement(
                    name="spine_vertical",
                    min_angle=0,
                    max_angle=10,
                    optimal_angle=0,
                    tolerance=5,
                    description="Spine should be vertical",
                    feedback_messages={
                        "perfect": "Spine perfectly upright! Excellent posture.",
                        "good": "Good spinal alignment.",
                        "needs_adjustment": "Stand up straighter.",
                        "poor": "Focus on keeping your spine vertical."
                    }
                )
            ],
            
            "downward_dog": [
                AngleRequirement(
                    name="shoulder_angle",
                    min_angle=40,
                    max_angle=60,
                    optimal_angle=50,
                    tolerance=8,
                    description="Shoulder angle creates inverted V",
                    feedback_messages={
                        "perfect": "Perfect downward dog angle! Great inverted V.",
                        "good": "Good downward dog position.",
                        "needs_adjustment": "Adjust your shoulder angle slightly.",
                        "poor": "Work on creating a better inverted V shape."
                    }
                ),
                AngleRequirement(
                    name="left_knee",
                    min_angle=160,
                    max_angle=180,
                    optimal_angle=175,
                    tolerance=10,
                    description="Legs should be straight",
                    feedback_messages={
                        "perfect": "Legs perfectly straight! Excellent foundation.",
                        "good": "Good leg extension.",
                        "needs_adjustment": "Try to straighten your legs more.",
                        "poor": "Focus on straightening both legs."
                    }
                ),
                AngleRequirement(
                    name="right_knee",
                    min_angle=160,
                    max_angle=180,
                    optimal_angle=175,
                    tolerance=10,
                    description="Legs should be straight",
                    feedback_messages={
                        "perfect": "Legs perfectly straight! Excellent foundation.",
                        "good": "Good leg extension.",
                        "needs_adjustment": "Try to straighten your legs more.",
                        "poor": "Focus on straightening both legs."
                    }
                )
            ]
        }
    
    def get_requirements(self, pose_name: str) -> List[AngleRequirement]:
        """Get angle requirements for a specific pose"""
        return self.pose_requirements.get(pose_name.lower(), [])
    
    def add_pose_requirements(self, pose_name: str, requirements: List[AngleRequirement]):
        """Add new pose requirements"""
        self.pose_requirements[pose_name.lower()] = requirements
    
    def save_to_file(self, filepath: str):
        """Save requirements to JSON file"""
        data = {}
        for pose_name, requirements in self.pose_requirements.items():
            data[pose_name] = []
            for req in requirements:
                req_dict = {
                    "name": req.name,
                    "min_angle": req.min_angle,
                    "max_angle": req.max_angle,
                    "optimal_angle": req.optimal_angle,
                    "tolerance": req.tolerance,
                    "description": req.description,
                    "feedback_messages": req.feedback_messages or {}
                }
                data[pose_name].append(req_dict)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load requirements from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.pose_requirements = {}
            for pose_name, req_list in data.items():
                requirements = []
                for req_dict in req_list:
                    req = AngleRequirement(
                        name=req_dict["name"],
                        min_angle=req_dict["min_angle"],
                        max_angle=req_dict["max_angle"],
                        optimal_angle=req_dict["optimal_angle"],
                        tolerance=req_dict.get("tolerance", 10.0),
                        description=req_dict.get("description", ""),
                        feedback_messages=req_dict.get("feedback_messages", {})
                    )
                    requirements.append(req)
                self.pose_requirements[pose_name] = requirements
        
        except FileNotFoundError:
            print(f"Critical angles file not found: {filepath}")
        except Exception as e:
            print(f"Error loading critical angles: {e}")


class PostureAnalyzer:
    """Analyzes pose angles and provides feedback"""
    
    def __init__(self, angle_database: CriticalAngleDatabase = None):
        self.calculator = BodyAngleCalculator()
        self.angle_db = angle_database or CriticalAngleDatabase()
    
    def analyze_pose(self, pose_name: str, keypoints: Dict) -> List[AngleAnalysis]:
        """
        Analyze a pose and return detailed feedback
        
        Args:
            pose_name: Name of the pose being performed
            keypoints: Current pose keypoints
            
        Returns:
            List of angle analyses with feedback
        """
        # Calculate current angles
        current_angles = self.calculator.calculate_pose_angles(keypoints)
        
        # Get requirements for this pose
        requirements = self.angle_db.get_requirements(pose_name)
        
        analyses = []
        
        for requirement in requirements:
            angle_name = requirement.name
            
            # Find corresponding measured angle
            measured_angle = None
            if angle_name in current_angles:
                measured_angle = current_angles[angle_name]
            elif angle_name == "front_knee":
                # For warrior pose, assume left knee is front
                measured_angle = current_angles.get("left_knee")
            elif angle_name == "back_leg":
                # For warrior pose, assume right knee is back
                measured_angle = current_angles.get("right_knee")
            elif angle_name == "standing_leg":
                # For tree pose, assume right leg is standing
                measured_angle = current_angles.get("right_knee")
            elif angle_name == "lifted_leg":
                # For tree pose, calculate lifted leg angle
                measured_angle = current_angles.get("left_hip")
            elif angle_name == "shoulder_angle":
                # For downward dog, use arm-torso angle
                left_arm = current_angles.get("left_arm_torso", 0)
                right_arm = current_angles.get("right_arm_torso", 0)
                if left_arm > 0 and right_arm > 0:
                    measured_angle = (left_arm + right_arm) / 2
            elif angle_name == "hip_alignment":
                measured_angle = abs(current_angles.get("hip_line", 0))
            
            if measured_angle is None or measured_angle < 0:
                continue  # Skip if angle couldn't be measured
            
            # Analyze the angle
            analysis = self._analyze_single_angle(requirement, measured_angle)
            analyses.append(analysis)
        
        return analyses
    
    def _analyze_single_angle(self, requirement: AngleRequirement, measured_angle: float) -> AngleAnalysis:
        """Analyze a single angle measurement"""
        
        deviation = abs(measured_angle - requirement.optimal_angle)
        
        # Determine feedback level
        if deviation <= requirement.tolerance:
            if deviation <= requirement.tolerance / 2:
                feedback_level = AngleFeedback.PERFECT
            else:
                feedback_level = AngleFeedback.GOOD
        elif (requirement.min_angle <= measured_angle <= requirement.max_angle):
            feedback_level = AngleFeedback.NEEDS_ADJUSTMENT
        else:
            feedback_level = AngleFeedback.POOR
        
        # Get feedback message
        message = requirement.feedback_messages.get(
            feedback_level.value, 
            f"Angle is {measured_angle:.1f}°, target is {requirement.optimal_angle:.1f}°"
        )
        
        # Generate improvement tip
        if measured_angle < requirement.optimal_angle:
            improvement_tip = f"Increase angle by {requirement.optimal_angle - measured_angle:.1f}°"
        elif measured_angle > requirement.optimal_angle:
            improvement_tip = f"Decrease angle by {measured_angle - requirement.optimal_angle:.1f}°"
        else:
            improvement_tip = "Perfect! Maintain this position."
        
        return AngleAnalysis(
            angle_name=requirement.name,
            measured_angle=measured_angle,
            required_angle=requirement.optimal_angle,
            deviation=deviation,
            feedback_level=feedback_level,
            message=message,
            improvement_tip=improvement_tip
        )
    
    def get_overall_score(self, analyses: List[AngleAnalysis]) -> Tuple[float, str]:
        """
        Calculate overall pose score
        
        Returns:
            Tuple of (score_0_to_100, grade_text)
        """
        if not analyses:
            return 0, "No data"
        
        total_score = 0
        for analysis in analyses:
            if analysis.feedback_level == AngleFeedback.PERFECT:
                total_score += 100
            elif analysis.feedback_level == AngleFeedback.GOOD:
                total_score += 85
            elif analysis.feedback_level == AngleFeedback.NEEDS_ADJUSTMENT:
                total_score += 70
            else:  # POOR
                total_score += 50
        
        average_score = total_score / len(analyses)
        
        if average_score >= 95:
            grade = "Excellent!"
        elif average_score >= 85:
            grade = "Very Good"
        elif average_score >= 75:
            grade = "Good"
        elif average_score >= 65:
            grade = "Fair"
        else:
            grade = "Needs Work"
        
        return average_score, grade


# Example usage and testing
if __name__ == "__main__":
    print("🧘 Testing Angle Analyzer")
    print("=" * 40)
    
    # Create sample keypoints for warrior 2 pose
    sample_keypoints = {
        "left_shoulder": [0.35, 0.25],
        "right_shoulder": [0.65, 0.25],
        "left_hip": [0.42, 0.50],
        "right_hip": [0.58, 0.50],
        "left_knee": [0.40, 0.70],  # Bent knee (front leg)
        "right_knee": [0.60, 0.70],  # Straight knee (back leg)
        "left_ankle": [0.38, 0.90],
        "right_ankle": [0.62, 0.90],
        "left_elbow": [0.20, 0.35],
        "right_elbow": [0.80, 0.35],
        "left_wrist": [0.15, 0.40],
        "right_wrist": [0.85, 0.40]
    }
    
    # Test angle calculation
    calculator = BodyAngleCalculator()
    angles = calculator.calculate_pose_angles(sample_keypoints)
    
    print("Calculated angles:")
    for name, angle in angles.items():
        print(f"  {name}: {angle:.1f}°")
    
    # Test posture analysis
    analyzer = PostureAnalyzer()
    analyses = analyzer.analyze_pose("warrior_2", sample_keypoints)
    
    print(f"\nWarrior 2 Analysis:")
    for analysis in analyses:
        print(f"  {analysis.angle_name}: {analysis.measured_angle:.1f}° "
              f"({analysis.feedback_level.value})")
        print(f"    {analysis.message}")
    
    score, grade = analyzer.get_overall_score(analyses)
    print(f"\nOverall Score: {score:.1f}/100 ({grade})") 
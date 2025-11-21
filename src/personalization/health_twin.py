# 👥 Health Twin - Personalized Baseline Learning Engine

"""
Digital Health Twin that learns each patient's unique baseline and detects
anomalies specific to their individual physiology.

Key Concept:
- Your "normal" HR might be 55 bpm (athlete)
- Someone else's "normal" might be 85 bpm (sedentary)
- Generic thresholds miss personalized patterns

The Health Twin learns YOUR normal over 90 days and alerts when YOU deviate.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import pickle
import json

class BaselineStatus(Enum):
    """Learning status"""
    LEARNING = "learning"          # < 7 days
    PRELIMINARY = "preliminary"    # 7-30 days
    ESTABLISHED = "established"    # 30-90 days
    MATURE = "mature"              # > 90 days

@dataclass
class PersonalBaseline:
    """Individual baseline for one vital sign"""
    metric_name: str
    mean: float
    std: float
    min_normal: float
    max_normal: float
    percentile_5: float
    percentile_95: float
    samples_count: int
    last_updated: float
    circadian_pattern: Optional[Dict] = None  # Hour of day patterns
    
    def is_anomaly(self, value: float, threshold_std: float = 2.0) -> bool:
        """Check if value is anomalous for this person"""
        z_score = abs(value - self.mean) / self.std if self.std > 0 else 0
        return z_score > threshold_std
    
    def get_deviation(self, value: float) -> float:
        """Get how many standard deviations from personal baseline"""
        return (value - self.mean) / self.std if self.std > 0 else 0

@dataclass  
class HealthTwin:
    """
    Digital twin that learns individual health patterns
    
    Learns:
    - Resting heart rate baseline
    - HRV (heart rate variability) baseline
    - SpO2 baseline
    - Respiratory rate baseline
    - Activity patterns
    - Sleep patterns
    - Circadian rhythms
    """
    
    patient_id: str
    created_at: float
    baselines: Dict[str, PersonalBaseline] = field(default_factory=dict)
    historical_data: List[Dict] = field(default_factory=list)
    anomaly_history: List[Dict] = field(default_factory=list)
    
    @property
    def status(self) -> BaselineStatus:
        """Determine learning status"""
        age_days = (datetime.now().timestamp() - self.created_at) / 86400
        
        if age_days < 7:
            return BaselineStatus.LEARNING
        elif age_days < 30:
            return BaselineStatus.PRELIMINARY
        elif age_days < 90:
            return BaselineStatus.ESTABLISHED
        else:
            return BaselineStatus.MATURE
    
    @property
    def confidence(self) -> float:
        """Confidence in baseline (0-1)"""
        age_days = (datetime.now().timestamp() - self.created_at) / 86400
        samples = len(self.historical_data)
        
        # Need both time and samples
        time_factor = min(age_days / 90, 1.0)  # Full confidence at 90 days
        sample_factor = min(samples / 1000, 1.0)  # Full confidence at 1000 samples
        
        return (time_factor + sample_factor) / 2
    
    def add_data_point(self, vitals: Dict):
        """Add new vital sign measurement to learn from"""
        
        timestamp = datetime.now().timestamp()
        
        # Store historical data
        data_point = {
            'timestamp': timestamp,
            **vitals
        }
        self.historical_data.append(data_point)
        
        # Update baselines for each metric
        for metric, value in vitals.items():
            if metric not in self.baselines:
                # Initialize baseline
                self.baselines[metric] = PersonalBaseline(
                    metric_name=metric,
                    mean=value,
                    std=0.0,
                    min_normal=value,
                    max_normal=value,
                    percentile_5=value,
                    percentile_95=value,
                    samples_count=1,
                    last_updated=timestamp
                )
            else:
                # Update baseline (incremental statistics)
                self._update_baseline(metric, value, timestamp)
    
    def _update_baseline(self, metric: str, new_value: float, timestamp: float):
        """Update baseline statistics incrementally"""
        
        baseline = self.baselines[metric]
        
        # Incremental mean and variance (Welford's algorithm)
        n = baseline.samples_count + 1
        delta = new_value - baseline.mean
        new_mean = baseline.mean + delta / n
        delta2 = new_value - new_mean
        new_variance = ((n - 1) * baseline.std ** 2 + delta * delta2) / n
        
        baseline.mean = new_mean
        baseline.std = np.sqrt(new_variance)
        baseline.samples_count = n
        baseline.last_updated = timestamp
        
        # Update min/max
        baseline.min_normal = min(baseline.min_normal, new_value)
        baseline.max_normal = max(baseline.max_normal, new_value)
        
        # Recompute percentiles (every 100 samples)
        if n % 100 == 0:
            self._recompute_percentiles(metric)
    
    def _recompute_percentiles(self, metric: str):
        """Recompute percentiles from historical data"""
        
        # Get all values for this metric
        values = [
            d[metric] for d in self.historical_data 
            if metric in d
        ]
        
        if values:
            baseline = self.baselines[metric]
            baseline.percentile_5 = np.percentile(values, 5)
            baseline.percentile_95 = np.percentile(values, 95)
    
    def detect_anomalies(self, current_vitals: Dict) -> List[Dict]:
        """
        Detect personalized anomalies
        
        Returns list of anomalies with severity
        """
        
        anomalies = []
        
        for metric, value in current_vitals.items():
            if metric not in self.baselines:
                continue  # Can't detect anomaly without baseline
            
            baseline = self.baselines[metric]
            
            # Check if anomalous
            if baseline.is_anomaly(value, threshold_std=2.0):
                deviation = baseline.get_deviation(value)
                
                # Determine severity
                if abs(deviation) > 3.0:
                    severity = "critical"
                elif abs(deviation) > 2.5:
                    severity = "high"
                elif abs(deviation) > 2.0:
                    severity = "moderate"
                else:
                    severity = "low"
                
                anomaly = {
                    'metric': metric,
                    'current_value': value,
                    'personal_baseline': baseline.mean,
                    'deviation_std': deviation,
                    'severity': severity,
                    'timestamp': datetime.now().timestamp(),
                    'explanation': self._explain_anomaly(metric, value, baseline, deviation)
                }
                
                anomalies.append(anomaly)
                self.anomaly_history.append(anomaly)
        
        return anomalies
    
    def _explain_anomaly(
        self, 
        metric: str, 
        value: float, 
        baseline: PersonalBaseline,
        deviation: float
    ) -> str:
        """Generate human-readable explanation"""
        
        direction = "higher" if deviation > 0 else "lower"
        
        explanation = (
            f"Your {metric} is {value:.1f}, which is {abs(deviation):.1f} standard deviations "
            f"{direction} than your personal baseline of {baseline.mean:.1f}. "
            f"Your normal range is {baseline.percentile_5:.1f}-{baseline.percentile_95:.1f}."
        )
        
        return explanation
    
    def get_personalized_thresholds(self, metric: str) -> Dict:
        """Get personalized alert thresholds"""
        
        if metric not in self.baselines:
            # Use generic thresholds
            generic_thresholds = {
                'heart_rate': {'low': 60, 'high': 100},
                'spo2': {'low': 95, 'high': 100},
                'respiratory_rate': {'low': 12, 'high': 20}
            }
            return generic_thresholds.get(metric, {'low': 0, 'high': 1000})
        
        baseline = self.baselines[metric]
        
        # Use 2 std as threshold (covers 95% of normal variation)
        return {
            'low': baseline.mean - 2 * baseline.std,
            'high': baseline.mean + 2 * baseline.std,
            'baseline': baseline.mean,
            'confidence': self.confidence
        }
    
    def predict_future_baseline(self, hours_ahead: int) -> Dict:
        """
        Predict future baseline based on circadian patterns
        
        Useful for: "Your HR usually drops to 60 bpm at night, 
                     but it's still 85 bpm - this is unusual for you"
        """
        
        predictions = {}
        
        for metric, baseline in self.baselines.items():
            if baseline.circadian_pattern:
                target_hour = (datetime.now().hour + hours_ahead) % 24
                predicted_value = baseline.circadian_pattern.get(
                    target_hour, 
                    baseline.mean
                )
            else:
                predicted_value = baseline.mean  # No pattern, use mean
            
            predictions[metric] = {
                'predicted_value': predicted_value,
                'current_baseline': baseline.mean,
                'hours_ahead': hours_ahead
            }
        
        return predictions
    
    def get_health_summary(self) -> str:
        """Generate personalized health summary"""
        
        summary = f"""
# 👥 Your Personal Health Twin

**Learning Status:** {self.status.value.title()}
**Confidence:** {self.confidence:.0%}
**Data Points:** {len(self.historical_data):,}
**Days Active:** {(datetime.now().timestamp() - self.created_at) / 86400:.0f}

## 📊 Your Personal Baselines

"""
        
        for metric, baseline in self.baselines.items():
            summary += f"### {metric.replace('_', ' ').title()}\n"
            summary += f"- **Your Normal:** {baseline.mean:.1f} ± {baseline.std:.1f}\n"
            summary += f"- **Your Range:** {baseline.percentile_5:.1f} - {baseline.percentile_95:.1f}\n"
            summary += f"- **Samples:** {baseline.samples_count:,}\n\n"
        
        # Recent anomalies
        recent_anomalies = [a for a in self.anomaly_history if 
                           datetime.now().timestamp() - a['timestamp'] < 86400]
        
        if recent_anomalies:
            summary += f"\n## ⚠️ Recent Anomalies (Last 24 hours)\n\n"
            for a in recent_anomalies:
                summary += f"- **{a['metric']}:** {a['explanation']}\n"
        
        return summary
    
    def save(self, filepath: str):
        """Save Health Twin to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filepath: str) -> 'HealthTwin':
        """Load Health Twin from file"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)


class HealthTwinManager:
    """
    Manages Health Twins for all patients
    """
    
    def __init__(self, storage_dir: str = "data/health_twins"):
        self.storage_dir = storage_dir
        self.active_twins: Dict[str, HealthTwin] = {}
    
    def get_or_create_twin(self, patient_id: str) -> HealthTwin:
        """Get existing twin or create new one"""
        
        if patient_id in self.active_twins:
            return self.active_twins[patient_id]
        
        # Try to load from disk
        filepath = f"{self.storage_dir}/{patient_id}.pkl"
        try:
            twin = HealthTwin.load(filepath)
            self.active_twins[patient_id] = twin
            return twin
        except FileNotFoundError:
            # Create new twin
            twin = HealthTwin(
                patient_id=patient_id,
                created_at=datetime.now().timestamp()
            )
            self.active_twins[patient_id] = twin
            return twin
    
    def update_twin(self, patient_id: str, vitals: Dict):
        """Update twin with new data"""
        twin = self.get_or_create_twin(patient_id)
        twin.add_data_point(vitals)
        
        # Save to disk every 10 updates
        if len(twin.historical_data) % 10 == 0:
            filepath = f"{self.storage_dir}/{patient_id}.pkl"
            twin.save(filepath)
    
    def check_for_anomalies(self, patient_id: str, current_vitals: Dict) -> List[Dict]:
        """Check current vitals against personal baseline"""
        twin = self.get_or_create_twin(patient_id)
        return twin.detect_anomalies(current_vitals)


# Example usage
def demo_health_twin():
    """Demo of Health Twin learning and anomaly detection"""
    
    import time
    import random
    
    # Create Health Twin
    twin = HealthTwin(
        patient_id="PATIENT_001",
        created_at=time.time()
    )
    
    print("🧬 Creating your digital Health Twin...\n")
    
    # Simulate 30 days of data (athlete with resting HR ~55)
    print("📊 Learning your baseline over 30 days...\n")
    
    for day in range(30):
        for hour in range(24):
            # Simulate realistic HR with circadian rhythm
            # Lower at night (50-60), higher during day (60-70), peak afternoon (70-80)
            if 0 <= hour < 6:  # Night
                base_hr = 55
            elif 6 <= hour < 12:  # Morning
                base_hr = 65
            elif 12 <= hour < 18:  # Afternoon
                base_hr = 72
            else:  # Evening
                base_hr = 62
            
            # Add random variation
            hr = base_hr + random.gauss(0, 5)
            spo2 = 98 + random.gauss(0, 0.5)
            hrv = 55 + random.gauss(0, 8)
            
            twin.add_data_point({
                'heart_rate': hr,
                'spo2': spo2,
                'hrv': hrv
            })
    
    print(f"✅ Baseline established!")
    print(f"Status: {twin.status.value}")
    print(f"Confidence: {twin.confidence:.0%}")
    print(f"Samples: {len(twin.historical_data):,}\n")
    
    # Show learned baselines
    print("📊 Your Personal Baselines:\n")
    for metric, baseline in twin.baselines.items():
        print(f"{metric}:")
        print(f"  Normal: {baseline.mean:.1f} ± {baseline.std:.1f}")
        print(f"  Range: {baseline.percentile_5:.1f} - {baseline.percentile_95:.1f}\n")
    
    # Test anomaly detection
    print("\n🔍 Testing Anomaly Detection:\n")
    
    test_cases = [
        {'heart_rate': 58, 'spo2': 98, 'hrv': 52, 'label': 'Normal day'},
        {'heart_rate': 95, 'spo2': 97, 'hrv': 35, 'label': 'Elevated HR (exercise?)'},
        {'heart_rate': 88, 'spo2': 93, 'hrv': 28, 'label': 'Concerning (low HRV + low SpO2)'},
    ]
    
    for case in test_cases:
        print(f"Test: {case['label']}")
        vitals = {k: v for k, v in case.items() if k != 'label'}
        anomalies = twin.detect_anomalies(vitals)
        
        if anomalies:
            print(f"  ⚠️ {len(anomalies)} anomalies detected:")
            for a in anomalies:
                print(f"     - {a['explanation']}")
                print(f"       Severity: {a['severity']}")
        else:
            print("  ✅ All vitals within your normal range")
        print()
    
    # Show summary
    print("\n" + "="*60)
    print(twin.get_health_summary())

if __name__ == "__main__":
    demo_health_twin()

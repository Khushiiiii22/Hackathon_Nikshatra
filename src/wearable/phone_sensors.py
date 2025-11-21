# 📱 Smartphone Sensor Integration - Real-Time Vital Monitoring

"""
Collect real-time vital signs using smartphone sensors (no wearable required!)

Sensors Used:
1. **Camera** - Photoplethysmography (PPG) for HR, SpO2
2. **Accelerometer** - Respiratory rate, activity level
3. **Microphone** - Cough detection, breathing sounds
4. **GPS** - Location for emergency services
5. **Proximity sensor** - User engagement

How it works:
- User places finger on camera lens (flash on)
- Phone detects blood volume changes from skin color
- Extracts HR, HRV, SpO2 from PPG signal
- Accelerometer tracks breathing (chest movement)
"""

from typing import Dict, Optional
from dataclasses import dataclass
import asyncio
import time
import numpy as np
from collections import deque

@dataclass
class PhoneSensorReading:
    """Single sensor reading from phone"""
    timestamp: float
    heart_rate: Optional[int] = None
    hrv_ms: Optional[float] = None
    spo2: Optional[float] = None
    respiratory_rate: Optional[int] = None
    temperature: Optional[float] = None  # Estimated from processing heat
    activity_level: Optional[int] = None
    location: Optional[tuple] = None  # (lat, lon)
    
class PhoneSensorMonitor:
    """
    Monitor vitals using smartphone sensors
    
    Frontend Integration:
    - Uses getUserMedia() to access camera
    - Uses DeviceMotionEvent for accelerometer
    - Uses MediaRecorder for microphone
    - Uses Geolocation API for location
    """
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.is_monitoring = False
        self.reading_buffer = deque(maxlen=300)  # 5 min at 1Hz
        
        # Simulated sensor connections (replace with actual API calls)
        self.camera_active = False
        self.accel_active = False
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.is_monitoring = True
        
        # Start sensor streams
        await asyncio.gather(
            self._monitor_camera_ppg(),
            self._monitor_accelerometer(),
            self._monitor_microphone()
        )
    
    async def _monitor_camera_ppg(self):
        """
        Monitor camera for PPG signal
        
        Frontend Implementation:
        ```javascript
        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',  // Back camera
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });
        
        // Turn on flash/torch
        const track = stream.getVideoTracks()[0];
        await track.applyConstraints({
            advanced: [{ torch: true }]
        });
        
        // Capture frames
        const video = document.createElement('video');
        video.srcObject = stream;
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        setInterval(() => {
            ctx.drawImage(video, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            // Calculate average red channel intensity
            let redSum = 0;
            for (let i = 0; i < imageData.data.length; i += 4) {
                redSum += imageData.data[i];  // Red channel
            }
            const avgRed = redSum / (imageData.data.length / 4);
            
            // Send to backend
            sendPPGSample(avgRed, Date.now());
        }, 33);  // 30 fps
        ```
        """
        
        print("📸 Camera PPG monitoring started (place finger on camera)")
        
        while self.is_monitoring:
            # Simulate PPG signal processing
            # In production: receive from frontend WebSocket
            ppg_sample = await self._get_ppg_sample()
            
            if ppg_sample:
                # Extract vitals from PPG
                vitals = self._process_ppg_signal(ppg_sample)
                
                # Store reading
                reading = PhoneSensorReading(
                    timestamp=time.time(),
                    heart_rate=vitals.get('heart_rate'),
                    hrv_ms=vitals.get('hrv_ms'),
                    spo2=vitals.get('spo2')
                )
                
                self.reading_buffer.append(reading)
            
            await asyncio.sleep(0.033)  # 30 Hz sampling
    
    async def _get_ppg_sample(self) -> Optional[float]:
        """
        Get PPG sample from camera
        
        Production: This receives data from WebSocket connection to frontend
        """
        # Simulate realistic PPG signal
        # Real implementation receives from frontend
        
        import random
        base_signal = 128  # Baseline pixel intensity
        heartbeat = np.sin(2 * np.pi * 1.2 * time.time())  # 72 bpm
        noise = random.gauss(0, 2)
        
        return base_signal + 20 * heartbeat + noise
    
    def _process_ppg_signal(self, ppg_buffer: list) -> Dict:
        """
        Process PPG signal to extract HR, HRV, SpO2
        
        Algorithm:
        1. Bandpass filter (0.5-4 Hz for HR)
        2. Peak detection
        3. Inter-beat intervals (IBI) for HRV
        4. AC/DC ratio for SpO2
        """
        
        if len(self.reading_buffer) < 30:
            return {}  # Need at least 30 samples
        
        # Extract PPG values
        ppg_values = [r.heart_rate or 0 for r in self.reading_buffer]
        
        # Simple peak detection (replace with proper algorithm)
        peaks = self._detect_peaks(ppg_values)
        
        # Calculate HR
        if len(peaks) > 2:
            ibi_ms = np.diff([p[0] for p in peaks]) * 33  # Convert to ms
            hr = 60000 / np.mean(ibi_ms)  # Convert to bpm
            hrv = np.std(ibi_ms)
        else:
            hr = None
            hrv = None
        
        # Estimate SpO2 (simplified - real algorithm uses red/infrared ratio)
        spo2 = 98 + np.random.normal(0, 0.5)  # Placeholder
        
        return {
            'heart_rate': int(hr) if hr else None,
            'hrv_ms': float(hrv) if hrv else None,
            'spo2': float(np.clip(spo2, 85, 100))
        }
    
    def _detect_peaks(self, signal: list) -> list:
        """Simple peak detection"""
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i-1] and signal[i] > signal[i+1]:
                if signal[i] > np.mean(signal):  # Above average
                    peaks.append((i, signal[i]))
        return peaks
    
    async def _monitor_accelerometer(self):
        """
        Monitor accelerometer for respiratory rate
        
        Frontend Implementation:
        ```javascript
        // Request motion permission (iOS 13+)
        if (typeof DeviceMotionEvent.requestPermission === 'function') {
            await DeviceMotionEvent.requestPermission();
        }
        
        // Listen to accelerometer
        window.addEventListener('devicemotion', (event) => {
            const accel = event.accelerationIncludingGravity;
            
            // Send to backend
            sendAccelerometerData({
                x: accel.x,
                y: accel.y,
                z: accel.z,
                timestamp: Date.now()
            });
        });
        ```
        
        User places phone on chest, accelerometer detects breathing
        """
        
        print("📳 Accelerometer monitoring started (place phone on chest)")
        
        while self.is_monitoring:
            # Simulate accelerometer data
            accel_data = await self._get_accelerometer_sample()
            
            if accel_data:
                # Extract respiratory rate
                rr = self._process_accelerometer(accel_data)
                
                # Update latest reading
                if self.reading_buffer:
                    latest = self.reading_buffer[-1]
                    latest.respiratory_rate = rr
            
            await asyncio.sleep(0.1)  # 10 Hz
    
    async def _get_accelerometer_sample(self) -> Optional[Dict]:
        """Get accelerometer sample"""
        # Simulate breathing motion
        breath_freq = 0.25  # 15 breaths/min
        z_accel = np.sin(2 * np.pi * breath_freq * time.time())
        
        return {
            'x': 0,
            'y': 0,
            'z': z_accel,
            'timestamp': time.time()
        }
    
    def _process_accelerometer(self, accel_history: list) -> Optional[int]:
        """Extract respiratory rate from accelerometer"""
        
        # Need enough data
        if len(accel_history) < 100:  # 10 seconds
            return None
        
        # Get Z-axis (perpendicular to chest)
        z_values = [a['z'] for a in accel_history[-100:]]
        
        # Count peaks (breaths)
        peaks = self._detect_peaks(z_values)
        
        # Calculate rate
        if len(peaks) > 2:
            duration_sec = 10
            breaths_per_min = (len(peaks) / duration_sec) * 60
            return int(breaths_per_min)
        
        return None
    
    async def _monitor_microphone(self):
        """
        Monitor microphone for breathing sounds, cough detection
        
        Frontend Implementation:
        ```javascript
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        
        microphone.connect(analyser);
        analyser.fftSize = 2048;
        
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        setInterval(() => {
            analyser.getByteFrequencyData(dataArray);
            
            // Send audio features to backend
            sendAudioData({
                frequency_data: Array.from(dataArray),
                timestamp: Date.now()
            });
        }, 100);
        ```
        """
        
        print("🎤 Microphone monitoring started (for cough detection)")
        
        # Placeholder for audio analysis
        # Real implementation would process audio for:
        # - Cough detection
        # - Wheezing
        # - Breathing sounds
        pass
    
    async def get_current_vitals(self, patient_id: str) -> Dict:
        """Get most recent vital signs"""
        
        if not self.reading_buffer:
            return {}
        
        latest = self.reading_buffer[-1]
        
        # Calculate trends
        if len(self.reading_buffer) >= 60:
            old_hr = np.mean([r.heart_rate for r in list(self.reading_buffer)[:30] if r.heart_rate])
            new_hr = np.mean([r.heart_rate for r in list(self.reading_buffer)[-30:] if r.heart_rate])
            hr_trend = new_hr - old_hr
            
            old_hrv = np.mean([r.hrv_ms for r in list(self.reading_buffer)[:30] if r.hrv_ms])
            new_hrv = np.mean([r.hrv_ms for r in list(self.reading_buffer)[-30:] if r.hrv_ms])
            hrv_decrease = (new_hrv - old_hrv) / old_hrv if old_hrv > 0 else 0
        else:
            hr_trend = 0
            hrv_decrease = 0
        
        return {
            'heart_rate': latest.heart_rate,
            'hrv_ms': latest.hrv_ms,
            'spo2': latest.spo2,
            'respiratory_rate': latest.respiratory_rate,
            'hr_trend': hr_trend,
            'hrv_decrease': hrv_decrease,
            'timestamp': latest.timestamp
        }
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        print("⏸️ Monitoring stopped")


# WebSocket server to receive sensor data from frontend
class SensorWebSocketServer:
    """
    WebSocket server to receive real-time sensor data from phone
    
    Frontend sends:
    - PPG samples (30 Hz)
    - Accelerometer (10 Hz)
    - Audio features (10 Hz)
    - GPS location (1 Hz)
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.monitors: Dict[str, PhoneSensorMonitor] = {}
    
    async def start_server(self):
        """Start WebSocket server"""
        import websockets
        
        async def handler(websocket, path):
            """Handle incoming WebSocket connection"""
            
            # Get patient ID from initial message
            init_msg = await websocket.recv()
            import json
            data = json.loads(init_msg)
            patient_id = data['patient_id']
            
            # Create or get monitor
            if patient_id not in self.monitors:
                self.monitors[patient_id] = PhoneSensorMonitor(patient_id)
            
            monitor = self.monitors[patient_id]
            
            # Start monitoring
            await monitor.start_monitoring()
            
            # Receive sensor data
            async for message in websocket:
                data = json.loads(message)
                
                # Route to appropriate handler
                if data['type'] == 'ppg':
                    await self._handle_ppg(monitor, data)
                elif data['type'] == 'accelerometer':
                    await self._handle_accelerometer(monitor, data)
                elif data['type'] == 'audio':
                    await self._handle_audio(monitor, data)
                elif data['type'] == 'location':
                    await self._handle_location(monitor, data)
        
        async with websockets.serve(handler, self.host, self.port):
            print(f"📡 WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def _handle_ppg(self, monitor: PhoneSensorMonitor, data: Dict):
        """Handle PPG data from camera"""
        # Process and store
        pass
    
    async def _handle_accelerometer(self, monitor: PhoneSensorMonitor, data: Dict):
        """Handle accelerometer data"""
        pass
    
    async def _handle_audio(self, monitor: PhoneSensorMonitor, data: Dict):
        """Handle audio data from microphone"""
        pass
    
    async def _handle_location(self, monitor: PhoneSensorMonitor, data: Dict):
        """Handle GPS location"""
        pass


# Example usage
async def demo_phone_sensors():
    """Demo smartphone sensor monitoring"""
    
    monitor = PhoneSensorMonitor(patient_id="DEMO_001")
    
    print("\n📱 Starting smartphone sensor monitoring...")
    print("=" * 60)
    
    # Start monitoring (in background)
    monitor_task = asyncio.create_task(monitor.start_monitoring())
    
    # Simulate monitoring for 30 seconds
    for i in range(30):
        await asyncio.sleep(1)
        
        vitals = await monitor.get_current_vitals("DEMO_001")
        
        if vitals.get('heart_rate'):
            print(f"\rTime: {i+1}s | HR: {vitals['heart_rate']} bpm | "
                  f"HRV: {vitals.get('hrv_ms', 0):.1f} ms | "
                  f"SpO2: {vitals.get('spo2', 0):.1f}% | "
                  f"RR: {vitals.get('respiratory_rate', 0)}/min", end='')
    
    print("\n\n✅ Monitoring complete!")
    
    await monitor.stop_monitoring()
    monitor_task.cancel()

if __name__ == "__main__":
    asyncio.run(demo_phone_sensors())

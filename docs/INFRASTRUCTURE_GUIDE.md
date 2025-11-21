# 🚀 Infrastructure Setup Guide

## 📦 What's Included

This infrastructure provides:

1. **Real-Time Streaming**: Kafka for vital sign streams (1Hz)
2. **Caching**: Redis for session management and load balancing
3. **Time-Series DB**: InfluxDB for vital signs history
4. **Relational DB**: PostgreSQL for patient records
5. **Monitoring**: Prometheus + Grafana for system metrics
6. **Load Balancing**: Multiple agent instances with Redis coordination

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Docker & Docker Compose
brew install docker docker-compose  # macOS
# or
sudo apt install docker.io docker-compose  # Linux

# Verify installation
docker --version
docker-compose --version
```

### 2. Start Infrastructure

```bash
# Navigate to project root
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Verify Services

Open these URLs in your browser:

```
✅ Kafka UI:         http://localhost:8080
✅ Redis Commander:  http://localhost:8081
✅ PgAdmin:          http://localhost:8082
✅ InfluxDB:         http://localhost:8086
✅ Prometheus:       http://localhost:9090
✅ Grafana:          http://localhost:3000
✅ API Gateway:      http://localhost:8000
✅ WebSocket:        ws://localhost:8766
```

---

## 📊 Service Details

### Kafka (Port 9092, 9093)
**Purpose**: Real-time vital sign streaming

**Topics Created Automatically**:
- `vitals-{patient_id}` - Individual patient streams
- `alerts` - Critical alerts
- `predictions` - Predictive warnings

**Usage**:
```python
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(
    bootstrap_servers='localhost:9093'
)

await producer.send(
    'vitals-P12345',
    value={'hr': 85, 'spo2': 98, 'timestamp': time.time()}
)
```

### Redis (Port 6379)
**Purpose**: 
- Session storage
- Load balancer state
- Agent health tracking
- Real-time metrics

**Password**: `mimiq_redis_password`

**Usage**:
```python
import redis.asyncio as redis

r = await redis.from_url(
    'redis://:mimiq_redis_password@localhost:6379/0'
)

# Store agent load
await r.set('agent_load:cardio-1', 5, ex=60)
```

### InfluxDB (Port 8086)
**Purpose**: Store vital signs time-series

**Credentials**:
- Username: `admin`
- Password: `mimiq_admin_password`
- Org: `mimiq`
- Bucket: `vitals`
- Token: `mimiq_influxdb_token_12345`

**Usage**:
```python
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

client = InfluxDBClientAsync(
    url='http://localhost:8086',
    token='mimiq_influxdb_token_12345',
    org='mimiq'
)

# Write vital sign
write_api = client.write_api()
await write_api.write(
    bucket='vitals',
    record={
        'measurement': 'vitals',
        'tags': {'patient_id': 'P12345'},
        'fields': {'heart_rate': 85, 'spo2': 98},
        'time': datetime.utcnow()
    }
)
```

### PostgreSQL (Port 5432)
**Purpose**: Store patient records, diagnoses, reports

**Credentials**:
- Username: `mimiq`
- Password: `mimiq_db_password`
- Database: `mimiq_health`

**Schema**:
```sql
-- Patients
CREATE TABLE patients (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    age INTEGER,
    sex CHAR(1),
    medical_history JSONB
);

-- Diagnoses
CREATE TABLE diagnoses (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    diagnosis TEXT,
    confidence FLOAT,
    risk_level VARCHAR(50),
    created_at TIMESTAMP
);

-- Vital Signs (aggregated)
CREATE TABLE vital_summaries (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    date DATE,
    avg_hr FLOAT,
    min_spo2 FLOAT,
    anomaly_count INTEGER
);
```

---

## 🎯 How Real-Time Data Flows

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA FLOW                               │
│                                                             │
│  📱 Phone Sensors (Camera, Accel, Mic)                     │
│         │                                                   │
│         │ WebSocket (ws://localhost:8766)                  │
│         ▼                                                   │
│  🔌 WebSocket Server                                       │
│         │                                                   │
│         │ Publishes to Kafka                               │
│         ▼                                                   │
│  📨 Kafka Topic: vitals-{patient_id}                       │
│         │                                                   │
│         ├─────────────────┬──────────────────┐             │
│         │                 │                  │             │
│         ▼                 ▼                  ▼             │
│  💾 InfluxDB       🔍 Monitor         💬 Chatbot          │
│  (Storage)        (Anomaly Detection) (Prevention)         │
│                           │                                │
│                           ▼                                │
│                    🚨 Alert Engine                         │
│                     (If risk > 0.85)                       │
│                           │                                │
│                           ▼                                │
│                    📲 Push Notification                    │
│                    📞 Emergency Call                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Development Workflow

### Start Development Environment

```bash
# Start infrastructure
docker-compose up -d

# Start API server (local)
python -m uvicorn app:app --reload --port 8000

# Start WebSocket server (local)
python src/wearable/phone_sensors.py

# Start monitoring
python src/wearable/realtime_monitor.py
```

### Test Real-Time Pipeline

```python
# Test phone sensor → Kafka → InfluxDB pipeline

import asyncio
from src.wearable.phone_sensors import PhoneSensorMonitor

async def test_pipeline():
    monitor = PhoneSensorMonitor(patient_id="TEST_001")
    
    # Start monitoring
    await monitor.start_monitoring()
    
    # Check InfluxDB after 30 seconds
    await asyncio.sleep(30)
    
    # Query stored data
    from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
    
    client = InfluxDBClientAsync(
        url='http://localhost:8086',
        token='mimiq_influxdb_token_12345',
        org='mimiq'
    )
    
    query = '''
    from(bucket: "vitals")
        |> range(start: -1h)
        |> filter(fn: (r) => r["patient_id"] == "TEST_001")
    '''
    
    result = await client.query_api().query(query)
    
    for table in result:
        for record in table.records:
            print(f"Time: {record.get_time()}, HR: {record.get_value()}")

asyncio.run(test_pipeline())
```

---

## 📈 Monitoring Dashboards

### Grafana Setup

1. Open http://localhost:3000
2. Login: `admin` / `mimiq_grafana_password`
3. Add InfluxDB data source:
   - URL: `http://influxdb:8086`
   - Token: `mimiq_influxdb_token_12345`
   - Org: `mimiq`
   - Bucket: `vitals`

4. Import dashboards:
   - Vital Signs Timeline
   - Agent Load Distribution
   - Alert History
   - System Performance

---

## 🔧 Scaling

### Add More Agent Instances

```bash
# Add more cardiology agents
docker-compose up -d --scale cardio-agent-2=5

# Or edit docker-compose.yml:
services:
  cardio-agent:
    deploy:
      replicas: 5  # Scale to 5 instances
```

### Horizontal Scaling

```bash
# Add more orchestrator instances
docker-compose up -d --scale orchestrator=5
```

---

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAREFUL: deletes data)
docker-compose down -v

# View disk usage
docker system df

# Clean up unused images
docker system prune -a
```

---

## 🔐 Security Notes

**⚠️ CHANGE THESE PASSWORDS IN PRODUCTION:**

```bash
# Redis
REDIS_PASSWORD=mimiq_redis_password

# PostgreSQL
POSTGRES_PASSWORD=mimiq_db_password

# InfluxDB
INFLUXDB_ADMIN_PASSWORD=mimiq_admin_password
INFLUXDB_TOKEN=mimiq_influxdb_token_12345

# Grafana
GF_SECURITY_ADMIN_PASSWORD=mimiq_grafana_password
```

Use environment variables or secrets management (e.g., Docker Secrets, AWS Secrets Manager).

---

## 📞 Troubleshooting

### Kafka not starting
```bash
# Check Zookeeper first
docker logs mimiq-zookeeper

# Increase memory
docker-compose down
# Edit docker-compose.yml: Add KAFKA_HEAP_OPTS: "-Xmx512M"
docker-compose up -d
```

### InfluxDB connection refused
```bash
# Wait for initialization
docker logs mimiq-influxdb

# InfluxDB takes ~30 seconds on first start
```

### Redis connection error
```bash
# Check password
redis-cli -h localhost -p 6379
AUTH mimiq_redis_password
PING
```

---

## ✅ Health Checks

```bash
# Check all services
docker-compose ps

# Expected output:
# mimiq-kafka         Up      9092/tcp, 9093/tcp
# mimiq-redis         Up      6379/tcp
# mimiq-influxdb      Up      8086/tcp
# mimiq-postgres      Up      5432/tcp
# ...
```

---

## 🚀 Next Steps

1. ✅ Start infrastructure: `docker-compose up -d`
2. ✅ Test WebSocket: `python src/wearable/phone_sensors.py`
3. ✅ Test chatbot: `python src/chatbot/prevention_flow.py`
4. ✅ Test Health Twin: `python src/personalization/health_twin.py`
5. ✅ Build frontend with sensor integration
6. ✅ Deploy to cloud (AWS/GCP/Azure)

**Infrastructure is ready for production! 🎉**

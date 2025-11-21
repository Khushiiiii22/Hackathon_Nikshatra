# 🔑 LLM API Setup Guide - How MIMIQ Uses Multiple LLMs

## 📋 IMPORTANT: CURRENT STATUS

**⚠️ The current codebase is NOT using external LLM APIs yet!**

The existing agents (Cardiology, Gastro, Pulmonary, etc.) are using **rule-based logic** with medical scoring systems:
- HEART Score (cardiology)
- Wells Criteria (PE risk)
- Troponin trend analysis
- Clinical risk stratification

**The multi-LLM architecture I described is the RECOMMENDED UPGRADE PATH.**

---

## 🎯 Where API Keys Are Configured (Ready But Not Active)

### 1. Configuration File: `src/config.py`

```python
# Lines 22-25 in src/config.py
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
```

**What this means:**
- The code is looking for API keys in **environment variables**
- Currently defaults to empty strings `""`
- Ready to accept keys once you provide them

---

## 🔧 HOW TO ADD YOUR API KEYS (3 Methods)

### Method 1: Create `.env` File (RECOMMENDED)

1. **Create a `.env` file in the project root:**
   ```bash
   cd /Users/khushi22/Hackathon/Hackathon_Nikshatra
   touch .env
   ```

2. **Add your API keys to `.env`:**
   ```bash
   # OpenAI API Key (for GPT-4, GPT-3.5, embeddings)
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Anthropic API Key (for Claude 3 Opus)
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # LLM Provider (openai, anthropic, or local)
   LLM_PROVIDER=openai
   
   # Default model
   LLM_MODEL=gpt-4-turbo-preview
   ```

3. **Install python-dotenv to load .env automatically:**
   ```bash
   pip install python-dotenv
   ```

4. **Add to the top of `src/config.py`:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load .env file
   ```

### Method 2: Export Environment Variables (Temporary)

**For macOS/Linux (zsh/bash):**
```bash
export OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4-turbo-preview"

# Then run your Python script
python demo_realtime_prevention.py
```

**Note:** These environment variables only last for the current terminal session.

### Method 3: Set in Code (NOT RECOMMENDED - Security Risk)

**⚠️ WARNING: Never commit API keys to Git!**

If you absolutely must hardcode (for testing only):
```python
# src/config.py
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # DON'T DO THIS!
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # SECURITY RISK!
```

Then add `.env` to `.gitignore` immediately:
```bash
echo ".env" >> .gitignore
```

---

## 🔑 WHERE TO GET API KEYS

### OpenAI API Key (for GPT-4, GPT-3.5, embeddings)

1. **Go to:** https://platform.openai.com/api-keys
2. **Sign up/Login** to your OpenAI account
3. **Click:** "Create new secret key"
4. **Copy** the key (starts with `sk-proj-...`)
5. **Cost:** ~$0.03 per 1K tokens (GPT-4 Turbo)

**Free Credits:**
- New users get $5 in free credits (expires after 3 months)
- Enough for ~166,000 tokens of GPT-4 Turbo

### Anthropic API Key (for Claude 3 Opus)

1. **Go to:** https://console.anthropic.com/
2. **Sign up/Login** to your Anthropic account
3. **Navigate to:** Settings → API Keys
4. **Click:** "Create Key"
5. **Copy** the key (starts with `sk-ant-...`)
6. **Cost:** ~$0.015 per 1K tokens (Claude 3 Opus)

**Free Credits:**
- New users get $5 in free credits
- Enough for ~333,000 tokens of Claude 3 Opus

---

## 🤖 HOW EACH LLM WOULD BE USED (When Implemented)

### Current Architecture vs. LLM-Enhanced Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ CURRENT (Rule-Based)                                           │
├────────────────────────────────────────────────────────────────┤
│ Patient Data → Cardiology Agent → HEART Score → Diagnosis     │
│                                   (No LLM)                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ FUTURE (LLM-Enhanced)                                          │
├────────────────────────────────────────────────────────────────┤
│ Patient Data → Master LLM (GPT-4) → Routes to Specialists     │
│                                   ↓                             │
│                   ┌───────────────┴───────────────┐            │
│                   ↓                   ↓           ↓            │
│         Claude 3 Opus        GPT-3.5 Turbo   GPT-3.5 Turbo    │
│         (Cardiology)         (Gastro)        (Pulmonary)      │
│                   ↓                   ↓           ↓            │
│                   └───────────────┬───────────────┘            │
│                                   ↓                             │
│                        Master LLM (GPT-4)                      │
│                        Final Synthesis                         │
└────────────────────────────────────────────────────────────────┘
```

### 1. Master Orchestrator (GPT-4 Turbo)

**File:** `src/agents/llm_orchestrator.py` (to be created)

**Role:** "Attending Physician" - routes patients to specialists

**API Call:**
```python
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    temperature=0.1,  # Low temp for consistent routing
    messages=[
        {"role": "system", "content": "You are a medical triage system..."},
        {"role": "user", "content": f"Patient: {patient_data}. Which specialists?"}
    ]
)

specialist_list = response.choices[0].message.content
```

**Cost:** ~$0.01 per patient (100 tokens input, 50 tokens output)

### 2. Cardiology Specialist (Claude 3 Opus)

**File:** `src/agents/cardiology_llm.py` (to be created)

**Role:** Deep medical reasoning for cardiac diagnoses

**API Call:**
```python
from anthropic import Anthropic
client = Anthropic(api_key=ANTHROPIC_API_KEY)

response = client.messages.create(
    model="claude-3-opus-20240229",
    temperature=0.2,
    max_tokens=1024,
    messages=[
        {"role": "user", "content": f"""
You are a cardiologist analyzing this patient:
- Troponin: {troponin}
- EKG: {ekg_findings}
- Symptoms: {symptoms}

Provide differential diagnosis with confidence scores.
"""}
    ]
)

diagnosis = response.content[0].text
```

**Cost:** ~$0.02 per analysis (500 tokens input, 500 tokens output)

### 3. Other Specialists (GPT-3.5 Turbo)

**File:** `src/agents/specialist_llm.py` (to be created)

**Role:** Fast, cost-effective analysis for Gastro, Pulmonary, MSK

**API Call:**
```python
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    temperature=0.2,
    messages=[
        {"role": "system", "content": "You are a gastroenterology specialist..."},
        {"role": "user", "content": f"Analyze: {symptoms}"}
    ]
)

analysis = response.choices[0].message.content
```

**Cost:** ~$0.002 per analysis (200 tokens input, 200 tokens output)

### 4. Knowledge Retrieval (text-embedding-3-large)

**File:** `src/agents/knowledge.py` (enhanced version)

**Role:** Convert medical queries to embeddings for vector search

**API Call:**
```python
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Chest pain with elevated troponin"
)

embedding = response.data[0].embedding  # 3072-dim vector
# Use for ChromaDB similarity search
```

**Cost:** ~$0.0001 per query (very cheap)

### 5. Safety Monitor (GPT-4 Turbo)

**File:** `src/agents/safety_llm.py` (to be created)

**Role:** Critical decision validation (STEMI, PE, Sepsis)

**API Call:**
```python
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    temperature=0.0,  # ZERO temp for safety checks
    messages=[
        {"role": "system", "content": "You are a safety monitor. Flag CRITICAL conditions."},
        {"role": "user", "content": f"Diagnosis: {diagnosis}. Any CRITICAL alerts?"}
    ]
)

safety_alerts = response.choices[0].message.content
```

**Cost:** ~$0.01 per check

### 6. Final Synthesis (GPT-4 Turbo)

**File:** `src/agents/llm_orchestrator.py` (synthesis method)

**Role:** Combine all specialist opinions into final diagnosis

**API Call:**
```python
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    messages=[
        {"role": "system", "content": "You are an attending physician synthesizing opinions..."},
        {"role": "user", "content": f"""
Cardiology (Claude): {cardio_diagnosis}
Gastro (GPT-3.5): {gastro_diagnosis}
Pulmonary (GPT-3.5): {pulm_diagnosis}
Safety: {safety_alerts}

Final diagnosis and plan?
"""}
    ]
)

final_decision = response.choices[0].message.content
```

**Cost:** ~$0.02 per synthesis

---

## 💰 COST BREAKDOWN (Per Patient Analysis)

| LLM Component | Model | Cost per Use | When Used |
|--------------|-------|--------------|-----------|
| Master Orchestrator | GPT-4 Turbo | $0.01 | Every patient |
| Cardiology Specialist | Claude 3 Opus | $0.02 | Cardiac cases (~70%) |
| Gastro Specialist | GPT-3.5 Turbo | $0.002 | GI cases (~50%) |
| Pulmonary Specialist | GPT-3.5 Turbo | $0.002 | Resp cases (~30%) |
| Safety Monitor | GPT-4 Turbo | $0.01 | High-risk cases (~20%) |
| Knowledge Search | Embeddings | $0.0001 | Every patient |
| Final Synthesis | GPT-4 Turbo | $0.02 | Every patient |

**Average Cost per Patient:** ~$0.05 - $0.08

**For 1,000 patients:** ~$50 - $80

**With $5 free credits:** 62-100 patient analyses

---

## 🚀 QUICK START: Enable LLM APIs (Step-by-Step)

### Step 1: Get API Keys (5 minutes)

```bash
# 1. OpenAI: https://platform.openai.com/api-keys
#    Copy your key: sk-proj-xxxxxxxxxxxxx

# 2. Anthropic: https://console.anthropic.com/
#    Copy your key: sk-ant-xxxxxxxxxxxxx
```

### Step 2: Create `.env` File

```bash
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra

cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
EOF
```

### Step 3: Install Required Packages

```bash
pip install openai anthropic python-dotenv langchain chromadb
```

### Step 4: Update `src/config.py`

Add at the top:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 5: Test API Connection

```bash
python -c "
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello, are you working?'}]
)

print('✅ OpenAI API is working!')
print(response.choices[0].message.content)
"
```

Expected output:
```
✅ OpenAI API is working!
Yes, I'm working! How can I help you today?
```

### Step 6: Test Anthropic API

```bash
python -c "
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

response = client.messages.create(
    model='claude-3-opus-20240229',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Hello Claude!'}]
)

print('✅ Anthropic API is working!')
print(response.content[0].text)
"
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. Never Commit API Keys to Git

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*_credentials.json" >> .gitignore

# Verify
git status  # Should NOT show .env file
```

### 2. Use Environment Variables in Production

**For deployment (Docker, AWS, etc.):**
```yaml
# docker-compose.yml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

Then set on the server:
```bash
export OPENAI_API_KEY="sk-proj-xxxxx"
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
docker-compose up
```

### 3. Rotate Keys Regularly

- Generate new keys every 90 days
- Revoke old keys in platform dashboards
- Update `.env` file

### 4. Set Usage Limits

**OpenAI Dashboard:**
- Settings → Billing → Usage limits
- Set monthly limit: $10 (safety net)

**Anthropic Console:**
- Settings → Usage
- Set alerts at $5 spent

---

## 📊 MONITORING API USAGE

### OpenAI Usage Dashboard

```
https://platform.openai.com/usage
```

Shows:
- Tokens used per day
- Cost breakdown by model
- API call volume

### Anthropic Usage Dashboard

```
https://console.anthropic.com/settings/usage
```

Shows:
- Messages sent
- Tokens processed
- Cost per model

### In-Code Usage Tracking

Add to `src/config.py`:
```python
import functools

def track_llm_usage(func):
    """Decorator to track LLM API calls"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.info(f"LLM call to {func.__name__} took {duration:.2f}s")
        # Log to database or file
        
        return result
    return wrapper
```

---

## 🧪 TEST WITHOUT SPENDING MONEY (Local LLM Alternative)

If you don't want to use paid APIs yet, you can use local LLMs:

### Option 1: Ollama (Free, Local)

```bash
# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai

# Download medical model
ollama pull llama3.1:70b

# Update src/config.py
LLM_PROVIDER = "local"
LLM_MODEL = "llama3.1:70b"
```

**Pros:** Free, private, no API limits
**Cons:** Slower, less accurate than GPT-4/Claude

### Option 2: HuggingFace Inference API (Free Tier)

```python
from transformers import pipeline

# Free inference on HuggingFace servers
generator = pipeline('text-generation', model='meta-llama/Llama-2-7b-chat-hf')

response = generator("Patient has chest pain with elevated troponin...")
```

**Pros:** Free tier available
**Cons:** Rate limits, queue delays

---

## 📝 SUMMARY: Where API Keys Come From

| Question | Answer |
|----------|--------|
| **Where are keys stored?** | `.env` file or environment variables |
| **How does code access them?** | `os.getenv("OPENAI_API_KEY")` in `src/config.py` |
| **Where to get OpenAI key?** | https://platform.openai.com/api-keys |
| **Where to get Anthropic key?** | https://console.anthropic.com/ |
| **Do I need both?** | OpenAI only (minimum), both for full architecture |
| **Cost for testing?** | $5 free credits = 62-100 patient analyses |
| **Is it working now?** | NO - rule-based agents only, LLM integration needed |
| **How to activate?** | Follow Quick Start above + implement LLM agents |

---

## 🎯 NEXT STEPS

1. **Get API keys** (5 min) - OpenAI + Anthropic
2. **Create `.env` file** (2 min) - Add keys
3. **Install packages** (5 min) - `pip install openai anthropic python-dotenv`
4. **Test connection** (5 min) - Run test scripts above
5. **Implement LLM agents** (optional) - Use code from MOBILE_INTEGRATION_GUIDE.md

**Total time to get started: ~20 minutes**

---

## 🆘 TROUBLESHOOTING

### Error: "OpenAI API key not found"

```bash
# Check if .env is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"

# Should print your key, not 'None'
```

### Error: "Rate limit exceeded"

- You're using free tier (3 requests/min on GPT-4)
- Upgrade to paid tier or wait 1 minute

### Error: "Invalid API key"

- Key expired or revoked
- Generate new key in dashboard
- Update `.env` file

### Error: "Insufficient credits"

- Check usage dashboard
- Add payment method
- Free credits may have expired

---

**Ready to enable the LLM architecture? Follow the Quick Start above! 🚀**

# 📋 SAMPLE MEDICAL REPORTS FOR TESTING

Created: November 22, 2025

## 🎯 Purpose

These are realistic sample medical reports to test the MIMIQ platform's file upload and analysis features.

---

## 📁 Available Reports

### ✅ Normal Reports (Low Risk)

1. **`ecg_report_normal.txt`**
   - Normal ECG for 45-year-old male
   - Heart rate: 72 bpm
   - No abnormalities
   - **Risk Level: LOW**

2. **`blood_test_normal.txt`**
   - Complete blood panel for 35-year-old female
   - All parameters normal
   - Cholesterol, glucose, liver, kidney all good
   - **Risk Level: LOW**

3. **`chest_xray_normal.txt`**
   - Clear chest X-ray for 42-year-old male
   - No lung or heart issues
   - Routine check-up
   - **Risk Level: LOW**

---

### ⚠️ Abnormal Reports (Requires Attention)

4. **`ecg_report_abnormal.txt`**
   - Abnormal ECG for 62-year-old female
   - Sinus tachycardia (105 bpm)
   - ST-segment depression
   - **Possible myocardial ischemia**
   - **Risk Level: HIGH**
   - **URGENT cardiology consultation needed**

5. **`blood_test_diabetes.txt`**
   - Diabetes screening for 58-year-old male
   - Fasting glucose: 165 mg/dL (HIGH)
   - HbA1c: 7.8% (Diabetic range)
   - **Type 2 Diabetes confirmed**
   - Early kidney involvement
   - **Risk Level: MEDIUM-HIGH**
   - **Requires immediate treatment**

6. **`chest_xray_pneumonia.txt`**
   - Chest X-ray for 68-year-old female
   - Right lower lobe pneumonia
   - Pleural effusion
   - **Bacterial infection likely**
   - **Risk Level: HIGH**
   - **URGENT: Antibiotics needed**

---

## 🧪 How to Test

### Method 1: Upload via UI
```
1. Open http://localhost:5173
2. Click "Upload" in navigation
3. Drag any report file to the upload area
4. Watch the AI agents analyze
5. View results in Dashboard
```

### Method 2: Upload via API (Terminal)
```bash
# Test normal ECG
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@sample_reports/ecg_report_normal.txt" \
  -F "patient_id=test_patient_001"

# Test abnormal ECG (should detect HIGH risk)
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@sample_reports/ecg_report_abnormal.txt" \
  -F "patient_id=test_patient_002"

# Test diabetes report
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@sample_reports/blood_test_diabetes.txt" \
  -F "patient_id=test_patient_003"

# Test pneumonia X-ray
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@sample_reports/chest_xray_pneumonia.txt" \
  -F "patient_id=test_patient_004"
```

---

## 🤖 Expected AI Agent Responses

### For Normal Reports:
- **Safety Monitor:** ✅ No emergency detected
- **Cardiology Agent:** ✅ Normal cardiac function (for ECG/blood)
- **Pulmonary Agent:** ✅ No respiratory issues (for X-ray)
- **Triage Agent:** ESI Level 4-5 (Non-urgent)

### For Abnormal Reports:
- **Safety Monitor:** ⚠️ May flag as urgent
- **Cardiology Agent:** ⚠️ Ischemia detected (for abnormal ECG)
- **Gastro Agent:** May analyze diabetes impact
- **Triage Agent:** ESI Level 1-3 (Urgent/Emergent)

---

## 📊 Test Scenarios

### Scenario 1: Routine Check-up
**Files:** `ecg_report_normal.txt` + `blood_test_normal.txt`
**Expected:** All clear, low risk, no urgent action

### Scenario 2: Cardiac Emergency
**File:** `ecg_report_abnormal.txt`
**Expected:** 
- HIGH risk detected
- Cardiology agent activates
- Recommend ER visit
- ESI Level 2 (Emergent)

### Scenario 3: Chronic Disease
**File:** `blood_test_diabetes.txt`
**Expected:**
- Diabetes diagnosis confirmed
- Multiple specialists involved
- Treatment plan recommended
- ESI Level 3 (Urgent)

### Scenario 4: Acute Infection
**File:** `chest_xray_pneumonia.txt`
**Expected:**
- Pulmonary agent identifies infection
- Safety monitor flags severity
- Antibiotic recommendation
- ESI Level 2 (Emergent)

---

## 🎯 AI Agent Testing Checklist

Use these reports to verify each agent works:

- [ ] **Safety Monitor**: Detects emergencies in abnormal reports
- [ ] **Cardiology Agent**: Analyzes ECG reports correctly
- [ ] **Pulmonary Agent**: Identifies pneumonia in X-ray
- [ ] **Gastro Agent**: Notes diabetes impact on digestion
- [ ] **MSK Agent**: (Add joint pain report if needed)
- [ ] **Triage Agent**: Assigns correct ESI levels (1-5)

---

## 📝 Report Details

### What Each Contains:

**ECG Reports:**
- Heart rate, rhythm
- PR/QRS/QT intervals
- ST-segment analysis
- Axis deviation
- Arrhythmia detection

**Blood Test Reports:**
- Complete Blood Count (CBC)
- Lipid profile (cholesterol)
- Blood sugar (glucose, HbA1c)
- Liver function tests
- Kidney function tests
- Thyroid levels

**Chest X-Ray Reports:**
- Lung fields assessment
- Cardiac silhouette
- Mediastinum examination
- Bone/soft tissue check
- Infiltrates/effusions

---

## 🔍 Keywords AI Should Extract

### From ECG Reports:
- "tachycardia", "bradycardia"
- "ST-segment depression/elevation"
- "T-wave inversion"
- "ischemia", "infarction"
- "arrhythmia", "fibrillation"

### From Blood Tests:
- "diabetes", "hyperglycemia"
- "cholesterol", "triglycerides"
- "anemia", "low hemoglobin"
- "kidney disease", "elevated creatinine"
- "abnormal liver enzymes"

### From X-Rays:
- "pneumonia", "infiltrates"
- "consolidation", "opacity"
- "pleural effusion"
- "cardiomegaly"
- "fracture", "nodule"

---

## 🚨 Urgency Levels

The AI should classify:

| Report | Urgency | ESI Level |
|--------|---------|-----------|
| Normal ECG | Low | 5 |
| Normal Blood | Low | 5 |
| Normal X-ray | Low | 5 |
| Abnormal ECG | HIGH | 2 |
| Diabetes | Medium-High | 3 |
| Pneumonia | HIGH | 2 |

---

## 💡 Demo Tips

1. **Start with Normal:** Show AI correctly identifies healthy reports
2. **Then Abnormal:** Demonstrate emergency detection
3. **Compare Side-by-Side:** Upload normal + abnormal ECG
4. **Show Speed:** AI analyzes in ~30 seconds
5. **Highlight Specialists:** Each agent contributes unique insights

---

## 📞 Quick Test Command

```bash
# Test all 6 reports in sequence
cd /Users/khushi22/Hackathon/Hackathon_Nikshatra/sample_reports

for file in *.txt; do
  echo "Testing: $file"
  curl -X POST http://localhost:5000/api/analyze \
    -F "file=@$file" \
    -F "patient_id=test_$(date +%s)"
  echo ""
  sleep 2
done
```

---

## 🎉 Ready to Use!

These reports are production-ready for:
- ✅ Live demos
- ✅ Integration testing
- ✅ AI agent validation
- ✅ Hackathon presentations
- ✅ User acceptance testing

**Location:** `/Users/khushi22/Hackathon/Hackathon_Nikshatra/sample_reports/`

**Usage:** Just drag and drop into the MIMIQ UI or use curl commands above!

---

**Created:** November 22, 2025  
**Format:** Plain text (.txt)  
**Medical Accuracy:** Realistic sample data for demonstration purposes only

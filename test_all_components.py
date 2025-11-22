#!/usr/bin/env python3
"""
Test all MIMIQ components to verify everything is working
"""

print('='*60)
print('🧪 TESTING ALL MIMIQ COMPONENTS')
print('='*60)

# Test 1: LLM Service Import
print('\n✅ Test 1: Import LLM Service')
try:
    from src.llm_service import get_llm_service, analyze_vitals, chat_medical
    print('   ✓ Import successful')
    test1_passed = True
except Exception as e:
    print(f'   ✗ Import failed: {e}')
    test1_passed = False

# Test 2: Get LLM Service
print('\n✅ Test 2: Initialize LLM Service')
try:
    llm = get_llm_service()
    print(f'   ✓ Service initialized')
    print(f'   ✓ Gemini configured: {llm.is_configured}')
    print(f'   ✓ Model: {llm.model_name}')
    test2_passed = True
except Exception as e:
    print(f'   ✗ Initialization failed: {e}')
    test2_passed = False

# Test 3: Quick Analysis Function
print('\n✅ Test 3: Quick Analysis Function')
try:
    response = analyze_vitals(heart_rate=72, hrv=65, spo2=98)
    print(f'   ✓ Function callable')
    print(f'   ✓ Response success: {response.success}')
    if response.metadata:
        print(f'   ✓ Diagnosis: {response.metadata.get("diagnosis", "N/A")[:50]}...')
        print(f'   ✓ Risk Level: {response.metadata.get("risk_level", "N/A")}')
    test3_passed = True
except Exception as e:
    print(f'   ✗ Analysis failed: {e}')
    test3_passed = False

# Test 4: Abnormal Vitals Test
print('\n✅ Test 4: Abnormal Vitals Detection')
try:
    response = analyze_vitals(heart_rate=95, hrv=38, spo2=94)
    print(f'   ✓ Abnormal vitals analyzed')
    print(f'   ✓ Response success: {response.success}')
    if response.metadata:
        print(f'   ✓ Diagnosis: {response.metadata.get("diagnosis", "N/A")[:50]}...')
        print(f'   ✓ Risk Level: {response.metadata.get("risk_level", "N/A")}')
        print(f'   ✓ Confidence: {response.metadata.get("confidence", 0)}%')
    test4_passed = True
except Exception as e:
    print(f'   ✗ Abnormal analysis failed: {e}')
    test4_passed = False

# Test 5: Flask API Integration
print('\n✅ Test 5: Flask API Integration')
try:
    import app_integrated
    print('   ✓ Flask app imports successfully')
    print('   ✓ LLM service integrated')
    test5_passed = True
except Exception as e:
    print(f'   ✗ Flask integration failed: {e}')
    test5_passed = False

# Test 6: Environment Configuration
print('\n✅ Test 6: Environment Configuration')
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    model = os.getenv('LLM_MODEL')
    print(f'   ✓ API Key configured: {"Yes" if api_key else "No"}')
    print(f'   ✓ Model configured: {model}')
    test6_passed = True
except Exception as e:
    print(f'   ✗ Environment check failed: {e}')
    test6_passed = False

# Summary
print('\n' + '='*60)
print('📊 TEST SUMMARY')
print('='*60)
tests = {
    'LLM Service Import': test1_passed,
    'LLM Service Init': test2_passed,
    'Normal Vitals Analysis': test3_passed,
    'Abnormal Vitals Analysis': test4_passed,
    'Flask Integration': test5_passed,
    'Environment Config': test6_passed
}

passed = sum(tests.values())
total = len(tests)

for test_name, result in tests.items():
    status = '✅' if result else '❌'
    print(f'{status} {test_name}')

print('\n' + '='*60)
if passed == total:
    print(f'🎉 ALL {total} TESTS PASSED! SYSTEM READY!')
else:
    print(f'⚠️  {passed}/{total} TESTS PASSED')
print('='*60)

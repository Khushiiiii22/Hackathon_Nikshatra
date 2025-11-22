#!/usr/bin/env python3
"""
Complete System Check - Identify all issues and working components
"""

import os
import sys
from pathlib import Path

print('='*70)
print('🔍 COMPLETE SYSTEM CHECK - MIMIQ PROJECT')
print('='*70)

issues = []
working = []

# Check 1: Python Environment
print('\n📦 Check 1: Python Environment')
try:
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f'   ✓ Python version: {python_version}')
    if sys.version_info < (3, 8):
        issues.append('Python version too old (need 3.8+)')
    else:
        working.append('Python 3.8+ installed')
except Exception as e:
    issues.append(f'Python check failed: {e}')

# Check 2: Virtual Environment
print('\n🐍 Check 2: Virtual Environment')
venv_path = Path('.venv/bin/python')
if venv_path.exists():
    print(f'   ✓ Virtual environment found: .venv/')
    working.append('Virtual environment exists')
else:
    print(f'   ✗ Virtual environment missing')
    issues.append('No virtual environment at .venv/')

# Check 3: Required Files
print('\n📁 Check 3: Core Files')
required_files = {
    'src/llm_service.py': 'Centralized LLM Service',
    'app_integrated.py': 'Flask API',
    '.env': 'Environment configuration',
    'requirements.txt': 'Dependencies',
    'phone_monitor.html': 'Phone interface',
    'docs/GEMINI_COMPLETE.md': 'Documentation'
}

for file_path, description in required_files.items():
    if Path(file_path).exists():
        print(f'   ✓ {description}: {file_path}')
        working.append(f'{description} exists')
    else:
        print(f'   ✗ {description}: {file_path} MISSING')
        issues.append(f'Missing {description}: {file_path}')

# Check 4: Environment Variables
print('\n⚙️  Check 4: Environment Configuration')
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    llm_model = os.getenv('LLM_MODEL')
    
    if gemini_key:
        print(f'   ✓ GEMINI_API_KEY: Configured ({gemini_key[:20]}...)')
        working.append('Gemini API key configured')
    else:
        print(f'   ✗ GEMINI_API_KEY: Not found')
        issues.append('GEMINI_API_KEY not configured in .env')
    
    if llm_model:
        print(f'   ✓ LLM_MODEL: {llm_model}')
        working.append(f'LLM model set to {llm_model}')
    else:
        print(f'   ⚠️  LLM_MODEL: Using default')
        
except Exception as e:
    print(f'   ✗ Environment check failed: {e}')
    issues.append(f'Environment configuration error: {e}')

# Check 5: Python Dependencies
print('\n📚 Check 5: Python Packages')
required_packages = [
    'flask',
    'flask_cors',
    'google.generativeai',
    'loguru',
    'dotenv'
]

for package in required_packages:
    try:
        if package == 'dotenv':
            __import__('dotenv')
        else:
            __import__(package.replace('-', '_'))
        print(f'   ✓ {package}')
        working.append(f'{package} installed')
    except ImportError:
        print(f'   ✗ {package} NOT INSTALLED')
        issues.append(f'Missing package: {package}')

# Check 6: LLM Service
print('\n🤖 Check 6: LLM Service')
try:
    from src.llm_service import get_llm_service, analyze_vitals
    print('   ✓ LLM service imports successfully')
    working.append('LLM service importable')
    
    try:
        llm = get_llm_service()
        print(f'   ✓ LLM service initialized')
        print(f'   ✓ Gemini configured: {llm.is_configured}')
        print(f'   ✓ Model: {llm.model_name}')
        working.append('LLM service initialized')
        
        if llm.is_configured:
            working.append('Gemini API connected')
        else:
            issues.append('Gemini API not configured')
            
    except Exception as e:
        print(f'   ✗ LLM initialization failed: {e}')
        issues.append(f'LLM service initialization error: {e}')
        
except Exception as e:
    print(f'   ✗ LLM service import failed: {e}')
    issues.append(f'Cannot import LLM service: {e}')

# Check 7: Flask API
print('\n🌐 Check 7: Flask API')
try:
    import app_integrated
    print('   ✓ Flask app imports successfully')
    working.append('Flask API importable')
except Exception as e:
    print(f'   ✗ Flask import failed: {e}')
    issues.append(f'Flask API import error: {e}')

# Check 8: Flask Server Status
print('\n🚀 Check 8: Flask Server')
try:
    import subprocess
    result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
    if result.stdout.strip():
        print(f'   ✓ Flask server RUNNING on port 5000 (PID: {result.stdout.strip()})')
        working.append('Flask server is running')
    else:
        print(f'   ⚠️  Flask server NOT running')
        issues.append('Flask server not started - run: .venv/bin/python app_integrated.py')
except Exception as e:
    print(f'   ⚠️  Cannot check server status: {e}')

# Check 9: Documentation
print('\n📖 Check 9: Documentation')
doc_files = [
    'docs/GEMINI_COMPLETE.md',
    'docs/LLM_SETUP_COMPLETE.md',
    'docs/GEMINI_EVERYWHERE_DONE.md',
    'GEMINI_READY.md',
    'TEST_RESULTS_VERIFIED.md',
    'README_PHONE.md',
    'VISUAL_GUIDE.md'
]

doc_count = 0
for doc in doc_files:
    if Path(doc).exists():
        doc_count += 1

print(f'   ✓ {doc_count}/{len(doc_files)} documentation files present')
working.append(f'{doc_count} documentation files available')

# Check 10: Phone Interface
print('\n📱 Check 10: Phone Interface')
if Path('phone_monitor.html').exists():
    print('   ✓ phone_monitor.html exists')
    working.append('Phone interface available')
    if Path('phone_qr_code.png').exists():
        print('   ✓ QR code generated')
        working.append('QR code available')
    else:
        print('   ⚠️  QR code not generated (optional)')
else:
    print('   ✗ phone_monitor.html MISSING')
    issues.append('Phone interface file missing')

# Summary
print('\n' + '='*70)
print('📊 SYSTEM STATUS SUMMARY')
print('='*70)

print(f'\n✅ WORKING COMPONENTS ({len(working)}):')
for item in working[:10]:  # Show first 10
    print(f'   • {item}')
if len(working) > 10:
    print(f'   ... and {len(working) - 10} more')

if issues:
    print(f'\n⚠️  ISSUES FOUND ({len(issues)}):')
    for issue in issues:
        print(f'   • {issue}')
else:
    print(f'\n🎉 NO ISSUES FOUND!')

print('\n' + '='*70)
if len(issues) == 0:
    print('✅ SYSTEM STATUS: ALL SYSTEMS OPERATIONAL')
elif len(issues) <= 2:
    print('⚠️  SYSTEM STATUS: MOSTLY WORKING (MINOR ISSUES)')
else:
    print('❌ SYSTEM STATUS: NEEDS ATTENTION')
print('='*70)

# Exit code
sys.exit(len(issues))

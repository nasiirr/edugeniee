"""
Test script to verify environment configuration
Run this before deploying to ensure everything is set up correctly
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] python-dotenv loaded successfully")
except ImportError:
    print("[ERROR] python-dotenv not installed")
    sys.exit(1)

print("\nChecking Environment Variables...\n")

# Check Gemini API Key
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"[OK] GEMINI_API_KEY: {gemini_key[:20]}...")
else:
    print("[ERROR] GEMINI_API_KEY: Not found")

# Check Firebase Web Config
firebase_vars = [
    'FIREBASE_API_KEY',
    'FIREBASE_AUTH_DOMAIN',
    'FIREBASE_PROJECT_ID',
    'FIREBASE_STORAGE_BUCKET',
    'FIREBASE_MESSAGING_SENDER_ID',
    'FIREBASE_APP_ID',
    'FIREBASE_MEASUREMENT_ID'
]

firebase_ok = True
for var in firebase_vars:
    value = os.getenv(var)
    if value:
        print(f"[OK] {var}: {value[:30]}...")
    else:
        print(f"[ERROR] {var}: Not found")
        firebase_ok = False

# Check Firebase Admin credentials
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

print("\nFirebase Admin Credentials:")
if cred_path:
    if os.path.exists(cred_path):
        print(f"[OK] FIREBASE_CREDENTIALS_PATH: {cred_path}")
    else:
        print(f"[ERROR] FIREBASE_CREDENTIALS_PATH set but file not found: {cred_path}")
elif cred_json:
    print(f"[OK] FIREBASE_CREDENTIALS_JSON: Set (length: {len(cred_json)} chars)")
else:
    print("[WARNING] No Firebase Admin credentials found (optional for basic features)")
    print("   Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON for Firestore write access")

# Test imports
print("\nTesting Package Imports...\n")

try:
    import streamlit
    print(f"[OK] streamlit {streamlit.__version__}")
except ImportError:
    print("[ERROR] streamlit not installed")

try:
    import google.generativeai as genai
    print("[OK] google-generativeai imported")
    
    # Try to configure (will fail if API key is invalid)
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            print("[OK] Gemini API configured successfully")
        except Exception as e:
            print(f"[WARNING] Gemini API configuration warning: {e}")
except ImportError:
    print("[ERROR] google-generativeai not installed")

try:
    import firebase_admin
    print(f"[OK] firebase-admin imported")
except ImportError:
    print("[ERROR] firebase-admin not installed")

print("\n" + "="*50)
print("Configuration Check Complete!")
print("="*50)

if gemini_key and firebase_ok:
    print("\n[OK] All required environment variables are set!")
    print("   You're ready to run the app with: streamlit run app.py")
else:
    print("\n[WARNING] Some environment variables are missing.")
    print("   Please check .env file and ensure all required variables are set.")
    print("   See .env.example for reference.")

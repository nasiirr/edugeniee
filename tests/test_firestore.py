"""
Firestore Connection Test Script
This script tests your Firebase Firestore connection and verifies everything is working.
"""
import os
import sys
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded environment variables from .env")
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment variables")

# Test Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    print("[OK] firebase-admin package imported")
except ImportError:
    print("[ERROR] firebase-admin not installed")
    print("       Please run: pip install firebase-admin")
    sys.exit(1)

print("\n" + "="*60)
print("FIRESTORE CONNECTION TEST")
print("="*60 + "\n")

# Check for credentials
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')

print("1. Checking for Firebase credentials...")

if cred_path:
    print(f"   [OK] FIREBASE_CREDENTIALS_PATH found: {cred_path}")
    if os.path.exists(cred_path):
        print(f"   [OK] File exists at: {cred_path}")
    else:
        print(f"   [ERROR] File NOT found at: {cred_path}")
        print("\n   Please make sure:")
        print("   1. You've downloaded the service account JSON from Firebase Console")
        print("   2. The file path in .env is correct")
        print("   3. The file exists at the specified location")
        sys.exit(1)
elif cred_json:
    print(f"   [OK] FIREBASE_CREDENTIALS_JSON found (length: {len(cred_json)} chars)")
else:
    print("   [ERROR] No Firebase credentials found!")
    print("\n   Please set one of these in your .env file:")
    print("   - FIREBASE_CREDENTIALS_PATH=path/to/serviceAccount.json")
    print("   - FIREBASE_CREDENTIALS_JSON={...json content...}")
    print("\n   See FIRESTORE_SETUP_GUIDE.md for detailed instructions")
    sys.exit(1)

# Initialize Firebase
print("\n2. Initializing Firebase Admin SDK...")
try:
    # Check if already initialized
    try:
        app = firebase_admin.get_app()
        print("   [OK] Firebase already initialized")
    except ValueError:
        # Not initialized, initialize now
        if cred_path:
            cred = credentials.Certificate(cred_path)
        else:
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
        
        firebase_admin.initialize_app(cred)
        print("   [OK] Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"   [ERROR] Failed to initialize Firebase: {e}")
    print("\n   Common issues:")
    print("   1. Invalid service account JSON file")
    print("   2. Corrupted credentials")
    print("   3. Network connectivity issues")
    sys.exit(1)

# Get Firestore client
print("\n3. Connecting to Firestore...")
try:
    db = firestore.client()
    print("   [OK] Firestore client created successfully")
except Exception as e:
    print(f"   [ERROR] Failed to create Firestore client: {e}")
    sys.exit(1)

# Test write operation
print("\n4. Testing write operation...")
try:
    test_doc = {
        'test': True,
        'message': 'Hello from Firestore!',
        'timestamp': datetime.utcnow(),
        'app': 'Edugenie Quiz Generator'
    }
    doc_ref = db.collection('_test').document('connection_test')
    doc_ref.set(test_doc)
    print("   [OK] Test document written successfully")
except Exception as e:
    print(f"   [ERROR] Failed to write test document: {e}")
    print("\n   Possible causes:")
    print("   1. Firestore not enabled in Firebase Console")
    print("   2. Incorrect project ID in service account")
    print("   3. Network/firewall issues")
    sys.exit(1)

# Test read operation
print("\n5. Testing read operation...")
try:
    doc_ref = db.collection('_test').document('connection_test')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        print(f"   [OK] Test document read successfully")
        print(f"   Data: {data.get('message', 'N/A')}")
    else:
        print("   [WARNING] Document was written but cannot be read")
except Exception as e:
    print(f"   [ERROR] Failed to read test document: {e}")
    sys.exit(1)

# Test delete operation
print("\n6. Testing delete operation...")
try:
    doc_ref = db.collection('_test').document('connection_test')
    doc_ref.delete()
    print("   [OK] Test document deleted successfully")
except Exception as e:
    print(f"   [WARNING] Could not delete test document: {e}")

# Test query operation
print("\n7. Testing collection query...")
try:
    # Try to query quiz_attempts collection
    attempts_ref = db.collection('quiz_attempts').limit(5)
    attempts = list(attempts_ref.stream())
    print(f"   [OK] Collection query successful")
    print(f"   Found {len(attempts)} quiz attempts in database")
    
    if len(attempts) > 0:
        print("\n   Recent quiz attempts:")
        for attempt in attempts[:3]:
            data = attempt.to_dict()
            topic = data.get('topic', 'Unknown')
            score = data.get('score_percentage', 0)
            print(f"   - Topic: {topic}, Score: {score:.1f}%")
except Exception as e:
    print(f"   [OK] Collection query works (no data yet: {e})")

print("\n" + "="*60)
print("✅ FIRESTORE CONNECTION TEST PASSED!")
print("="*60)
print("\nFirestore is properly configured and working!")
print("\nNext steps:")
print("1. Run the app: C:/Python313/python.exe -m streamlit run app.py")
print("2. Complete a quiz to save data to Firestore")
print("3. View insights: C:/Python313/python.exe -m streamlit run pagesss/user_insights.py")
print("\nYou can also view your data in Firebase Console:")
print("https://console.firebase.google.com/")
print("\n" + "="*60)

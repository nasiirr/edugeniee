import json
import sys

"""
Firebase serviceAccount.json to Streamlit Secrets Converter
Run this script to convert your Firebase credentials to TOML format
"""

def convert_to_streamlit_secrets():
    try:
        # Read serviceAccount.json
        with open('serviceAccount.json', 'r') as f:
            firebase_creds = json.load(f)
        
        print("=" * 70)
        print("STREAMLIT CLOUD SECRETS CONFIGURATION")
        print("=" * 70)
        print()
        print("Copy everything below and paste into Streamlit Cloud secrets:")
        print()
        print("-" * 70)
        print()
        
        # Add placeholder for Gemini API key
        print('# Add your Gemini API Key here')
        print('GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"')
        print()
        
        # Firebase credentials
        print('# Firebase credentials from serviceAccount.json')
        print('[firebase_credentials]')
        
        for key, value in firebase_creds.items():
            if isinstance(value, str):
                # Special handling for private_key - escape newlines
                if key == 'private_key':
                    # Replace actual newlines with \\n for TOML
                    escaped_value = value.replace('\n', '\\n')
                    print(f'{key} = "{escaped_value}"')
                else:
                    print(f'{key} = "{value}"')
            elif isinstance(value, (int, float)):
                print(f'{key} = {value}')
            elif isinstance(value, bool):
                print(f'{key} = {str(value).lower()}')
            else:
                print(f'{key} = "{value}"')
        
        print()
        print("-" * 70)
        print()
        print("✅ Conversion complete!")
        print()
        print("NEXT STEPS:")
        print("1. Copy the entire output above (excluding this message)")
        print("2. Go to Streamlit Cloud → App Settings → Secrets")
        print("3. Paste the configuration")
        print("4. Replace YOUR_GEMINI_API_KEY_HERE with your actual API key")
        print("5. Click 'Save'")
        print()
        print("=" * 70)
        
    except FileNotFoundError:
        print("❌ ERROR: serviceAccount.json not found!")
        print()
        print("Make sure you have 'serviceAccount.json' in the same directory")
        print("as this script.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid JSON in serviceAccount.json")
        print()
        print("Please check that your serviceAccount.json is valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    convert_to_streamlit_secrets()

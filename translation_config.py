#!/usr/bin/env python3
"""
Translation API configuration
"""

import os
from pathlib import Path

# Translation API Keys (set as environment variables or in config file)
GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY')
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')

# Config file path
CONFIG_FILE = Path(__file__).parent / "translation_keys.txt"

def load_api_keys():
    """Load API keys from config file or environment variables"""
    keys = {
        'google': GOOGLE_TRANSLATE_API_KEY,
        'deepl': DEEPL_API_KEY
    }
    
    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip().strip('"\'')
                        
                        if key == 'google_api_key':
                            keys['google'] = value
                        elif key == 'deepl_api_key':
                            keys['deepl'] = value
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    return keys

def create_config_template():
    """Create template config file"""
    if not CONFIG_FILE.exists():
        template = """# Translation API Keys Configuration
# Remove the # to uncomment and add your keys

# Google Cloud Translation API Key
# google_api_key=YOUR_GOOGLE_API_KEY_HERE

# DeepL API Key  
# deepl_api_key=YOUR_DEEPL_API_KEY_HERE

# How to get API Keys:
# 
# Google Cloud Translation API:
# 1. Go to https://cloud.google.com/translate
# 2. Create a project and enable Translation API
# 3. Create credentials (API Key)
# 4. Uncomment the line above and paste your key
#
# DeepL API:
# 1. Go to https://www.deepl.com/pro-api
# 2. Sign up for free tier (500,000 characters/month)
# 3. Get your API key from account settings
# 4. Uncomment the line above and paste your key
"""
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"Created config template: {CONFIG_FILE}")
        except Exception as e:
            print(f"Error creating config template: {e}")

if __name__ == "__main__":
    # Create config template if it doesn't exist
    create_config_template()
    
    # Test loading keys
    keys = load_api_keys()
    print("Current API key status:")
    print(f"Google API Key: {'✓ Set' if keys['google'] else '✗ Not set'}")
    print(f"DeepL API Key: {'✓ Set' if keys['deepl'] else '✗ Not set'}")
    
    if not any(keys.values()):
        print(f"\nTo add API keys, edit: {CONFIG_FILE}")
        print("Or set environment variables: GOOGLE_TRANSLATE_API_KEY, DEEPL_API_KEY")
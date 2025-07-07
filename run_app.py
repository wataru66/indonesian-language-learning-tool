#!/usr/bin/env python3
"""
Application launcher for Indonesian Language Learning Application
アプリケーション起動スクリプト
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import flet
        print("✓ Flet is installed")
    except ImportError:
        print("✗ Flet is not installed. Please run: pip install flet")
        return False
    
    return True

def main():
    """Main launcher"""
    print("Indonesian Language Learning Application v1.0")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install required dependencies and try again.")
        return 1
    
    print("\nStarting application...")
    
    try:
        # Import and run main application
        from main import main as app_main
        import flet as ft
        
        # Launch the Flet app
        ft.app(target=app_main, assets_dir="assets")
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        return 0
    except Exception as e:
        print(f"\nError starting application: {e}")
        print("\nFor troubleshooting, please check:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. Python version is 3.9 or higher")
        print("3. Display server is available (for GUI applications)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
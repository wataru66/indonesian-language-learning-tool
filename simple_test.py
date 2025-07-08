#!/usr/bin/env python3
"""
Simple test to verify core functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        import flet as ft
        print("✓ Flet import: OK")
    except Exception as e:
        print(f"✗ Flet import error: {e}")
        return False
    
    try:
        from config.settings import Settings
        print("✓ Settings import: OK")
    except Exception as e:
        print(f"✗ Settings import error: {e}")
        return False
    
    try:
        from data.database import Database
        print("✓ Database import: OK")
    except Exception as e:
        print(f"✗ Database import error: {e}")
        return False
    
    try:
        from ui.main_window import MainWindow
        print("✓ MainWindow import: OK")
    except Exception as e:
        print(f"✗ MainWindow import error: {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from data.database import Database
        db = Database()
        db.initialize()
        print("✓ Database initialization: OK")
        return True
    except Exception as e:
        print(f"✗ Database initialization error: {e}")
        return False

def test_settings():
    """Test settings initialization"""
    print("\nTesting settings...")
    
    try:
        from config.settings import Settings
        settings = Settings()
        print("✓ Settings initialization: OK")
        return True
    except Exception as e:
        print(f"✗ Settings initialization error: {e}")
        return False

def test_ui_components():
    """Test UI component imports"""
    print("\nTesting UI components...")
    
    components = [
        'ui.file_tab',
        'ui.flashcard_view', 
        'ui.test_view',
        'ui.progress_view',
        'ui.settings_view',
        'ui.tutorial_view',
        'ui.help_view'
    ]
    
    for component in components:
        try:
            __import__(component)
            print(f"✓ {component}: OK")
        except Exception as e:
            print(f"✗ {component}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("Indonesian Language Learning Tool - Component Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database, 
        test_settings,
        test_ui_components
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("python3 main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
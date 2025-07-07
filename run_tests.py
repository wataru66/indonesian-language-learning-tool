#!/usr/bin/env python3
"""
Test runner for Indonesian Language Learning Application
統合テストとファイル整合性チェック
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports work correctly"""
    print("=== Import Tests ===")
    
    try:
        # Core imports
        print("Testing core imports...")
        from core.analyzer import IndonesianAnalyzer
        from core.file_processor import FileProcessor
        from core.flashcard import FlashcardManager
        from core.test_engine import TestEngine
        from core.priority_manager import PriorityManager
        print("✓ Core imports successful")
        
        # Data imports
        print("Testing data imports...")
        from data.database import Database
        from data.models import Word, Phrase, LearningProgress
        from data.patterns import PhrasePatterns
        print("✓ Data imports successful")
        
        # Config imports
        print("Testing config imports...")
        from config.settings import Settings
        print("✓ Config imports successful")
        
        # Utils imports
        print("Testing utils imports...")
        from utils.export import DataExporter
        print("✓ Utils imports successful")
        
        # UI imports (may require display, so catch errors)
        print("Testing UI imports...")
        try:
            import flet as ft
            from ui.main_window import MainWindow
            from ui.tutorial_view import TutorialView
            from ui.help_view import HelpView
            from ui.file_tab import FileTab
            from ui.flashcard_view import FlashcardView
            from ui.test_view import TestView
            from ui.progress_view import ProgressView
            from ui.priority_list_view import PriorityListView
            from ui.settings_view import SettingsView
            print("✓ UI imports successful")
        except Exception as e:
            print(f"⚠ UI imports failed (expected in headless environment): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_core_functionality():
    """Test core functionality"""
    print("\n=== Core Functionality Tests ===")
    
    try:
        # Test Indonesian Analyzer
        print("Testing Indonesian Analyzer...")
        from core.analyzer import IndonesianAnalyzer
        analyzer = IndonesianAnalyzer()
        
        # Test stemming
        test_words = ["makan", "memakan", "berkerja", "mengerjakan"]
        for word in test_words:
            stem = analyzer.stem(word)
            print(f"  {word} -> {stem}")
        
        # Test text analysis
        test_text = "Saya makan nasi. Dia berkerja di kantor."
        results = analyzer.analyze_text(test_text)
        print(f"  Analysis results: {len(results['unique_words'])} unique words")
        print("✓ Indonesian Analyzer working")
        
        # Test File Processor
        print("Testing File Processor...")
        from core.file_processor import FileProcessor
        processor = FileProcessor()
        extensions = processor.get_supported_extensions()
        print(f"  Supported extensions: {extensions}")
        print("✓ File Processor working")
        
        # Test Database
        print("Testing Database...")
        from data.database import Database
        db = Database("test.db")
        db.initialize()
        print("✓ Database initialization working")
        
        # Clean up test database
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")
            
        return True
        
    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        return False

def test_file_structure():
    """Test project file structure"""
    print("\n=== File Structure Tests ===")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "ui/__init__.py",
        "ui/main_window.py",
        "ui/tutorial_view.py",
        "ui/help_view.py",
        "ui/file_tab.py",
        "ui/flashcard_view.py",
        "ui/test_view.py",
        "ui/progress_view.py",
        "ui/priority_list_view.py",
        "ui/settings_view.py",
        "core/__init__.py",
        "core/analyzer.py",
        "core/file_processor.py",
        "core/flashcard.py",
        "core/test_engine.py",
        "core/priority_manager.py",
        "data/__init__.py",
        "data/database.py",
        "data/models.py",
        "data/patterns.py",
        "config/__init__.py",
        "config/settings.py",
        "utils/__init__.py",
        "utils/export.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def test_requirements():
    """Test requirements.txt"""
    print("\n=== Requirements Tests ===")
    
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        required_packages = ["flet", "sqlite3"]
        for package in required_packages:
            if package in requirements.lower():
                print(f"✓ {package} in requirements")
            else:
                print(f"⚠ {package} not found in requirements")
        
        return True
        
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Indonesian Language Learning Application - Integration Tests")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_requirements,
        test_imports,
        test_core_functionality
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Application is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
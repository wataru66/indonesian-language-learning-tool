#!/usr/bin/env python3
"""
Debug version of main.py to identify UI issues
"""

import sys
import os
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def debug_main(page: ft.Page):
    """Debug version of main application"""
    try:
        print("Starting debug main...")
        
        # Configure page
        page.title = "インドネシア語学習支援ツール v1.0 (Debug)"
        page.window_width = 1200
        page.window_height = 800
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        print("Page configured successfully")
        
        # Test basic UI
        page.add(ft.Text("デバッグモード: 基本UI表示成功", size=20))
        page.update()
        
        print("Basic UI added")
        
        # Try to import modules step by step
        try:
            from config.settings import Settings
            print("Settings import: OK")
            settings = Settings()
            print("Settings initialized: OK")
        except Exception as e:
            print(f"Settings error: {e}")
            page.add(ft.Text(f"Settings error: {e}", color="red"))
            page.update()
            return
        
        try:
            from data.database import Database
            print("Database import: OK")
            db = Database()
            db.initialize()
            print("Database initialized: OK")
        except Exception as e:
            print(f"Database error: {e}")
            page.add(ft.Text(f"Database error: {e}", color="red"))
            page.update()
            return
        
        try:
            from ui.main_window import MainWindow
            print("MainWindow import: OK")
            
            # Create main window
            main_window = MainWindow(page, db, settings)
            print("MainWindow created: OK")
            
            page.add(main_window)
            print("MainWindow added to page: OK")
            
        except Exception as e:
            print(f"MainWindow error: {e}")
            import traceback
            traceback.print_exc()
            page.add(ft.Text(f"MainWindow error: {e}", color="red"))
            page.update()
            return
        
        print("Debug main completed successfully")
        
    except Exception as e:
        print(f"Fatal error in debug_main: {e}")
        import traceback
        traceback.print_exc()
        page.add(ft.Text(f"Fatal error: {e}", color="red"))
        page.update()

if __name__ == "__main__":
    print("Starting debug application...")
    ft.app(target=debug_main, assets_dir="assets")
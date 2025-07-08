#!/usr/bin/env python3
"""
Main application without tutorial
"""

import sys
import os
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from data.database import Database
from config.settings import Settings


def main(page: ft.Page):
    """Main application entry point without tutorial"""
    try:
        print("Initializing application...")
        
        # Configure page
        page.title = "インドネシア語学習支援ツール v1.0"
        page.window_width = 1200
        page.window_height = 800
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        print("Page configured")
        
        # Initialize settings
        settings = Settings()
        print("Settings initialized")
        
        # Initialize database
        db = Database()
        db.initialize()
        print("Database initialized")
        
        # Create main window but force skip tutorial
        main_window = MainWindow(page, db, settings)
        main_window.is_first_run = False  # Force skip tutorial
        print("MainWindow created (tutorial skipped)")
        
        page.add(main_window)
        print("MainWindow added to page")
        
        # Handle window resize
        def on_resize(e):
            try:
                main_window.on_resize(page.width, page.height)
            except Exception as resize_error:
                print(f"Resize error: {resize_error}")
        
        page.on_resize = on_resize
        page.update()
        print("Application initialization completed")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error in UI
        error_text = ft.Text(
            f"アプリケーション初期化エラー: {str(e)}",
            size=16,
            color="red"
        )
        page.add(ft.Container(
            content=error_text,
            padding=20
        ))
        page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
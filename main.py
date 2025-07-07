#!/usr/bin/env python3
"""
Indonesian Language Learning Support Application
Main entry point
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
    """Main application entry point"""
    # Configure page
    page.title = "インドネシア語学習支援ツール v1.0"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Initialize settings
    settings = Settings()
    
    # Initialize database
    db = Database()
    db.initialize()
    
    # Create and display main window
    main_window = MainWindow(page, db, settings)
    page.add(main_window)
    
    # Handle window resize
    def on_resize(e):
        main_window.on_resize(page.width, page.height)
    
    page.on_resize = on_resize
    page.update()


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
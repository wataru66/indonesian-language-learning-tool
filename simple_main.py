#!/usr/bin/env python3
"""
Simplified main.py for debugging
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.database import Database
from config.settings import Settings

def simple_main(page: ft.Page):
    """Simplified main function with minimal UI"""
    try:
        print("Starting simple main...")
        
        # Configure page
        page.title = "インドネシア語学習支援ツール v1.0 (簡易版)"
        page.window_width = 1200
        page.window_height = 800
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        
        print("Page configured")
        
        # Initialize settings
        settings = Settings()
        print("Settings initialized")
        
        # Initialize database
        db = Database()
        db.initialize()
        print("Database initialized")
        
        # Create simple UI
        content = ft.Column([
            ft.Text(
                "インドネシア語学習支援ツール v1.0",
                size=24,
                weight=ft.FontWeight.BOLD
            ),
            ft.Divider(),
            ft.Text("アプリケーションが正常に起動しました", size=16),
            ft.Text("データベース接続: 成功", size=14, color="green"),
            ft.Text("設定読み込み: 成功", size=14, color="green"),
            ft.ElevatedButton(
                "メイン画面に切り替え",
                on_click=lambda e: switch_to_main(page, db, settings)
            )
        ])
        
        page.add(content)
        page.update()
        print("Simple UI added successfully")
        
    except Exception as e:
        print(f"Error in simple_main: {e}")
        import traceback
        traceback.print_exc()
        
        error_content = ft.Column([
            ft.Text("エラーが発生しました", size=20, color="red"),
            ft.Text(str(e), size=14),
            ft.Text("詳細はターミナルを確認してください", size=12)
        ])
        page.add(error_content)
        page.update()

def switch_to_main(page: ft.Page, db: Database, settings: Settings):
    """Switch to the full main window"""
    try:
        print("Switching to main window...")
        page.clean()
        
        from ui.main_window import MainWindow
        main_window = MainWindow(page, db, settings)
        page.add(main_window)
        page.update()
        print("Main window loaded successfully")
        
    except Exception as e:
        print(f"Error switching to main: {e}")
        import traceback
        traceback.print_exc()
        
        error_content = ft.Column([
            ft.Text("メイン画面の読み込みでエラーが発生しました", size=16, color="red"),
            ft.Text(str(e), size=12),
            ft.ElevatedButton(
                "簡易版に戻る",
                on_click=lambda _: simple_main(page)
            )
        ])
        page.add(error_content)
        page.update()

if __name__ == "__main__":
    print("Starting simplified application...")
    ft.app(target=simple_main, assets_dir="assets")
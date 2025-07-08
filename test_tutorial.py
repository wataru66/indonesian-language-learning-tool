#!/usr/bin/env python3
"""
Test tutorial dialog
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_tutorial(page: ft.Page):
    """Test tutorial dialog with simple content"""
    page.title = "チュートリアルテスト"
    page.window_width = 800
    page.window_height = 600
    
    def show_simple_dialog(e):
        """Show simple dialog"""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("簡単なテスト"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("これは簡単なテストダイアログです", size=16),
                    ft.Text("正常に表示されていますか？", size=14),
                    ft.Container(
                        width=200,
                        height=100,
                        bgcolor=ft.colors.BLUE_100,
                        content=ft.Text("テストコンテンツ"),
                        alignment=ft.alignment.center
                    )
                ]),
                width=300,
                height=200,
                padding=20
            ),
            actions=[
                ft.TextButton("閉じる", on_click=lambda e: close_dialog())
            ]
        )
        
        def close_dialog():
            dialog.open = False
            page.update()
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def show_tutorial_dialog(e):
        """Show actual tutorial dialog"""
        try:
            from ui.tutorial_view import TutorialView
            from config.settings import Settings
            
            settings = Settings()
            tutorial = TutorialView(page, settings)
            tutorial.show()
            
        except Exception as err:
            # Show error dialog
            error_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("エラー"),
                content=ft.Text(f"チュートリアル表示エラー: {err}"),
                actions=[ft.TextButton("OK", on_click=lambda e: close_error())]
            )
            
            def close_error():
                error_dialog.open = False
                page.update()
            
            page.dialog = error_dialog
            error_dialog.open = True
            page.update()
    
    # Main content
    page.add(
        ft.Column([
            ft.Text("チュートリアルテスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.ElevatedButton(
                "簡単なダイアログをテスト",
                on_click=show_simple_dialog
            ),
            ft.ElevatedButton(
                "実際のチュートリアルをテスト",
                on_click=show_tutorial_dialog
            )
        ], spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=test_tutorial)
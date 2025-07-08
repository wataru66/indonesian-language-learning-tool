#!/usr/bin/env python3
"""
Debug UI interactions
"""

import flet as ft

def debug_ui(page: ft.Page):
    """Test basic UI interactions"""
    page.title = "UIインタラクションテスト"
    page.window_width = 600
    page.window_height = 500
    
    click_count = 0
    status_text = ft.Text("ボタンをクリックしてください", size=16)
    
    def on_button_click(e):
        nonlocal click_count
        click_count += 1
        status_text.value = f"ボタンが {click_count} 回クリックされました"
        print(f"Button clicked {click_count} times")
        page.update()
    
    def on_elevated_button_click(e):
        nonlocal click_count
        click_count += 1
        status_text.value = f"ElevatedButton が {click_count} 回クリックされました"
        print(f"ElevatedButton clicked {click_count} times")
        page.update()
    
    def test_file_picker(e):
        print("File picker test clicked")
        status_text.value = "ファイルピッカーテスト実行中..."
        page.update()
        
        def on_files_selected(result):
            print(f"Files selected: {result}")
            if result and result.files:
                status_text.value = f"選択されたファイル数: {len(result.files)}"
            else:
                status_text.value = "ファイルが選択されませんでした"
            page.update()
        
        file_picker = ft.FilePicker(on_result=on_files_selected)
        page.overlay.append(file_picker)
        page.update()
        
        file_picker.pick_files(
            dialog_title="テストファイル選択",
            allow_multiple=True
        )
    
    # Test different button types
    page.add(
        ft.Column([
            ft.Text("UIインタラクションテスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            status_text,
            ft.Container(height=20),
            
            # Basic button
            ft.TextButton(
                "基本ボタン",
                on_click=on_button_click
            ),
            
            # Elevated button
            ft.ElevatedButton(
                "立体ボタン",
                on_click=on_elevated_button_click
            ),
            
            # Button with icon
            ft.ElevatedButton(
                "アイコン付きボタン",
                icon=ft.icons.STAR,
                on_click=on_elevated_button_click
            ),
            
            # File picker test
            ft.ElevatedButton(
                "ファイルピッカーテスト",
                icon=ft.icons.UPLOAD_FILE,
                on_click=test_file_picker
            ),
            
            # Row of buttons
            ft.Row([
                ft.ElevatedButton("ボタン1", on_click=on_button_click),
                ft.ElevatedButton("ボタン2", on_click=on_button_click),
                ft.ElevatedButton("ボタン3", on_click=on_button_click),
            ], spacing=10),
            
        ], spacing=15)
    )

if __name__ == "__main__":
    ft.app(target=debug_ui)
#!/usr/bin/env python3
"""
Test file picker functionality
"""

import flet as ft

def test_file_picker(page: ft.Page):
    """Test file picker with simple UI"""
    page.title = "ファイルピッカーテスト"
    page.window_width = 600
    page.window_height = 400
    
    selected_files = []
    file_list_view = ft.ListView(height=200)
    
    def on_files_selected(result):
        print(f"File picker result: {result}")
        if result and result.files:
            print(f"Selected files: {[f.name for f in result.files]}")
            selected_files.clear()
            file_list_view.controls.clear()
            
            for file in result.files:
                selected_files.append(file)
                file_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(file.name),
                        subtitle=ft.Text(file.path)
                    )
                )
            page.update()
        else:
            print("No files selected")
    
    def test_simple_file_picker(e):
        print("Opening simple file picker...")
        file_picker = ft.FilePicker(on_result=on_files_selected)
        page.overlay.append(file_picker)
        page.update()
        
        file_picker.pick_files(
            dialog_title="ファイルを選択してください",
            allow_multiple=True,
            allowed_extensions=["txt", "xlsx", "docx", "pdf"]
        )
    
    def test_with_sample_data(e):
        print("Testing with sample data...")
        # Simulate file selection with sample data
        class MockFile:
            def __init__(self, name, path):
                self.name = name
                self.path = path
        
        class MockResult:
            def __init__(self, files):
                self.files = files
        
        sample_files = [
            MockFile("basic_daily_conversation.txt", 
                    "/Users/nakanishiwataru/Developer/Project/LearningIndonesia/indonesian_analyzer/sample_data/basic_daily_conversation.txt"),
            MockFile("business_manufacturing_terms.txt",
                    "/Users/nakanishiwataru/Developer/Project/LearningIndonesia/indonesian_analyzer/sample_data/business_manufacturing_terms.txt")
        ]
        
        mock_result = MockResult(sample_files)
        on_files_selected(mock_result)
    
    # UI
    page.add(
        ft.Column([
            ft.Text("ファイルピッカーテスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Row([
                ft.ElevatedButton(
                    "ファイル選択テスト",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=test_simple_file_picker
                ),
                ft.ElevatedButton(
                    "サンプルデータテスト",
                    icon=ft.icons.FOLDER,
                    on_click=test_with_sample_data
                )
            ], spacing=10),
            
            ft.Text("選択されたファイル:", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=file_list_view,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                padding=10
            )
        ], spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=test_file_picker)
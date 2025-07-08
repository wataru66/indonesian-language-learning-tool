#!/usr/bin/env python3
"""
Fixed main application with working UI structure
"""

import sys
import os
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.database import Database
from config.settings import Settings
from core.analyzer import IndonesianAnalyzer

def main_fixed(page: ft.Page):
    """Fixed main application with tabbed interface that works"""
    page.title = "インドネシア語学習支援ツール v1.0"
    page.window_width = 1200
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Initialize components
    settings = Settings()
    db = Database()
    db.initialize()
    analyzer = IndonesianAnalyzer()
    
    print("Application initialized successfully")
    
    # State variables
    selected_files = []
    
    # Create working file tab content
    def create_file_tab_content():
        """Create working file processing tab"""
        file_list_view = ft.ListView(height=150, spacing=5)
        status_text = ft.Text("準備完了", size=14)
        results_text = ft.Text("", size=12)
        
        analyze_button = ft.ElevatedButton(
            "分析実行",
            icon=ft.icons.ANALYTICS,
            disabled=True,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
            height=50
        )
        
        def update_file_list():
            """Update file list display"""
            file_list_view.controls.clear()
            
            for i, file_info in enumerate(selected_files):
                file_item = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.INSERT_DRIVE_FILE, size=20),
                        ft.Text(file_info['name'], expand=True),
                        ft.Text(f"{file_info['size']} bytes", size=12),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            on_click=lambda e, idx=i: remove_file(idx),
                            icon_size=16
                        )
                    ]),
                    padding=5,
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=5
                )
                file_list_view.controls.append(file_item)
            
            analyze_button.disabled = len(selected_files) == 0
            page.update()
        
        def remove_file(index):
            """Remove file from list"""
            if 0 <= index < len(selected_files):
                selected_files.pop(index)
                update_file_list()
        
        def load_sample_data(e):
            """Load sample data files"""
            print("Loading sample data...")
            status_text.value = "サンプルデータを読み込み中..."
            page.update()
            
            try:
                sample_dir = Path(__file__).parent / "sample_data"
                sample_files = list(sample_dir.glob("*.txt"))
                
                selected_files.clear()
                for file_path in sample_files:
                    selected_files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size
                    })
                
                update_file_list()
                status_text.value = f"{len(sample_files)} 個のサンプルファイルを読み込みました"
                print(f"Loaded {len(sample_files)} sample files")
                
            except Exception as ex:
                print(f"Sample loading error: {ex}")
                status_text.value = f"エラー: {str(ex)}"
                page.update()
        
        def select_files(e):
            """Select files using file picker"""
            print("Opening file picker...")
            status_text.value = "ファイル選択中..."
            page.update()
            
            def on_files_selected(result):
                print(f"File picker result: {result}")
                if result and result.files:
                    for file in result.files:
                        selected_files.append({
                            'path': file.path,
                            'name': file.name,
                            'size': file.size if hasattr(file, 'size') else 0
                        })
                    update_file_list()
                    status_text.value = f"{len(result.files)} 個のファイルを選択しました"
                else:
                    status_text.value = "ファイルが選択されませんでした"
                page.update()
            
            file_picker = ft.FilePicker(on_result=on_files_selected)
            page.overlay.append(file_picker)
            page.update()
            
            file_picker.pick_files(
                dialog_title="インドネシア語ファイルを選択",
                allow_multiple=True,
                allowed_extensions=["txt", "xlsx", "docx", "pdf"]
            )
        
        def clear_files(e):
            """Clear all files"""
            print("Clearing files...")
            selected_files.clear()
            update_file_list()
            status_text.value = "ファイルをクリアしました"
            results_text.value = ""
            page.update()
        
        def analyze_files(e):
            """Analyze selected files"""
            if not selected_files:
                return
            
            print(f"Starting analysis of {len(selected_files)} files...")
            status_text.value = "分析実行中..."
            results_text.value = "分析中..."
            page.update()
            
            try:
                all_text = ""
                for file_data in selected_files:
                    with open(file_data['path'], 'r', encoding='utf-8') as f:
                        all_text += f.read() + "\n"
                
                # Analyze text
                analysis_results = analyzer.analyze_text(all_text)
                
                # Format results
                result_output = f"""分析完了！

統計情報:
総単語数: {analysis_results['total_words']:,}
ユニーク単語数: {analysis_results['unique_words']:,}
語幹数: {analysis_results['unique_stems']:,}

頻出語幹 TOP 10:
"""
                
                for i, (stem, count) in enumerate(analysis_results['top_stems'][:10]):
                    result_output += f"{i+1}. {stem} ({count}回)\n"
                
                results_text.value = result_output
                status_text.value = "分析完了！"
                
            except Exception as error:
                print(f"Analysis error: {error}")
                results_text.value = f"分析エラー: {str(error)}"
                status_text.value = "分析エラーが発生しました"
            
            page.update()
        
        # Set button event
        analyze_button.on_click = analyze_files
        
        # Create file tab content
        return ft.Container(
            content=ft.Column([
                # File Selection
                ft.Container(
                    content=ft.Column([
                        ft.Text("ファイル選択", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton(
                                "ファイル選択",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=select_files,
                                height=40
                            ),
                            ft.ElevatedButton(
                                "サンプルデータ",
                                icon=ft.icons.FOLDER_SPECIAL,
                                on_click=load_sample_data,
                                height=40,
                                bgcolor=ft.colors.GREEN,
                                color=ft.colors.WHITE
                            ),
                            ft.ElevatedButton(
                                "クリア",
                                icon=ft.icons.CLEAR,
                                on_click=clear_files,
                                height=40,
                                bgcolor=ft.colors.RED,
                                color=ft.colors.WHITE
                            )
                        ], spacing=10),
                        ft.Container(height=10),
                        ft.Text("選択されたファイル:", size=14),
                        ft.Container(
                            content=file_list_view,
                            border=ft.border.all(1, ft.colors.GREY_300),
                            border_radius=5,
                            padding=5
                        )
                    ]),
                    padding=ft.padding.all(15),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10
                ),
                
                ft.Container(height=15),
                
                # Analysis Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("分析実行", size=18, weight=ft.FontWeight.BOLD),
                        status_text,
                        ft.Container(height=10),
                        analyze_button
                    ]),
                    padding=ft.padding.all(15),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10
                ),
                
                ft.Container(height=15),
                
                # Results Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("分析結果", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=results_text,
                            height=200,
                            border=ft.border.all(1, ft.colors.GREY_300),
                            border_radius=5,
                            padding=10
                        )
                    ]),
                    padding=ft.padding.all(15),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(10)
        )
    
    def create_placeholder_tab(title):
        """Create placeholder tab content"""
        return ft.Container(
            content=ft.Column([
                ft.Text(f"{title}機能", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("この機能は開発中です", size=16),
                ft.Text("ファイル処理タブで基本的な分析機能をお試しください", size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=50
        )
    
    # Create app bar
    app_bar = ft.AppBar(
        title=ft.Text("インドネシア語学習支援ツール v1.0"),
        center_title=True,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE
    )
    
    # Create tabs with working content
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="ファイル処理",
                icon=ft.icons.FOLDER_OPEN,
                content=create_file_tab_content()
            ),
            ft.Tab(
                text="学習リスト",
                icon=ft.icons.LIST,
                content=create_placeholder_tab("学習リスト")
            ),
            ft.Tab(
                text="フラッシュカード",
                icon=ft.icons.STYLE,
                content=create_placeholder_tab("フラッシュカード")
            ),
            ft.Tab(
                text="テスト",
                icon=ft.icons.QUIZ,
                content=create_placeholder_tab("テスト")
            ),
            ft.Tab(
                text="進捗管理",
                icon=ft.icons.ANALYTICS,
                content=create_placeholder_tab("進捗管理")
            )
        ]
    )
    
    # Create main layout
    main_layout = ft.Column(
        [
            app_bar,
            ft.Container(
                content=tabs,
                expand=True,
                padding=ft.padding.all(0)
            )
        ],
        spacing=0
    )
    
    page.add(main_layout)
    page.update()
    print("Fixed main application loaded successfully")

if __name__ == "__main__":
    ft.app(target=main_fixed, assets_dir="assets")
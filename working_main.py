#!/usr/bin/env python3
"""
Working version with simplified UI
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.database import Database
from config.settings import Settings
from core.analyzer import IndonesianAnalyzer

def working_main(page: ft.Page):
    """Working main with simplified single-page UI"""
    page.title = "インドネシア語学習支援ツール v1.0 (動作版)"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Initialize components
    settings = Settings()
    db = Database()
    db.initialize()
    analyzer = IndonesianAnalyzer()
    
    print("Application initialized successfully")
    
    # State variables
    selected_files = []
    
    # UI Components
    file_list_view = ft.ListView(height=150, spacing=5)
    
    status_text = ft.Text("準備完了", size=14)
    
    analyze_button = ft.ElevatedButton(
        "分析実行",
        icon=ft.icons.ANALYTICS,
        disabled=True,
        bgcolor=ft.colors.BLUE,
        color=ft.colors.WHITE,
        height=50
    )
    
    results_text = ft.Text("", size=12)
    
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
        results_text.value = "分析中...\n処理には少し時間がかかる場合があります。"
        page.update()
        
        try:
            all_text = ""
            file_info = []
            
            for file_data in selected_files:
                file_path = Path(file_data['path'])
                print(f"Processing: {file_path.name}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    all_text += text + "\n"
                    file_info.append(f"{file_path.name}: {len(text)} 文字")
            
            print(f"Total text length: {len(all_text)}")
            
            # Analyze text
            analysis_results = analyzer.analyze_text(all_text)
            
            print("Analysis completed")
            
            # Format results
            result_output = f"""🎉 分析完了！

📊 統計情報:
総文字数: {len(all_text):,}
総単語数: {analysis_results['total_words']:,}
ユニーク単語数: {analysis_results['unique_words']:,}
語幹数: {analysis_results['unique_stems']:,}
語幹抽出率: {(analysis_results['unique_stems']/analysis_results['unique_words']*100):.1f}%

📁 処理ファイル:
{chr(10).join(file_info)}

🔥 頻出語幹 TOP 15:
"""
            
            for i, (stem, count) in enumerate(analysis_results['top_stems'][:15]):
                result_output += f"{i+1:2d}. {stem:<15} ({count:3d}回)\n"
            
            result_output += f"\n🔤 頻出単語 TOP 10:\n"
            for i, (word, count) in enumerate(analysis_results['top_words'][:10]):
                result_output += f"{i+1:2d}. {word:<20} ({count:3d}回)\n"
            
            results_text.value = result_output
            status_text.value = "分析完了！"
            
            # Save to database (basic implementation)
            print("Saving results to database...")
            # Here you could save the results to the database
            
        except Exception as error:
            print(f"Analysis error: {error}")
            import traceback
            traceback.print_exc()
            results_text.value = f"❌ 分析エラー:\n{str(error)}"
            status_text.value = "分析エラーが発生しました"
        
        page.update()
    
    # Set up button events
    analyze_button.on_click = analyze_files
    
    # Create UI
    page.add(
        ft.Column([
            # Header
            ft.Container(
                content=ft.Column([
                    ft.Text("🇮🇩 インドネシア語学習支援ツール", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("Indonesian Language Learning Tool v1.0", size=16, color=ft.colors.GREY_600),
                    ft.Text("テキストファイル分析・語幹抽出・学習データ生成", size=14, color=ft.colors.GREY_700),
                ]),
                padding=ft.padding.only(bottom=20)
            ),
            
            ft.Divider(),
            
            # File Selection Section
            ft.Container(
                content=ft.Column([
                    ft.Text("📁 ファイル選択", size=20, weight=ft.FontWeight.BOLD),
                    
                    ft.Row([
                        ft.ElevatedButton(
                            "ファイル選択",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=select_files,
                            height=45,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "サンプルデータ使用",
                            icon=ft.icons.FOLDER_SPECIAL,
                            on_click=load_sample_data,
                            height=45,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN,
                                color=ft.colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "クリア",
                            icon=ft.icons.CLEAR,
                            on_click=clear_files,
                            height=45,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED,
                                color=ft.colors.WHITE
                            )
                        )
                    ], spacing=15),
                    
                    ft.Container(height=10),
                    ft.Text("選択されたファイル:", size=16, weight=ft.FontWeight.BOLD),
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
                    ft.Text("⚡ 分析実行", size=20, weight=ft.FontWeight.BOLD),
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
                    ft.Text("📊 分析結果", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            results_text
                        ], scroll=ft.ScrollMode.AUTO),
                        height=300,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5,
                        padding=10
                    )
                ]),
                padding=ft.padding.all(15),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10
            )
        ], spacing=0)
    )

if __name__ == "__main__":
    ft.app(target=working_main)
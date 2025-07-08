#!/usr/bin/env python3
"""
Quick fix version with simplified file processing
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.database import Database
from config.settings import Settings
from core.analyzer import IndonesianAnalyzer

def quick_fix_main(page: ft.Page):
    """Quick fix version with working file processing"""
    page.title = "インドネシア語学習支援ツール v1.0 (修正版)"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    
    # Initialize components
    settings = Settings()
    db = Database()
    db.initialize()
    analyzer = IndonesianAnalyzer()
    
    # UI components
    file_path_text = ft.Text("ファイルが選択されていません", size=14)
    analyze_button = ft.ElevatedButton("分析実行", disabled=True)
    results_text = ft.Text("", size=12)
    
    selected_file_path = None
    
    def on_file_selected(result):
        nonlocal selected_file_path
        print(f"File picker result: {result}")
        
        if result and result.files and len(result.files) > 0:
            selected_file = result.files[0]
            selected_file_path = selected_file.path
            file_path_text.value = f"選択ファイル: {selected_file.name}"
            analyze_button.disabled = False
            print(f"Selected file: {selected_file_path}")
        else:
            selected_file_path = None
            file_path_text.value = "ファイルが選択されていません"
            analyze_button.disabled = True
            print("No file selected")
        
        page.update()
    
    def select_file(e):
        print("Opening file picker...")
        file_picker = ft.FilePicker(on_result=on_file_selected)
        page.overlay.append(file_picker)
        page.update()
        
        file_picker.pick_files(
            dialog_title="インドネシア語テキストファイルを選択",
            allow_multiple=False,
            allowed_extensions=["txt"]
        )
    
    def use_sample_file(e):
        nonlocal selected_file_path
        sample_path = Path(__file__).parent / "sample_data" / "basic_daily_conversation.txt"
        if sample_path.exists():
            selected_file_path = str(sample_path)
            file_path_text.value = f"サンプルファイル: {sample_path.name}"
            analyze_button.disabled = False
            print(f"Using sample file: {selected_file_path}")
        else:
            file_path_text.value = "サンプルファイルが見つかりません"
            analyze_button.disabled = True
            print(f"Sample file not found: {sample_path}")
        
        page.update()
    
    def analyze_file(e):
        if not selected_file_path:
            return
        
        try:
            print(f"Starting analysis of: {selected_file_path}")
            results_text.value = "分析中..."
            page.update()
            
            # Read file
            with open(selected_file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            print(f"File read successfully, length: {len(text)}")
            
            # Analyze
            analysis_results = analyzer.analyze_text(text)
            
            print(f"Analysis completed")
            print(f"Total words: {analysis_results['total_words']}")
            print(f"Unique words: {analysis_results['unique_words']}")
            print(f"Unique stems: {analysis_results['unique_stems']}")
            
            # Display results
            result_text = f"""分析完了！

総単語数: {analysis_results['total_words']}
ユニーク単語数: {analysis_results['unique_words']}  
語幹数: {analysis_results['unique_stems']}

頻出語幹 (上位10個):
"""
            
            for i, (stem, count) in enumerate(analysis_results['top_stems'][:10]):
                result_text += f"{i+1}. {stem} ({count}回)\n"
            
            results_text.value = result_text
            
        except Exception as error:
            print(f"Analysis error: {error}")
            import traceback
            traceback.print_exc()
            results_text.value = f"分析エラー: {str(error)}"
        
        page.update()
    
    analyze_button.on_click = analyze_file
    
    # UI Layout
    page.add(
        ft.Column([
            ft.Text("インドネシア語学習支援ツール", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("テキストファイル分析機能", size=16, color=ft.colors.GREY_700),
            ft.Divider(),
            
            # File selection
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("ファイル選択", size=18, weight=ft.FontWeight.BOLD),
                        file_path_text,
                        ft.Row([
                            ft.ElevatedButton(
                                "ファイル選択",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=select_file
                            ),
                            ft.ElevatedButton(
                                "サンプルファイル使用",
                                icon=ft.icons.FOLDER,
                                on_click=use_sample_file
                            )
                        ], spacing=10),
                    ], spacing=10),
                    padding=20
                )
            ),
            
            # Analysis
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("分析実行", size=18, weight=ft.FontWeight.BOLD),
                        analyze_button
                    ], spacing=10),
                    padding=20
                )
            ),
            
            # Results
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("分析結果", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=results_text,
                            height=300,
                            border=ft.border.all(1, ft.colors.GREY_300),
                            border_radius=5,
                            padding=10
                        )
                    ], spacing=10),
                    padding=20
                )
            )
        ], spacing=20)
    )

if __name__ == "__main__":
    ft.app(target=quick_fix_main)
#!/usr/bin/env python3
"""
Minimal working app to verify basic functionality
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.analyzer import IndonesianAnalyzer

def minimal_app(page: ft.Page):
    """Minimal working app"""
    page.title = "インドネシア語分析ツール (最小版)"
    page.window_width = 800
    page.window_height = 600
    page.padding = 20
    
    analyzer = IndonesianAnalyzer()
    
    # UI elements
    status_text = ft.Text("準備完了", size=16)
    results_container = ft.Container(
        content=ft.Text("結果がここに表示されます", size=12),
        height=300,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=5,
        padding=10
    )
    
    def test_sample_1(e):
        print("Sample 1 button clicked")
        status_text.value = "サンプル1を分析中..."
        page.update()
        
        try:
            sample_path = Path(__file__).parent / "sample_data" / "basic_daily_conversation.txt"
            with open(sample_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            results = analyzer.analyze_text(text)
            
            result_text = f"""サンプル1分析完了

ファイル: {sample_path.name}
文字数: {len(text)}
総単語数: {results['total_words']}
ユニーク単語: {results['unique_words']}
語幹数: {results['unique_stems']}

頻出語幹:
"""
            for i, (stem, count) in enumerate(results['top_stems'][:5]):
                result_text += f"{i+1}. {stem} ({count}回)\n"
            
            results_container.content = ft.Text(result_text, size=12)
            status_text.value = "分析完了"
            
        except Exception as error:
            print(f"Error: {error}")
            results_container.content = ft.Text(f"エラー: {error}", size=12, color="red")
            status_text.value = "エラーが発生しました"
        
        page.update()
    
    def test_sample_2(e):
        print("Sample 2 button clicked")
        status_text.value = "サンプル2を分析中..."
        page.update()
        
        try:
            sample_path = Path(__file__).parent / "sample_data" / "business_manufacturing_terms.txt"
            with open(sample_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            results = analyzer.analyze_text(text)
            
            result_text = f"""サンプル2分析完了

ファイル: {sample_path.name}
文字数: {len(text)}
総単語数: {results['total_words']}
ユニーク単語: {results['unique_words']}
語幹数: {results['unique_stems']}

頻出語幹:
"""
            for i, (stem, count) in enumerate(results['top_stems'][:5]):
                result_text += f"{i+1}. {stem} ({count}回)\n"
            
            results_container.content = ft.Text(result_text, size=12)
            status_text.value = "分析完了"
            
        except Exception as error:
            print(f"Error: {error}")
            results_container.content = ft.Text(f"エラー: {error}", size=12, color="red")
            status_text.value = "エラーが発生しました"
        
        page.update()
    
    def clear_results(e):
        print("Clear button clicked")
        results_container.content = ft.Text("結果がクリアされました", size=12)
        status_text.value = "クリア完了"
        page.update()
    
    # Layout
    page.add(
        ft.Column([
            # Header
            ft.Text("インドネシア語分析ツール", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("最小動作確認版", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            
            # Status
            status_text,
            ft.Container(height=10),
            
            # Buttons
            ft.Row([
                ft.ElevatedButton(
                    "サンプル1分析",
                    icon=ft.icons.ANALYTICS,
                    on_click=test_sample_1,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "サンプル2分析", 
                    icon=ft.icons.BUSINESS,
                    on_click=test_sample_2,
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "クリア",
                    icon=ft.icons.CLEAR,
                    on_click=clear_results,
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE
                )
            ], spacing=15),
            
            ft.Container(height=20),
            
            # Results
            ft.Text("分析結果:", size=16, weight=ft.FontWeight.BOLD),
            results_container
            
        ], spacing=10)
    )

if __name__ == "__main__":
    ft.app(target=minimal_app)
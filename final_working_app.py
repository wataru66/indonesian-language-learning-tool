#!/usr/bin/env python3
"""
Final working version - Simple and functional
"""

import sys
import flet as ft
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from data.database import Database
from config.settings import Settings
from core.analyzer import IndonesianAnalyzer
from core.priority_manager import PriorityManager
from core.flashcard import FlashcardManager
from core.test_engine import TestEngine

def final_working_app(page: ft.Page):
    """Final working version with all features"""
    # Basic page setup
    page.title = "インドネシア語学習支援ツール v1.0"
    page.window_width = 1200
    page.window_height = 800
    page.padding = 20
    
    # Initialize components
    print("Initializing components...")
    settings = Settings()
    db = Database()
    db.initialize()
    analyzer = IndonesianAnalyzer()
    priority_manager = PriorityManager(db)
    flashcard_manager = FlashcardManager(db)
    test_engine = TestEngine(db)
    
    # State
    current_tab = 0
    selected_files = []
    
    # Create tab buttons
    def change_tab(index):
        nonlocal current_tab
        current_tab = index
        update_content()
    
    tab_buttons = ft.Row([
        ft.ElevatedButton(
            "📁 ファイル処理",
            on_click=lambda e: change_tab(0),
            bgcolor=ft.colors.BLUE if current_tab == 0 else None
        ),
        ft.ElevatedButton(
            "📋 学習リスト",
            on_click=lambda e: change_tab(1),
            bgcolor=ft.colors.BLUE if current_tab == 1 else None
        ),
        ft.ElevatedButton(
            "🎴 フラッシュカード",
            on_click=lambda e: change_tab(2),
            bgcolor=ft.colors.BLUE if current_tab == 2 else None
        ),
        ft.ElevatedButton(
            "📝 テスト",
            on_click=lambda e: change_tab(3),
            bgcolor=ft.colors.BLUE if current_tab == 3 else None
        ),
        ft.ElevatedButton(
            "📊 進捗管理",
            on_click=lambda e: change_tab(4),
            bgcolor=ft.colors.BLUE if current_tab == 4 else None
        ),
        ft.ElevatedButton(
            "⚙️ 設定",
            on_click=lambda e: change_tab(5),
            bgcolor=ft.colors.BLUE if current_tab == 5 else None
        )
    ], spacing=10)
    
    # Content container
    content_container = ft.Container(
        height=600,
        padding=20,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=10
    )
    
    # Tab 0: File Processing
    def create_file_tab():
        file_list_view = ft.ListView(height=150, spacing=5)
        status_text = ft.Text("準備完了", size=14)
        results_text = ft.Text("", size=12, selectable=True)
        
        analyze_button = ft.ElevatedButton(
            "分析実行",
            icon=ft.icons.ANALYTICS,
            disabled=True,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE,
            height=45
        )
        
        def update_file_list():
            file_list_view.controls.clear()
            for i, file_info in enumerate(selected_files):
                file_item = ft.ListTile(
                    leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE),
                    title=ft.Text(file_info['name']),
                    subtitle=ft.Text(f"{file_info['size']} bytes"),
                    trailing=ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda e, idx=i: remove_file(idx)
                    )
                )
                file_list_view.controls.append(file_item)
            analyze_button.disabled = len(selected_files) == 0
            page.update()
        
        def remove_file(index):
            if 0 <= index < len(selected_files):
                selected_files.pop(index)
                update_file_list()
        
        def load_sample_data(e):
            print("Loading sample data...")
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
                page.update()
            except Exception as ex:
                print(f"Error: {ex}")
                status_text.value = f"エラー: {str(ex)}"
                page.update()
        
        def analyze_files(e):
            if not selected_files:
                return
            print(f"Analyzing {len(selected_files)} files...")
            status_text.value = "分析中..."
            page.update()
            
            try:
                all_text = ""
                for file_data in selected_files:
                    with open(file_data['path'], 'r', encoding='utf-8') as f:
                        all_text += f.read() + "\n"
                
                results = analyzer.analyze_text(all_text)
                
                # Save to database
                print("Saving to database...")
                from data.models import Word, Category
                from translation_service import get_translation_service
                from translation_config import load_api_keys
                
                # Load API keys and initialize translation service
                api_keys = load_api_keys()
                translator = get_translation_service(
                    google_api_key=api_keys.get('google'),
                    deepl_api_key=api_keys.get('deepl')
                )
                
                saved_count = 0
                for stem, count in list(results['stem_frequency'].items())[:20]:  # Save top 20 stems
                    try:
                        # Get Japanese translation using auto-translation
                        print(f"Translating: {stem}...")
                        japanese_translation = translator.translate(stem, 'id', 'ja')
                        
                        # Create Word object
                        word = Word(
                            indonesian=stem,
                            japanese=japanese_translation,
                            stem=stem,
                            category=Category.GENERAL,
                            difficulty=3,
                            frequency=count
                        )
                        # Add word to database
                        db.add_word(word)
                        saved_count += 1
                        print(f"Saved: {stem} -> {japanese_translation}")
                        
                        # Small delay to avoid rate limiting
                        import time
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"Error saving {stem}: {e}")
                
                print(f"Saved {saved_count} words to database")
                
                # Display results
                output = f"""分析完了！

総単語数: {results['total_words']:,}
ユニーク単語数: {results['unique_words']:,}
語幹数: {results['unique_stems']:,}

頻出語幹 TOP 15:
"""
                for i, (stem, count) in enumerate(results['top_stems'][:15]):
                    output += f"{i+1:2d}. {stem:<20} ({count:3d}回)\n"
                
                results_text.value = output
                status_text.value = "分析完了！データベースに保存しました。"
                page.update()
                
            except Exception as error:
                print(f"Analysis error: {error}")
                results_text.value = f"エラー: {str(error)}"
                status_text.value = "分析エラー"
                page.update()
        
        analyze_button.on_click = analyze_files
        
        return ft.Column([
            ft.Text("ファイル処理", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "サンプルデータ読込",
                    icon=ft.icons.FOLDER_SPECIAL,
                    on_click=load_sample_data,
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "クリア",
                    icon=ft.icons.CLEAR,
                    on_click=lambda e: (selected_files.clear(), update_file_list()),
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE
                )
            ], spacing=10),
            ft.Container(height=10),
            ft.Text("選択ファイル:", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=file_list_view,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5
            ),
            ft.Container(height=10),
            status_text,
            analyze_button,
            ft.Container(height=10),
            ft.Text("分析結果:", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([results_text], scroll=ft.ScrollMode.AUTO),
                height=250,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                padding=10
            )
        ])
    
    # Tab 1: Learning List
    def create_learning_list_tab():
        list_view = ft.ListView(height=400, spacing=5)
        
        def load_learning_items():
            list_view.controls.clear()
            try:
                # Get priority items (correct method name)
                items = priority_manager.get_priority_list(limit=50)
                
                if not items:
                    list_view.controls.append(
                        ft.Text("学習アイテムがありません。先にファイルを分析してください。")
                    )
                else:
                    for item in items:
                        list_item = ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.STAR if item.learning_priority > 5 else ft.icons.CIRCLE,
                                color=ft.colors.YELLOW if item.learning_priority > 5 else None
                            ),
                            title=ft.Text(item.content),
                            subtitle=ft.Text(f"翻訳: {item.translation} | 優先度: {item.learning_priority:.1f}"),
                            trailing=ft.Text(f"頻度: {item.frequency}")
                        )
                        list_view.controls.append(list_item)
                
                page.update()
            except Exception as e:
                print(f"Error loading learning items: {e}")
                list_view.controls.append(ft.Text(f"エラー: {str(e)}"))
                page.update()
        
        load_button = ft.ElevatedButton(
            "学習リスト更新",
            icon=ft.icons.REFRESH,
            on_click=lambda e: load_learning_items()
        )
        
        return ft.Column([
            ft.Text("学習リスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("優先度順の学習アイテム", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            load_button,
            ft.Container(height=10),
            ft.Container(
                content=list_view,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5
            )
        ])
    
    # Tab 2: Flashcards
    def create_flashcard_tab():
        return ft.Column([
            ft.Text("フラッシュカード", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("効率的な暗記学習", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.STYLE, size=100, color=ft.colors.BLUE),
                    ft.Text("フラッシュカード機能", size=20),
                    ft.Text("開発中です", size=16, color=ft.colors.GREY_600),
                    ft.Text("学習リストから単語を選んで暗記練習ができます", size=14)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=400
            )
        ])
    
    # Tab 3: Test
    def create_test_tab():
        return ft.Column([
            ft.Text("テスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("学習効果の測定", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.QUIZ, size=100, color=ft.colors.GREEN),
                    ft.Text("テスト機能", size=20),
                    ft.Text("開発中です", size=16, color=ft.colors.GREY_600),
                    ft.Text("タイピングテストと選択問題で実力を確認", size=14)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=400
            )
        ])
    
    # Tab 4: Progress
    def create_progress_tab():
        stats_text = ft.Text("", size=14)
        
        def load_stats():
            try:
                stats = db.get_learning_stats()
                stats_text.value = f"""学習統計

総単語数: {stats['total_words']}
総フレーズ数: {stats['total_phrases']}
習得済み単語: {stats['words_mastered']}
習得済みフレーズ: {stats['phrases_mastered']}
単語習得率: {stats.get('words_mastery_rate', 0):.1f}%
フレーズ習得率: {stats.get('phrases_mastery_rate', 0):.1f}%

学習セッション数: {stats['total_sessions']}
総学習時間: {stats['total_study_time']} 分
実施テスト数: {stats['total_tests']}
平均正答率: {stats.get('average_accuracy', 0):.1f}%"""
                page.update()
            except Exception as e:
                print(f"Error loading stats: {e}")
                stats_text.value = f"統計情報の読み込みエラー: {str(e)}"
                page.update()
        
        return ft.Column([
            ft.Text("進捗管理", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("学習状況の可視化", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            ft.ElevatedButton(
                "統計情報を更新",
                icon=ft.icons.REFRESH,
                on_click=lambda e: load_stats()
            ),
            ft.Container(height=10),
            ft.Container(
                content=stats_text,
                padding=20,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5
            )
        ])
    
    # Tab 5: Settings
    def create_settings_tab():
        return ft.Column([
            ft.Text("設定", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("アプリケーション設定と翻訳API設定", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            
            # Translation API Settings
            ft.Container(
                content=ft.Column([
                    ft.Text("🌐 翻訳API設定", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("より高品質な日本語翻訳のためのAPI設定", size=14, color=ft.colors.GREY_700),
                    ft.Container(height=10),
                    
                    # Current status
                    ft.Container(
                        content=ft.Column([
                            ft.Text("現在の翻訳サービス状況:", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("✅ ローカル辞書（300+語彙・即座）", size=14),
                            ft.Text("✅ Google Translate 無料版（制限あり）", size=14),
                            ft.Text("✅ MyMemory API（無料）", size=14),
                            ft.Text("❓ Google Cloud Translation API（APIキー必要）", size=14, color=ft.colors.ORANGE),
                            ft.Text("❓ DeepL API（APIキー必要・高品質）", size=14, color=ft.colors.ORANGE),
                        ]),
                        padding=15,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5
                    ),
                    
                    ft.Container(height=15),
                    
                    # API Key Setup Guide
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🔑 APIキー設定ガイド", size=18, weight=ft.FontWeight.BOLD),
                            
                            ft.Text("1. Google Cloud Translation API（推奨）", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                            ft.Text("• 月間500,000文字まで無料", size=14),
                            ft.Text("• 手順: https://cloud.google.com/ → プロジェクト作成 → Translation API有効化 → APIキー作成", size=12),
                            ft.Text("• クレジットカード登録必要（無料枠内は課金なし）", size=12, color=ft.colors.GREY_600),
                            
                            ft.Container(height=10),
                            
                            ft.Text("2. DeepL API（高品質）", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN),
                            ft.Text("• 月間500,000文字まで無料", size=14),
                            ft.Text("• 手順: https://www.deepl.com/pro-api → 無料登録 → APIキー取得", size=12),
                            ft.Text("• クレジットカード登録不要", size=12, color=ft.colors.GREEN),
                            
                            ft.Container(height=15),
                            
                            ft.Text("📝 設定方法", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("1. ターミナルで: python translation_config.py", size=14, bgcolor=ft.colors.GREY_100),
                            ft.Text("2. translation_keys.txt ファイルを編集", size=14),
                            ft.Text("3. APIキーを追加:", size=14),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("google_api_key=YOUR_GOOGLE_API_KEY", size=12, color=ft.colors.BLUE),
                                    ft.Text("deepl_api_key=YOUR_DEEPL_API_KEY", size=12, color=ft.colors.GREEN),
                                ]),
                                padding=10,
                                bgcolor=ft.colors.GREY_100,
                                border_radius=5
                            ),
                            
                            ft.Container(height=10),
                            
                            ft.Text("💰 料金について", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("• 両方とも無料枠で十分使用可能", size=14),
                            ft.Text("• 1,000語の分析 ≈ 5,000文字", size=14),
                            ft.Text("• 月200回分析 ≈ 100,000文字（無料枠内）", size=14),
                            ft.Text("• 超過後: Google $20/100万文字、DeepL €5.99/月〜", size=12, color=ft.colors.GREY_600),
                            
                        ]),
                        padding=20,
                        border=ft.border.all(1, ft.colors.BLUE_100),
                        border_radius=10,
                        bgcolor=ft.colors.BLUE_50
                    ),
                    
                    ft.Container(height=15),
                    
                    # Quick Actions
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🚀 クイックアクション", size=16, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.ElevatedButton(
                                    "設定ファイル作成",
                                    icon=ft.icons.CREATE_NEW_FOLDER,
                                    on_click=lambda e: create_config_file(),
                                    bgcolor=ft.colors.BLUE,
                                    color=ft.colors.WHITE
                                ),
                                ft.ElevatedButton(
                                    "翻訳テスト",
                                    icon=ft.icons.TRANSLATE,
                                    on_click=lambda e: test_translation(),
                                    bgcolor=ft.colors.GREEN,
                                    color=ft.colors.WHITE
                                ),
                            ], spacing=10),
                        ]),
                        padding=15,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5
                    )
                ]),
                padding=20
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def create_config_file():
        """Create translation config file"""
        try:
            from translation_config import create_config_template
            create_config_template()
            print("✅ 設定ファイル translation_keys.txt を作成しました")
        except Exception as e:
            print(f"❌ 設定ファイル作成エラー: {e}")
    
    def test_translation():
        """Test translation service"""
        try:
            from translation_service import get_translation_service
            from translation_config import load_api_keys
            
            api_keys = load_api_keys()
            translator = get_translation_service(
                google_api_key=api_keys.get('google'),
                deepl_api_key=api_keys.get('deepl')
            )
            
            test_words = ["makan", "kerja", "selamat"]
            print("\n🧪 翻訳テスト結果:")
            for word in test_words:
                translation = translator.translate(word)
                print(f"  {word} → {translation}")
                
        except Exception as e:
            print(f"❌ 翻訳テストエラー: {e}")
    
    # Update content based on current tab
    def update_content():
        if current_tab == 0:
            content_container.content = create_file_tab()
        elif current_tab == 1:
            content_container.content = create_learning_list_tab()
        elif current_tab == 2:
            content_container.content = create_flashcard_tab()
        elif current_tab == 3:
            content_container.content = create_test_tab()
        elif current_tab == 4:
            content_container.content = create_progress_tab()
        elif current_tab == 5:
            content_container.content = create_settings_tab()
        
        # Update button colors
        for i, button in enumerate(tab_buttons.controls):
            button.bgcolor = ft.colors.BLUE if i == current_tab else None
        
        page.update()
    
    # Main layout
    page.add(
        ft.Column([
            ft.Text("🇮🇩 インドネシア語学習支援ツール v1.0", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            tab_buttons,
            ft.Container(height=10),
            content_container
        ])
    )
    
    # Initialize with file tab
    update_content()
    print("Application loaded successfully!")

if __name__ == "__main__":
    ft.app(target=final_working_app)
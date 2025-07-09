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
    page.window_height = 900  # 高さを増やす
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
        height=700,  # 高さを増やす
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
        
        def pick_files(e):
            print("Opening file picker...")
            
            def on_result(result):
                if result and result.files:
                    print(f"Selected {len(result.files)} files")
                    for file in result.files:
                        if file.path not in [f['path'] for f in selected_files]:
                            selected_files.append({
                                'path': file.path,
                                'name': file.name,
                                'size': Path(file.path).stat().st_size if Path(file.path).exists() else 0
                            })
                    update_file_list()
                    status_text.value = f"{len(result.files)} 個のファイルを追加しました"
                    page.update()
                else:
                    print("No files selected")
            
            file_picker = ft.FilePicker(on_result=on_result)
            page.overlay.append(file_picker)
            page.update()
            
            try:
                file_picker.pick_files(
                    dialog_title="ファイルを選択",
                    allow_multiple=True,
                    allowed_extensions=["txt", "docx", "pdf", "xlsx"]
                )
            except Exception as ex:
                print(f"File picker error: {ex}")
                status_text.value = f"ファイル選択エラー: {str(ex)}"
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
                        # Check if word already exists
                        existing_words = db.search_words(stem)
                        if existing_words:
                            print(f"Word '{stem}' already exists, skipping...")
                            continue
                        
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
                            frequency=count,
                            notes=""
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
        
        # 左側のコントロール部分
        left_side = ft.Column([
            ft.Text("ファイル処理", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton(
                    "ファイル選択",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=pick_files,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE
                ),
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
        ], expand=True)
        
        # 右側の分析結果部分
        right_side = ft.Column([
            ft.Text("分析結果:", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([results_text], scroll=ft.ScrollMode.ALWAYS),
                height=500,  # さらに高くする
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5,
                padding=10
            )
        ], expand=True)
        
        return ft.Row([
            ft.Container(content=left_side, width=500),  # 左側を固定幅
            ft.Container(width=20),  # スペーサー
            ft.Container(content=right_side, expand=True)  # 右側を可変幅
        ])
    
    # Tab 1: Learning List
    def create_learning_list_tab():
        list_view = ft.ListView(height=450, spacing=5)
        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("翻訳を編集"),
            content_padding=20,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
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
                        # Check if translation needs improvement
                        needs_translation = (
                            item.translation.endswith('（翻訳取得失敗）') or 
                            item.translation.endswith('（翻訳未登録）') or
                            item.translation == item.content
                        )
                        
                        # Create subtitle with notes indicator
                        subtitle_text = f"翻訳: {item.translation} | 優先度: {item.learning_priority:.1f}"
                        try:
                            item_notes = getattr(item, 'notes', '') or ''
                        except AttributeError:
                            item_notes = ''
                        if item_notes:
                            subtitle_text += f" 📝"
                        
                        list_item = ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.STAR if item.learning_priority > 5 else ft.icons.CIRCLE,
                                color=ft.colors.YELLOW if item.learning_priority > 5 else None
                            ),
                            title=ft.Text(item.content),
                            subtitle=ft.Text(
                                subtitle_text,
                                color=ft.colors.RED if needs_translation else None
                            ),
                            trailing=ft.Row([
                                ft.Text(f"頻度: {item.frequency}"),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="翻訳・備考を編集",
                                    on_click=lambda e, word=item: edit_translation(word)
                                )
                            ], tight=True)
                        )
                        list_view.controls.append(list_item)
                
                page.update()
            except Exception as e:
                print(f"Error loading learning items: {e}")
                list_view.controls.append(ft.Text(f"エラー: {str(e)}"))
                page.update()
        
        def edit_translation(word_item):
            """Edit translation dialog"""
            
            # Create input fields
            indonesian_field = ft.TextField(
                label="インドネシア語",
                value=word_item.content,
                read_only=True,
                width=300
            )
            
            japanese_field = ft.TextField(
                label="日本語翻訳",
                value=word_item.translation,
                width=300,
                autofocus=True
            )
            
            # Get notes safely
            try:
                notes_value = getattr(word_item, 'notes', '') or ''
            except AttributeError:
                notes_value = ''
                
            notes_field = ft.TextField(
                label="備考・注意事項",
                value=notes_value,
                width=300,
                multiline=True,
                min_lines=2,
                max_lines=4
            )
            
            def save_translation(e):
                try:
                    new_translation = japanese_field.value.strip()
                    new_notes = notes_field.value.strip()
                    
                    if not new_translation:
                        japanese_field.error_text = "翻訳を入力してください"
                        page.update()
                        return
                    
                    # Update in database
                    from data.models import Word
                    
                    # Find and update the word
                    words = db.search_words(word_item.content)
                    if words:
                        word = words[0]
                        # Update the word's translation and notes
                        updated_word = Word(
                            id=word.id,
                            indonesian=word.indonesian,
                            japanese=new_translation,
                            stem=word.stem,
                            category=word.category,
                            difficulty=word.difficulty,
                            frequency=word.frequency,
                            notes=new_notes
                        )
                        db.update_word(updated_word)
                        print(f"Updated: {word_item.content} -> {new_translation}")
                        if new_notes:
                            print(f"Notes: {new_notes}")
                        
                        # Close dialog and refresh list
                        page.dialog.open = False
                        page.update()
                        load_learning_items()
                    else:
                        japanese_field.error_text = "単語が見つかりません"
                        page.update()
                        
                except Exception as ex:
                    print(f"Translation update error: {ex}")
                    japanese_field.error_text = f"更新エラー: {str(ex)}"
                    page.update()
            
            def cancel_edit(e):
                page.dialog.open = False
                page.update()
            
            # Update dialog content
            edit_dialog.content = ft.Column([
                indonesian_field,
                ft.Container(height=10),
                japanese_field,
                ft.Container(height=10),
                notes_field,
                ft.Container(height=10),
                ft.Text("※ 専門用語の翻訳修正と注意事項を記録できます", 
                       size=12, color=ft.colors.GREY_600)
            ], tight=True)
            
            edit_dialog.actions = [
                ft.TextButton("キャンセル", on_click=cancel_edit),
                ft.ElevatedButton("保存", on_click=save_translation)
            ]
            
            # Show dialog
            page.dialog = edit_dialog
            page.dialog.open = True
            page.update()
        
        def auto_translate_missing():
            """Auto-translate words with missing translations"""
            try:
                from translation_service import get_translation_service
                from translation_config import load_api_keys
                
                # Load API keys and initialize translation service
                api_keys = load_api_keys()
                translator = get_translation_service(
                    google_api_key=api_keys.get('google'),
                    deepl_api_key=api_keys.get('deepl')
                )
                
                # Get words with missing translations
                items = priority_manager.get_priority_list(limit=100)
                missing_count = 0
                updated_count = 0
                
                for item in items:
                    if (item.translation.endswith('（翻訳取得失敗）') or 
                        item.translation.endswith('（翻訳未登録）') or
                        item.translation == item.content):
                        
                        missing_count += 1
                        print(f"Re-translating: {item.content}...")
                        
                        new_translation = translator.translate(item.content, 'id', 'ja')
                        if new_translation and new_translation != item.content:
                            # Update in database
                            words = db.search_words(item.content)
                            if words:
                                from data.models import Word
                                word = words[0]
                                updated_word = Word(
                                    id=word.id,
                                    indonesian=word.indonesian,
                                    japanese=new_translation,
                                    stem=word.stem,
                                    category=word.category,
                                    difficulty=word.difficulty,
                                    frequency=word.frequency
                                )
                                db.update_word(updated_word)
                                updated_count += 1
                                print(f"Updated: {item.content} -> {new_translation}")
                        
                        # Small delay to avoid rate limiting
                        import time
                        time.sleep(0.5)
                
                print(f"Auto-translation complete: {updated_count}/{missing_count} words updated")
                load_learning_items()
                
            except Exception as e:
                print(f"Auto-translation error: {e}")
        
        def export_to_csv(e):
            """Export learning list to CSV for Excel editing"""
            try:
                import csv
                from datetime import datetime
                
                # Get all learning items
                items = priority_manager.get_priority_list(limit=1000)
                if not items:
                    print("No items to export")
                    return
                
                # Create CSV file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_path = Path(__file__).parent / f"indonesian_words_{timestamp}.csv"
                
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header
                    writer.writerow(['インドネシア語', '日本語翻訳', '備考・注意事項', '語幹', '頻度', '優先度', '修正要否'])
                    
                    # Write data
                    for item in items:
                        needs_fix = (
                            item.translation.endswith('（翻訳取得失敗）') or 
                            item.translation.endswith('（翻訳未登録）') or
                            item.translation == item.content
                        )
                        # Get notes safely
                        try:
                            item_notes = getattr(item, 'notes', '') or ''
                        except AttributeError:
                            item_notes = ''
                            
                        writer.writerow([
                            item.content,
                            item.translation,
                            item_notes,  # 備考欄
                            item.stem if hasattr(item, 'stem') else '',
                            item.frequency,
                            f"{item.learning_priority:.1f}",
                            "要修正" if needs_fix else "OK"
                        ])
                
                print(f"✅ CSV exported: {csv_path}")
                print(f"Exported {len(items)} words")
                print("Excelで編集後、「CSV取り込み」ボタンで読み込んでください")
                
            except Exception as ex:
                print(f"❌ CSV export error: {ex}")
        
        def import_from_csv(e):
            """Import translations from CSV file"""
            
            def on_file_result(result):
                if result and result.files:
                    csv_file = result.files[0]
                    try:
                        import csv
                        
                        # Detect encoding
                        try:
                            import chardet
                            with open(csv_file.path, 'rb') as f:
                                raw_data = f.read()
                                encoding_result = chardet.detect(raw_data)
                                encoding = encoding_result['encoding'] or 'utf-8'
                        except ImportError:
                            # Fallback if chardet is not available
                            encoding = 'utf-8-sig'
                        
                        print(f"Reading CSV file: {csv_file.name} (encoding: {encoding})")
                        
                        updated_count = 0
                        error_count = 0
                        
                        with open(csv_file.path, 'r', encoding=encoding) as csvfile:
                            reader = csv.reader(csvfile)
                            header = next(reader)  # Skip header
                            print(f"CSV header: {header}")
                            
                            for row_num, row in enumerate(reader, start=2):
                                if len(row) < 2:
                                    continue
                                
                                indonesian_word = row[0].strip()
                                japanese_translation = row[1].strip()
                                notes = row[2].strip() if len(row) > 2 else ''  # 備考欄
                                
                                if not indonesian_word or not japanese_translation:
                                    continue
                                
                                try:
                                    # Find and update the word
                                    words = db.search_words(indonesian_word)
                                    if words:
                                        word = words[0]
                                        from data.models import Word
                                        
                                        updated_word = Word(
                                            id=word.id,
                                            indonesian=word.indonesian,
                                            japanese=japanese_translation,
                                            stem=word.stem,
                                            category=word.category,
                                            difficulty=word.difficulty,
                                            frequency=word.frequency,
                                            notes=notes
                                        )
                                        db.update_word(updated_word)
                                        updated_count += 1
                                        print(f"Updated: {indonesian_word} -> {japanese_translation}")
                                        if notes:
                                            print(f"  Notes: {notes}")
                                    else:
                                        print(f"Word not found: {indonesian_word}")
                                        error_count += 1
                                        
                                except Exception as update_error:
                                    print(f"Error updating {indonesian_word}: {update_error}")
                                    error_count += 1
                        
                        print(f"✅ CSV import complete: {updated_count} updated, {error_count} errors")
                        load_learning_items()  # Refresh the list
                        
                    except Exception as ex:
                        print(f"❌ CSV import error: {ex}")
                else:
                    print("No file selected")
            
            # Create file picker for CSV import
            csv_picker = ft.FilePicker(on_result=on_file_result)
            page.overlay.append(csv_picker)
            page.update()
            
            try:
                csv_picker.pick_files(
                    dialog_title="CSVファイルを選択",
                    allowed_extensions=["csv"],
                    allow_multiple=False
                )
            except Exception as ex:
                print(f"File picker error: {ex}")
        
        load_button = ft.ElevatedButton(
            "学習リスト更新",
            icon=ft.icons.REFRESH,
            on_click=lambda e: load_learning_items()
        )
        
        auto_translate_button = ft.ElevatedButton(
            "未翻訳を自動翻訳",
            icon=ft.icons.TRANSLATE,
            on_click=lambda e: auto_translate_missing(),
            bgcolor=ft.colors.ORANGE,
            color=ft.colors.WHITE
        )
        
        export_csv_button = ft.ElevatedButton(
            "CSV書き出し",
            icon=ft.icons.DOWNLOAD,
            on_click=export_to_csv,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        import_csv_button = ft.ElevatedButton(
            "CSV取り込み",
            icon=ft.icons.UPLOAD,
            on_click=import_from_csv,
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE
        )
        
        return ft.Column([
            ft.Text("学習リスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("優先度順の学習アイテム（赤文字は翻訳要修正）", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            ft.Row([
                load_button,
                auto_translate_button
            ], spacing=10),
            ft.Container(height=5),
            ft.Row([
                export_csv_button,
                import_csv_button
            ], spacing=10),
            ft.Text("📋 CSV編集手順: 1.書き出し → 2.Excelで翻訳編集 → 3.取り込み", 
                   size=12, color=ft.colors.GREY_600),
            ft.Container(height=10),
            ft.Container(
                content=list_view,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=5
            )
        ])
    
    # Tab 2: Flashcards
    def create_flashcard_tab():
        # State for flashcard session
        current_cards = []
        current_index = 0
        is_answer_shown = False
        session_stats = {"correct": 0, "total": 0}
        
        # UI elements
        card_display = ft.Container(
            width=500,
            height=300,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(2, ft.colors.BLUE_200),
            border_radius=15,
            padding=30,
            alignment=ft.alignment.center
        )
        
        progress_text = ft.Text("", size=14, color=ft.colors.GREY_600)
        stats_text = ft.Text("", size=14, color=ft.colors.GREY_600)
        
        def load_flashcards(e):
            """Load flashcards from learning list"""
            nonlocal current_cards, current_index
            try:
                # Get words from priority manager
                items = priority_manager.get_priority_list(limit=20)  # Top 20 words
                if not items:
                    card_display.content = ft.Text("学習単語がありません。先にファイルを分析してください。", 
                                                  size=16, text_align=ft.TextAlign.CENTER)
                    page.update()
                    return
                
                current_cards = items
                current_index = 0
                session_stats["correct"] = 0
                session_stats["total"] = 0
                
                show_card()
                update_stats()
                print(f"Loaded {len(current_cards)} flashcards")
                
            except Exception as ex:
                print(f"Error loading flashcards: {ex}")
                card_display.content = ft.Text(f"エラー: {str(ex)}", size=16, text_align=ft.TextAlign.CENTER)
                page.update()
        
        def show_card():
            """Display current card (question side)"""
            nonlocal is_answer_shown
            if not current_cards or current_index >= len(current_cards):
                show_session_complete()
                return
            
            is_answer_shown = False
            current_card = current_cards[current_index]
            
            # Show Indonesian word (question)
            card_display.content = ft.Column([
                ft.Text("インドネシア語", size=14, color=ft.colors.BLUE_700),
                ft.Container(height=20),
                ft.Text(current_card.content, size=36, weight=ft.FontWeight.BOLD, 
                       text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK),
                ft.Container(height=30),
                ft.Text("クリックで答えを表示", size=12, color=ft.colors.BLUE_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            card_display.bgcolor = ft.colors.BLUE_100
            progress_text.value = f"カード {current_index + 1} / {len(current_cards)}"
            update_button_states()
            page.update()
        
        def show_answer():
            """Display current card (answer side)"""
            nonlocal is_answer_shown
            if not current_cards or current_index >= len(current_cards):
                return
            
            is_answer_shown = True
            current_card = current_cards[current_index]
            
            # Show Japanese translation (answer)
            card_display.content = ft.Column([
                ft.Text("日本語", size=14, color=ft.colors.GREEN_700),
                ft.Container(height=10),
                ft.Text(current_card.content, size=18, color=ft.colors.BLACK, weight=ft.FontWeight.W_500),
                ft.Container(height=20),
                ft.Text(current_card.translation, size=32, weight=ft.FontWeight.BOLD, 
                       text_align=ft.TextAlign.CENTER, color=ft.colors.GREEN_800),
                ft.Container(height=20),
                # Show notes if available
                ft.Text(
                    getattr(current_card, 'notes', '') or '',
                    size=12, 
                    color=ft.colors.BLACK,
                    text_align=ft.TextAlign.CENTER
                ) if getattr(current_card, 'notes', '') else ft.Container(),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            card_display.bgcolor = ft.colors.GREEN_100
            update_button_states()
            page.update()
        
        def show_session_complete():
            """Show session completion screen"""
            accuracy = (session_stats["correct"] / session_stats["total"] * 100) if session_stats["total"] > 0 else 0
            
            card_display.content = ft.Column([
                ft.Icon(ft.icons.CELEBRATION, size=80, color=ft.colors.GREEN),
                ft.Container(height=20),
                ft.Text("セッション完了！", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Text(f"正答率: {accuracy:.1f}%", size=20),
                ft.Text(f"正解: {session_stats['correct']} / {session_stats['total']}", size=16, color=ft.colors.GREY_600),
                ft.Container(height=30),
                ft.ElevatedButton(
                    "もう一度練習",
                    on_click=load_flashcards,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            card_display.bgcolor = ft.colors.WHITE
            progress_text.value = "セッション完了"
            page.update()
        
        def on_card_click(e):
            """Handle card click (show answer or next card)"""
            if not current_cards:
                return
                
            if not is_answer_shown:
                show_answer()
            # If answer is shown, wait for correct/incorrect button
        
        def mark_correct(e):
            """Mark current answer as correct"""
            if is_answer_shown:
                session_stats["correct"] += 1
                session_stats["total"] += 1
                next_card()
        
        def mark_incorrect(e):
            """Mark current answer as incorrect"""
            if is_answer_shown:
                session_stats["total"] += 1
                next_card()
        
        def next_card():
            """Move to next card"""
            nonlocal current_index
            current_index += 1
            update_stats()
            show_card()
        
        def update_stats():
            """Update statistics display"""
            if session_stats["total"] > 0:
                accuracy = session_stats["correct"] / session_stats["total"] * 100
                stats_text.value = f"正答率: {accuracy:.1f}% ({session_stats['correct']}/{session_stats['total']})"
            else:
                stats_text.value = "統計: まだありません"
        
        # Make card clickable
        card_display.on_click = on_card_click
        
        # Control buttons
        correct_button = ft.ElevatedButton(
            "正解 ✓",
            on_click=mark_correct,
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            disabled=True
        )
        
        incorrect_button = ft.ElevatedButton(
            "不正解 ✗",
            on_click=mark_incorrect,
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            disabled=True
        )
        
        skip_button = ft.ElevatedButton(
            "スキップ →",
            on_click=lambda e: next_card(),
            bgcolor=ft.colors.GREY,
            color=ft.colors.WHITE
        )
        
        control_buttons = ft.Row([
            correct_button,
            incorrect_button,
            skip_button
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        def update_button_states():
            """Update button enabled/disabled states"""
            correct_button.disabled = not is_answer_shown
            incorrect_button.disabled = not is_answer_shown
            page.update()
        
        # Initialize with welcome message
        card_display.content = ft.Column([
            ft.Icon(ft.icons.SCHOOL, size=80, color=ft.colors.BLUE),
            ft.Container(height=20),
            ft.Text("フラッシュカード学習", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text("「学習開始」ボタンで暗記練習を始めましょう", size=14, color=ft.colors.GREY_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        return ft.Column([
            ft.Text("フラッシュカード", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("インタラクティブな暗記学習", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            
            # Start button
            ft.Container(
                content=ft.ElevatedButton(
                    "学習開始",
                    icon=ft.icons.PLAY_ARROW,
                    on_click=load_flashcards,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE,
                    height=40
                ),
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=20),
            
            # Progress and stats
            ft.Row([
                progress_text,
                ft.Container(expand=True),
                stats_text
            ]),
            
            ft.Container(height=10),
            
            # Flashcard display
            ft.Container(
                content=card_display,
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=20),
            
            # Control buttons
            control_buttons,
            
            ft.Container(height=10),
            
            # Instructions
            ft.Text(
                "💡 使い方: カードをクリック→答え表示→正解/不正解を選択",
                size=12,
                color=ft.colors.GREY_600,
                text_align=ft.TextAlign.CENTER
            )
        ])
    
    # Tab 3: Test
    def create_test_tab():
        # Test state
        test_words = []
        current_question = 0
        test_type = "typing"  # "typing" or "choice"
        test_stats = {"correct": 0, "total": 0, "start_time": None}
        user_answer = ""
        
        # UI elements
        question_display = ft.Container(
            width=600,
            height=200,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(2, ft.colors.BLUE_200),
            border_radius=10,
            padding=30,
            alignment=ft.alignment.center
        )
        
        answer_input = ft.TextField(
            label="答えを入力してください",
            width=400,
            autofocus=True,
            on_submit=lambda e: check_typing_answer()
        )
        
        choice_buttons = ft.Column([])
        submit_button = ft.ElevatedButton(
            "回答",
            on_click=lambda e: check_typing_answer(),
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        result_display = ft.Container(
            width=600,
            height=100,
            visible=False
        )
        
        progress_text = ft.Text("", size=14)
        stats_text = ft.Text("", size=14)
        
        def start_test(test_mode):
            """Start test with specified mode"""
            nonlocal test_words, current_question, test_type, test_stats
            
            try:
                # Get test words
                items = priority_manager.get_priority_list(limit=10)  # 10 questions
                if not items:
                    question_display.content = ft.Text("テスト用の単語がありません。先にファイルを分析してください。", 
                                                     size=16, text_align=ft.TextAlign.CENTER)
                    page.update()
                    return
                
                test_words = items
                current_question = 0
                test_type = test_mode
                test_stats = {"correct": 0, "total": 0, "start_time": None}
                
                import time
                test_stats["start_time"] = time.time()
                
                show_question()
                update_ui_for_test_type()
                print(f"Started {test_mode} test with {len(test_words)} words")
                
            except Exception as ex:
                print(f"Error starting test: {ex}")
                question_display.content = ft.Text(f"エラー: {str(ex)}", size=16, text_align=ft.TextAlign.CENTER)
                page.update()
        
        def show_question():
            """Display current question"""
            if current_question >= len(test_words):
                show_test_complete()
                return
            
            word = test_words[current_question]
            
            if test_type == "typing":
                # Show Japanese, ask for Indonesian
                question_display.content = ft.Column([
                    ft.Text("次の日本語をインドネシア語で入力してください", size=14, color=ft.colors.GREY_600),
                    ft.Container(height=20),
                    ft.Text(word.translation, size=28, weight=ft.FontWeight.BOLD, 
                           text_align=ft.TextAlign.CENTER, color=ft.colors.BLUE_800),
                    ft.Container(height=10),
                    ft.Text(f"問題 {current_question + 1} / {len(test_words)}", 
                           size=12, color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                
            else:  # choice
                # Show Indonesian, ask for Japanese (multiple choice)
                import random
                
                # Get correct answer
                correct_answer = word.translation
                
                # Generate wrong choices
                all_words = test_words + (priority_manager.get_priority_list(limit=50) or [])
                wrong_choices = [w.translation for w in all_words if w.translation != correct_answer]
                wrong_choices = random.sample(wrong_choices, min(3, len(wrong_choices)))
                
                # Mix choices
                choices = [correct_answer] + wrong_choices
                random.shuffle(choices)
                
                question_display.content = ft.Column([
                    ft.Text("次のインドネシア語の意味を選択してください", size=14, color=ft.colors.GREY_600),
                    ft.Container(height=20),
                    ft.Text(word.content, size=28, weight=ft.FontWeight.BOLD, 
                           text_align=ft.TextAlign.CENTER, color=ft.colors.BLUE_800),
                    ft.Container(height=10),
                    ft.Text(f"問題 {current_question + 1} / {len(test_words)}", 
                           size=12, color=ft.colors.GREY_500)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                
                # Create choice buttons
                choice_buttons.controls.clear()
                for i, choice in enumerate(choices):
                    btn = ft.ElevatedButton(
                        f"{chr(65+i)}. {choice}",
                        on_click=lambda e, selected=choice: check_choice_answer(selected),
                        width=350,
                        height=45
                    )
                    choice_buttons.controls.append(btn)
            
            # Reset input
            answer_input.value = ""
            result_display.visible = False
            
            progress_text.value = f"問題 {current_question + 1} / {len(test_words)}"
            update_stats()
            page.update()
        
        def check_typing_answer():
            """Check typing test answer"""
            if current_question >= len(test_words):
                return
                
            user_input = answer_input.value.strip().lower()
            correct_answer = test_words[current_question].content.lower()
            
            # Simple similarity check
            import difflib
            similarity = difflib.SequenceMatcher(None, user_input, correct_answer).ratio()
            is_correct = similarity >= 0.8  # 80% similarity threshold
            
            show_answer_result(is_correct, user_input, correct_answer)
            
            # Update stats
            test_stats["total"] += 1
            if is_correct:
                test_stats["correct"] += 1
            
            # Move to next question after delay
            def next_after_delay():
                import time
                time.sleep(1.5)
                next_question()
            
            # Use threading to avoid blocking UI
            import threading
            threading.Thread(target=next_after_delay, daemon=True).start()
        
        def check_choice_answer(selected_answer):
            """Check choice test answer"""
            if current_question >= len(test_words):
                return
                
            correct_answer = test_words[current_question].translation
            is_correct = selected_answer == correct_answer
            
            show_answer_result(is_correct, selected_answer, correct_answer)
            
            # Update stats
            test_stats["total"] += 1
            if is_correct:
                test_stats["correct"] += 1
            
            # Move to next question after delay
            def next_after_delay():
                import time
                time.sleep(1.5)
                next_question()
            
            import threading
            threading.Thread(target=next_after_delay, daemon=True).start()
        
        def show_answer_result(is_correct, user_answer, correct_answer):
            """Show answer result"""
            if is_correct:
                result_display.content = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN, size=30),
                        ft.Text("正解！", size=20, color=ft.colors.GREEN, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=ft.colors.GREEN_100,
                    padding=15,
                    border_radius=10
                )
            else:
                result_display.content = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.CANCEL, color=ft.colors.RED, size=30),
                            ft.Text("不正解", size=20, color=ft.colors.RED, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text(f"正解: {correct_answer}", size=14, color=ft.colors.BLACK),
                        ft.Text(f"回答: {user_answer}", size=14, color=ft.colors.GREY_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=ft.colors.RED_100,
                    padding=15,
                    border_radius=10
                )
            
            result_display.visible = True
            page.update()
        
        def next_question():
            """Move to next question"""
            nonlocal current_question
            current_question += 1
            show_question()
        
        def show_test_complete():
            """Show test completion screen"""
            import time
            elapsed_time = int(time.time() - test_stats["start_time"]) if test_stats["start_time"] else 0
            accuracy = (test_stats["correct"] / test_stats["total"] * 100) if test_stats["total"] > 0 else 0
            
            question_display.content = ft.Column([
                ft.Icon(ft.icons.EMOJI_EVENTS, size=80, color=ft.colors.AMBER),
                ft.Container(height=20),
                ft.Text("テスト完了！", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                ft.Text(f"正答率: {accuracy:.1f}%", size=20, color=ft.colors.BLUE_700),
                ft.Text(f"正解: {test_stats['correct']} / {test_stats['total']}", size=16),
                ft.Text(f"所要時間: {elapsed_time}秒", size=14, color=ft.colors.GREY_600),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "タイピングテスト再開",
                        on_click=lambda e: start_test("typing"),
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                    ft.ElevatedButton(
                        "選択テスト再開", 
                        on_click=lambda e: start_test("choice"),
                        bgcolor=ft.colors.GREEN,
                        color=ft.colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            # Hide input elements
            answer_input.visible = False
            submit_button.visible = False
            choice_buttons.visible = False
            result_display.visible = False
            
            progress_text.value = "テスト完了"
            page.update()
        
        def update_ui_for_test_type():
            """Update UI based on test type"""
            if test_type == "typing":
                answer_input.visible = True
                submit_button.visible = True
                choice_buttons.visible = False
            else:  # choice
                answer_input.visible = False
                submit_button.visible = False
                choice_buttons.visible = True
            
            page.update()
        
        def update_stats():
            """Update statistics display"""
            if test_stats["total"] > 0:
                accuracy = test_stats["correct"] / test_stats["total"] * 100
                stats_text.value = f"正答率: {accuracy:.1f}% ({test_stats['correct']}/{test_stats['total']})"
            else:
                stats_text.value = "統計: 開始前"
        
        # Initialize welcome screen
        question_display.content = ft.Column([
            ft.Icon(ft.icons.QUIZ, size=80, color=ft.colors.GREEN),
            ft.Container(height=20),
            ft.Text("学習効果測定テスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Text("タイピングまたは選択式でテストを開始しましょう", size=14, color=ft.colors.GREY_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Hide input elements initially
        answer_input.visible = False
        submit_button.visible = False
        choice_buttons.visible = False
        
        return ft.Column([
            ft.Text("テスト", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("学習効果の測定とスキルチェック", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            
            # Test type selection
            ft.Row([
                ft.ElevatedButton(
                    "タイピングテスト",
                    icon=ft.icons.KEYBOARD,
                    on_click=lambda e: start_test("typing"),
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE,
                    height=40
                ),
                ft.ElevatedButton(
                    "選択式テスト",
                    icon=ft.icons.RADIO_BUTTON_CHECKED,
                    on_click=lambda e: start_test("choice"),
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE,
                    height=40
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            
            ft.Container(height=15),
            
            # Progress and stats
            ft.Row([
                progress_text,
                ft.Container(expand=True),
                stats_text
            ]),
            
            ft.Container(height=10),
            
            # Question display
            ft.Container(
                content=question_display,
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=15),
            
            # Answer input (typing)
            ft.Container(
                content=answer_input,
                alignment=ft.alignment.center
            ),
            
            # Submit button (typing)
            ft.Container(
                content=submit_button,
                alignment=ft.alignment.center
            ),
            
            # Choice buttons (multiple choice)
            ft.Container(
                content=choice_buttons,
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=10),
            
            # Result display
            ft.Container(
                content=result_display,
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=10),
            
            # Instructions
            ft.Text(
                "💡 タイピング: 日本語→インドネシア語入力 | 選択式: インドネシア語→日本語選択",
                size=12,
                color=ft.colors.GREY_600,
                text_align=ft.TextAlign.CENTER
            )
        ])
    
    # Tab 4: Progress
    def create_progress_tab():
        stats_text = ft.Text("", size=14)
        word_stats_text = ft.Text("", size=14)
        recent_activity_text = ft.Text("", size=14)
        
        def load_stats():
            try:
                # Basic database stats
                stats = db.get_learning_stats()
                
                # Word analysis stats
                word_stats = get_word_analysis_stats()
                
                # Recent activity
                recent_activity = get_recent_activity()
                
                # Format basic stats
                stats_text.value = f"""📊 基本統計

総単語数: {stats['total_words']:,}
総フレーズ数: {stats['total_phrases']:,}
習得済み単語: {stats['words_mastered']:,}
習得済みフレーズ: {stats['phrases_mastered']:,}
単語習得率: {stats.get('words_mastery_rate', 0):.1f}%
フレーズ習得率: {stats.get('phrases_mastery_rate', 0):.1f}%

学習セッション数: {stats['total_sessions']:,}
総学習時間: {stats['total_study_time']} 分
実施テスト数: {stats['total_tests']:,}
平均正答率: {stats.get('average_accuracy', 0):.1f}%"""
                
                # Format word stats
                word_stats_text.value = f"""🔤 単語分析統計

分析済み単語数: {word_stats['total_words']:,}
翻訳済み単語数: {word_stats['translated_words']:,}
備考付き単語数: {word_stats['words_with_notes']:,}
翻訳完了率: {word_stats['translation_rate']:.1f}%

カテゴリ別分布:
• 一般: {word_stats['categories'].get('general', 0):,}語
• ビジネス: {word_stats['categories'].get('business', 0):,}語
• 製造: {word_stats['categories'].get('production', 0):,}語
• 技術: {word_stats['categories'].get('technical', 0):,}語

優先度レベル分布:
• 高 (7.0+): {word_stats['priority_levels'].get('high', 0):,}語
• 中 (4.0-7.0): {word_stats['priority_levels'].get('medium', 0):,}語
• 低 (-4.0): {word_stats['priority_levels'].get('low', 0):,}語"""
                
                # Format recent activity
                recent_activity_text.value = f"""📈 最近の活動

{recent_activity['summary']}

頻出単語 TOP 5:
{recent_activity['top_words']}

最近追加された単語:
{recent_activity['recent_words']}"""
                
                page.update()
                
            except Exception as e:
                print(f"Error loading stats: {e}")
                stats_text.value = f"統計情報の読み込みエラー: {str(e)}"
                page.update()
        
        def get_word_analysis_stats():
            """Get word analysis statistics"""
            try:
                # Get all words from database
                words = db.get_all_words(limit=None)
                
                stats = {
                    'total_words': len(words),
                    'translated_words': 0,
                    'words_with_notes': 0,
                    'categories': {},
                    'priority_levels': {'high': 0, 'medium': 0, 'low': 0}
                }
                
                for word in words:
                    # Check translation status
                    if (word.japanese and 
                        not word.japanese.endswith('（翻訳取得失敗）') and
                        not word.japanese.endswith('（翻訳未登録）')):
                        stats['translated_words'] += 1
                    
                    # Check notes
                    if hasattr(word, 'notes') and word.notes:
                        stats['words_with_notes'] += 1
                    
                    # Category distribution
                    category = word.category.value if hasattr(word.category, 'value') else str(word.category)
                    stats['categories'][category] = stats['categories'].get(category, 0) + 1
                    
                    # Priority level distribution
                    priority = word.priority
                    if priority >= 7.0:
                        stats['priority_levels']['high'] += 1
                    elif priority >= 4.0:
                        stats['priority_levels']['medium'] += 1
                    else:
                        stats['priority_levels']['low'] += 1
                
                # Calculate translation rate
                stats['translation_rate'] = (stats['translated_words'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0
                
                return stats
                
            except Exception as e:
                print(f"Error getting word analysis stats: {e}")
                return {
                    'total_words': 0,
                    'translated_words': 0,
                    'words_with_notes': 0,
                    'translation_rate': 0,
                    'categories': {},
                    'priority_levels': {'high': 0, 'medium': 0, 'low': 0}
                }
        
        def get_recent_activity():
            """Get recent activity summary"""
            try:
                # Get priority words
                priority_words = priority_manager.get_priority_list(limit=100)
                
                if not priority_words:
                    return {
                        'summary': "まだ分析データがありません",
                        'top_words': "分析を実行してください",
                        'recent_words': "分析を実行してください"
                    }
                
                # Create summary
                total_words = len(priority_words)
                avg_priority = sum(w.learning_priority for w in priority_words) / total_words if total_words > 0 else 0
                
                summary = f"学習対象: {total_words:,}語 | 平均優先度: {avg_priority:.1f}"
                
                # Top words by frequency
                top_words = sorted(priority_words, key=lambda w: w.frequency, reverse=True)[:5]
                top_words_str = ""
                for i, word in enumerate(top_words, 1):
                    top_words_str += f"{i}. {word.content} ({word.frequency}回) - {word.translation}\\n"
                
                # Recent words (highest priority)
                recent_words = sorted(priority_words, key=lambda w: w.learning_priority, reverse=True)[:5]
                recent_words_str = ""
                for i, word in enumerate(recent_words, 1):
                    recent_words_str += f"{i}. {word.content} (優先度: {word.learning_priority:.1f}) - {word.translation}\\n"
                
                return {
                    'summary': summary,
                    'top_words': top_words_str,
                    'recent_words': recent_words_str
                }
                
            except Exception as e:
                print(f"Error getting recent activity: {e}")
                return {
                    'summary': f"エラー: {str(e)}",
                    'top_words': "データ取得エラー",
                    'recent_words': "データ取得エラー"
                }
        
        def export_progress_report():
            """Export progress report to CSV"""
            try:
                from datetime import datetime
                import csv
                
                # Get all data
                words = db.get_all_words(limit=None)
                priority_words = priority_manager.get_priority_list(limit=None)
                
                # Create report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = Path(__file__).parent / f"progress_report_{timestamp}.csv"
                
                with open(report_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow(['インドネシア語', '日本語', '備考', '頻度', '優先度', '難易度', 'カテゴリ'])
                    
                    # Data
                    for word in words:
                        writer.writerow([
                            word.indonesian,
                            word.japanese,
                            getattr(word, 'notes', ''),
                            word.frequency,
                            f"{word.priority:.2f}",
                            word.difficulty,
                            word.category.value if hasattr(word.category, 'value') else str(word.category)
                        ])
                
                print(f"✅ Progress report exported: {report_path}")
                return True
                
            except Exception as e:
                print(f"❌ Export error: {e}")
                return False
        
        # Auto-load stats on tab creation
        load_stats()
        
        return ft.Column([
            ft.Text("進捗管理", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("学習状況の詳細分析と可視化", size=14, color=ft.colors.GREY_600),
            ft.Divider(),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    "統計更新",
                    icon=ft.icons.REFRESH,
                    on_click=lambda e: load_stats(),
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "レポート出力",
                    icon=ft.icons.DOWNLOAD,
                    on_click=lambda e: export_progress_report(),
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE
                )
            ], spacing=10),
            
            ft.Container(height=15),
            
            # Stats in three columns
            ft.Row([
                # Column 1: Basic stats
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=stats_text,
                            padding=15,
                            border=ft.border.all(1, ft.colors.BLUE_200),
                            border_radius=10,
                            bgcolor=ft.colors.BLUE_50
                        )
                    ]),
                    expand=True
                ),
                
                ft.Container(width=10),
                
                # Column 2: Word analysis
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=word_stats_text,
                            padding=15,
                            border=ft.border.all(1, ft.colors.GREEN_200),
                            border_radius=10,
                            bgcolor=ft.colors.GREEN_50
                        )
                    ]),
                    expand=True
                ),
                
                ft.Container(width=10),
                
                # Column 3: Recent activity
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=recent_activity_text,
                            padding=15,
                            border=ft.border.all(1, ft.colors.ORANGE_200),
                            border_radius=10,
                            bgcolor=ft.colors.ORANGE_50
                        )
                    ]),
                    expand=True
                )
            ], spacing=0),
            
            ft.Container(height=15),
            
            # Tips
            ft.Container(
                content=ft.Column([
                    ft.Text("💡 学習のコツ", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("• 高優先度の単語を重点的に学習しましょう", size=14),
                    ft.Text("• フラッシュカードで定期的に復習しましょう", size=14),
                    ft.Text("• テストで理解度を確認しましょう", size=14),
                    ft.Text("• 備考欄に覚えるコツを書き留めましょう", size=14)
                ]),
                padding=15,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                bgcolor=ft.colors.GREY_50
            )
        ], scroll=ft.ScrollMode.AUTO)
    
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
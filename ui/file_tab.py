"""File processing tab UI"""

import flet as ft
from typing import List, Dict, Optional
from pathlib import Path
import threading
import asyncio

from data.database import Database
from data.models import Word, Phrase, Category
from config.settings import Settings
from core.file_processor import FileProcessor
from core.analyzer import IndonesianAnalyzer
from data.patterns import PhrasePatterns


class FileTab(ft.UserControl):
    """File processing tab component"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Initialize processors
        self.file_processor = FileProcessor()
        self.analyzer = IndonesianAnalyzer()
        
        # UI components
        self.file_list = []
        self.file_list_view = None
        self.progress_bar = None
        self.progress_text = None
        self.analyze_button = None
        self.results_view = None
        
        # Analysis state
        self.is_analyzing = False
        self.analysis_results = None
        
    def build(self):
        """Build file processing tab UI"""
        # File selection section
        file_selection = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "ファイル選択",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            text="ファイル選択",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=self._select_files,
                            height=40
                        ),
                        ft.ElevatedButton(
                            text="フォルダ選択",
                            icon=ft.icons.FOLDER_OPEN,
                            on_click=self._select_folder,
                            height=40
                        ),
                        ft.ElevatedButton(
                            text="サンプルデータ",
                            icon=ft.icons.FOLDER_SPECIAL,
                            on_click=self._load_sample_data,
                            height=40,
                            bgcolor=ft.colors.GREEN,
                            color=ft.colors.WHITE
                        ),
                        ft.ElevatedButton(
                            text="クリア",
                            icon=ft.icons.CLEAR,
                            on_click=self._clear_files,
                            height=40,
                            bgcolor=ft.colors.RED,
                            color=ft.colors.WHITE
                        )
                    ], spacing=10),
                    ft.Container(height=10),
                    ft.Text(
                        f"対応形式: {', '.join(self.file_processor.get_supported_extensions())}",
                        size=12,
                        color=ft.colors.GREY_700
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # File list section
        self.file_list_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=ft.padding.all(10)
        )
        
        file_list_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "選択ファイル",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=self.file_list_view,
                        height=200,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Analysis section
        self.progress_bar = ft.ProgressBar(
            visible=False,
            color=ft.colors.PRIMARY
        )
        
        self.progress_text = ft.Text(
            "分析待機中...",
            size=14,
            visible=False
        )
        
        def test_click(e):
            print("Analysis button clicked!")
            self._start_analysis(e)
        
        self.analyze_button = ft.ElevatedButton(
            text="分析開始",
            icon=ft.icons.ANALYTICS,
            on_click=test_click,
            disabled=True,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )
        
        analysis_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "分析実行",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    self.progress_bar,
                    self.progress_text,
                    ft.Container(height=10),
                    self.analyze_button
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Results section
        self.results_view = ft.Container(
            content=ft.Text(
                "分析結果がここに表示されます",
                size=14,
                color=ft.colors.GREY_600
            ),
            padding=ft.padding.all(20)
        )
        
        results_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "分析結果",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    self.results_view
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Main layout
        return ft.Column([
            file_selection,
            file_list_section,
            analysis_section,
            results_section
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def _select_files(self, e):
        """Select files using file picker"""
        print("Opening file picker...")
        
        def on_files_selected(result):
            print(f"File picker result: {result}")
            if result and result.files:
                print(f"Selected {len(result.files)} files")
                for file in result.files:
                    print(f"Adding file: {file.name} -> {file.path}")
                    if file.path not in [f['path'] for f in self.file_list]:
                        self.file_list.append({
                            'path': file.path,
                            'name': file.name,
                            'size': self._get_file_size(file.path)
                        })
                self._update_file_list()
            else:
                print("No files selected")
        
        file_picker = ft.FilePicker(on_result=on_files_selected)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        # Open file picker
        try:
            file_picker.pick_files(
                dialog_title="ファイルを選択",
                allow_multiple=True,
                allowed_extensions=self.file_processor.get_supported_extensions()
            )
        except Exception as picker_error:
            print(f"File picker error: {picker_error}")
            self._show_error(f"ファイル選択エラー: {str(picker_error)}")
    
    def _select_folder(self, e):
        """Select folder using directory picker"""
        def on_folder_selected(result):
            if result.path:
                try:
                    folder_files = self.file_processor.process_folder(result.path)
                    for file_info in folder_files:
                        if file_info['file_path'] not in [f['path'] for f in self.file_list]:
                            self.file_list.append({
                                'path': file_info['file_path'],
                                'name': file_info['file_name'],
                                'size': file_info['file_size']
                            })
                    self._update_file_list()
                except Exception as ex:
                    self._show_error(f"フォルダ読み込みエラー: {str(ex)}")
        
        folder_picker = ft.FilePicker(on_result=on_folder_selected)
        self.page.overlay.append(folder_picker)
        self.page.update()
        
        folder_picker.get_directory_path(dialog_title="フォルダを選択")
    
    def _load_sample_data(self, e):
        """Load sample data files"""
        print("Loading sample data...")
        
        try:
            sample_dir = Path(__file__).parent.parent / "sample_data"
            if not sample_dir.exists():
                self._show_error("サンプルデータフォルダが見つかりません")
                return
            
            sample_files = list(sample_dir.glob("*.txt"))
            if not sample_files:
                self._show_error("サンプルデータファイルが見つかりません")
                return
            
            for file_path in sample_files:
                if str(file_path) not in [f['path'] for f in self.file_list]:
                    self.file_list.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': self._get_file_size(str(file_path))
                    })
                    print(f"Added sample file: {file_path.name}")
            
            self._update_file_list()
            print(f"Loaded {len(sample_files)} sample files")
            
        except Exception as ex:
            print(f"Sample data loading error: {ex}")
            self._show_error(f"サンプルデータ読み込みエラー: {str(ex)}")
    
    def _clear_files(self, e):
        """Clear all selected files"""
        self.file_list.clear()
        self._update_file_list()
    
    def _update_file_list(self):
        """Update file list display"""
        self.file_list_view.controls.clear()
        
        for file_info in self.file_list:
            # Create file item
            file_item = ft.ListTile(
                leading=ft.Icon(ft.icons.INSERT_DRIVE_FILE),
                title=ft.Text(file_info['name']),
                subtitle=ft.Text(f"サイズ: {self._format_file_size(file_info['size'])}"),
                trailing=ft.IconButton(
                    icon=ft.icons.DELETE,
                    on_click=lambda e, path=file_info['path']: self._remove_file(path)
                )
            )
            
            self.file_list_view.controls.append(file_item)
        
        # Update analyze button state
        self.analyze_button.disabled = len(self.file_list) == 0
        
        self.page.update()
    
    def _remove_file(self, file_path: str):
        """Remove file from list"""
        self.file_list = [f for f in self.file_list if f['path'] != file_path]
        self._update_file_list()
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except:
            return 0
    
    def _format_file_size(self, size: int) -> str:
        """Format file size for display"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def _start_analysis(self, e):
        """Start file analysis"""
        if self.is_analyzing or not self.file_list:
            return
        
        self.is_analyzing = True
        self.analyze_button.disabled = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.progress_text.value = "分析を開始しています..."
        self.page.update()
        
        # Run analysis in separate thread
        threading.Thread(target=self._run_analysis, daemon=True).start()
    
    def _run_analysis(self):
        """Run analysis in background thread"""
        try:
            # Process files
            self._update_progress("ファイルを処理中...")
            file_paths = [f['path'] for f in self.file_list]
            file_results = self.file_processor.process_files(file_paths)
            
            # Combine content
            self._update_progress("テキストを統合中...")
            combined_text = self.file_processor.combine_contents(file_results)
            
            # Analyze text
            self._update_progress("言語分析中...")
            analysis_results = self.analyzer.analyze_text(combined_text)
            
            # Extract phrases
            self._update_progress("フレーズを抽出中...")
            phrases = self.analyzer.extract_phrases(combined_text)
            
            # Save to database
            self._update_progress("データベースに保存中...")
            self._save_to_database(analysis_results, phrases)
            
            # Update UI
            self._update_progress("完了")
            self.analysis_results = analysis_results
            self.page.run_thread_safe(self._show_results)
            
        except Exception as ex:
            self.page.run_thread_safe(lambda: self._show_error(f"分析エラー: {str(ex)}"))
        finally:
            self.is_analyzing = False
            self.page.run_thread_safe(self._reset_ui)
    
    def _update_progress(self, message: str):
        """Update progress message"""
        def update():
            self.progress_text.value = message
            self.page.update()
        
        self.page.run_thread_safe(update)
    
    def _save_to_database(self, analysis_results: dict, phrases: List[tuple]):
        """Save analysis results to database"""
        # Save words
        for word, freq in analysis_results['word_frequency'].items():
            if len(word) > 2:  # Skip very short words
                stem = analysis_results['stem_frequency'].get(word, word)
                word_obj = Word(
                    indonesian=word,
                    japanese="",  # To be filled later
                    stem=stem,
                    category=Category.GENERAL,
                    frequency=freq,
                    difficulty=1
                )
                try:
                    self.database.add_word(word_obj)
                except:
                    pass  # Skip duplicates
        
        # Save phrases
        for phrase, freq in phrases:
            if len(phrase.split()) >= 2:  # Only multi-word phrases
                phrase_obj = Phrase(
                    indonesian=phrase,
                    japanese="",  # To be filled later
                    category=Category.GENERAL,
                    frequency=freq,
                    difficulty=1
                )
                try:
                    self.database.add_phrase(phrase_obj)
                except:
                    pass  # Skip duplicates
        
        # Add common patterns
        self._add_common_patterns()
    
    def _add_common_patterns(self):
        """Add common phrase patterns to database"""
        patterns = PhrasePatterns.get_all_phrases()
        
        for indonesian, japanese in patterns:
            # Determine category
            category = Category.GENERAL
            if any(word in indonesian.lower() for word in ['rapat', 'meeting', 'diskusi']):
                category = Category.MEETING
            elif any(word in indonesian.lower() for word in ['produksi', 'target', 'shift']):
                category = Category.PRODUCTION
            elif any(word in indonesian.lower() for word in ['safety', 'helm', 'bahaya']):
                category = Category.SAFETY
            elif any(word in indonesian.lower() for word in ['bisnis', 'perusahaan', 'klien']):
                category = Category.BUSINESS
            elif any(word in indonesian.lower() for word in ['sistem', 'komputer', 'software']):
                category = Category.TECHNICAL
            
            phrase_obj = Phrase(
                indonesian=indonesian,
                japanese=japanese,
                category=category,
                frequency=1,
                difficulty=2
            )
            try:
                self.database.add_phrase(phrase_obj)
            except:
                pass  # Skip duplicates
    
    def _show_results(self):
        """Show analysis results"""
        if not self.analysis_results:
            return
        
        # Create results display
        results_content = ft.Column([
            ft.Text(
                "分析完了!",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREEN
            ),
            ft.Container(height=10),
            ft.Row([
                ft.Column([
                    ft.Text("総単語数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(self.analysis_results['total_words']), size=20)
                ]),
                ft.Column([
                    ft.Text("ユニーク単語数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(self.analysis_results['unique_words']), size=20)
                ]),
                ft.Column([
                    ft.Text("語幹数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(self.analysis_results['unique_stems']), size=20)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Container(height=10),
            ft.ElevatedButton(
                text="学習リストを表示",
                icon=ft.icons.LIST,
                on_click=self._show_learning_list
            )
        ])
        
        self.results_view.content = results_content
        self.page.update()
    
    def _show_learning_list(self, e):
        """Switch to learning list tab"""
        # This would be implemented by the parent window
        if hasattr(self.page, 'main_window'):
            self.page.main_window.switch_to_tab('learning_list')
    
    def _reset_ui(self):
        """Reset UI after analysis"""
        self.analyze_button.disabled = len(self.file_list) == 0
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error message"""
        error_dialog = ft.AlertDialog(
            title=ft.Text("エラー"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_error_dialog())
            ]
        )
        
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()
    
    def _close_error_dialog(self):
        """Close error dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def refresh(self):
        """Refresh tab content"""
        pass
    
    def on_resize(self, width: int, height: int):
        """Handle resize"""
        pass
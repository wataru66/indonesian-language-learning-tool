"""Enhanced flashcard learning view"""

import flet as ft
from typing import Optional, List, Dict
from datetime import datetime
import time

from data.database import Database
from data.models import LearningStatus
from config.settings import Settings
from core.flashcard import FlashcardManager, StudyMode, CardSide, FlashCard, StudySession
from core.priority_manager import ItemType


class FlashcardView(ft.UserControl):
    """Enhanced flashcard learning component"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Initialize flashcard manager
        self.flashcard_manager = FlashcardManager(database)
        
        # UI components
        self.session_setup = None
        self.flashcard_display = None
        self.session_controls = None
        self.progress_info = None
        self.results_display = None
        
        # Session state
        self.current_session = None
        self.is_card_flipped = False
        self.card_start_time = None
        
        # UI state
        self.main_container = None
        
    def build(self):
        """Build flashcard view UI"""
        
        # Create main container that switches between setup and study
        self.main_container = ft.Container(
            content=self._create_session_setup(),
            expand=True
        )
        
        return self.main_container
    
    def _create_session_setup(self) -> ft.Container:
        """Create session setup interface"""
        
        # Study mode selection
        mode_selection = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "学習モード選択",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="word_only", label="単語のみ"),
                            ft.Radio(value="phrase_only", label="フレーズのみ"),
                            ft.Radio(value="mixed", label="単語＋フレーズ")
                        ]),
                        value="mixed"
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Card side selection
        side_selection = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "表示設定",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="indonesian", label="インドネシア語 → 日本語"),
                            ft.Radio(value="japanese", label="日本語 → インドネシア語")
                        ]),
                        value="indonesian"
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Session configuration
        config_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "学習設定",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text("カード数", size=14, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=100,
                                value="20",
                                options=[
                                    ft.dropdown.Option("10", "10"),
                                    ft.dropdown.Option("20", "20"),
                                    ft.dropdown.Option("30", "30"),
                                    ft.dropdown.Option("50", "50")
                                ]
                            )
                        ]),
                        ft.Column([
                            ft.Text("カテゴリ", size=14, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=150,
                                value="all",
                                options=[
                                    ft.dropdown.Option("all", "すべて"),
                                    ft.dropdown.Option("general", "一般"),
                                    ft.dropdown.Option("business", "ビジネス"),
                                    ft.dropdown.Option("meeting", "会議"),
                                    ft.dropdown.Option("production", "生産"),
                                    ft.dropdown.Option("safety", "安全"),
                                    ft.dropdown.Option("technical", "技術"),
                                    ft.dropdown.Option("daily", "日常")
                                ]
                            )
                        ]),
                        ft.Column([
                            ft.Text("学習状態", size=14, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=120,
                                value="all",
                                options=[
                                    ft.dropdown.Option("all", "すべて"),
                                    ft.dropdown.Option("not_started", "未学習"),
                                    ft.dropdown.Option("learning", "学習中"),
                                    ft.dropdown.Option("mastered", "習得済み")
                                ]
                            )
                        ])
                    ], spacing=20)
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Quick start options
        quick_start = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "クイックスタート",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            text="復習セッション",
                            icon=ft.icons.REFRESH,
                            on_click=self._start_review_session
                        ),
                        ft.ElevatedButton(
                            text="新規学習",
                            icon=ft.icons.NEW_LABEL,
                            on_click=lambda e: self._start_custom_session("not_started")
                        ),
                        ft.ElevatedButton(
                            text="ランダム学習",
                            icon=ft.icons.SHUFFLE,
                            on_click=lambda e: self._start_custom_session("all")
                        )
                    ], spacing=10)
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Start session button
        start_button = ft.Container(
            content=ft.ElevatedButton(
                text="学習開始",
                icon=ft.icons.PLAY_ARROW,
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.PRIMARY,
                    padding=ft.padding.all(15)
                ),
                on_click=self._start_custom_session_from_ui
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20)
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "フラッシュカード学習",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                mode_selection,
                side_selection,
                config_section,
                quick_start,
                start_button
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20)
        )
    
    def _create_study_interface(self, session: StudySession) -> ft.Container:
        """Create study interface"""
        
        # Progress bar
        progress = session.get_progress_info()
        self.progress_info = ft.Column([
            ft.ProgressBar(
                value=progress['current'] / progress['total'],
                color=ft.colors.PRIMARY
            ),
            ft.Text(
                f"{progress['current']} / {progress['total']} カード "
                f"(正解率: {progress['accuracy']:.1f}%)",
                size=14,
                text_align=ft.TextAlign.CENTER
            )
        ])
        
        # Flashcard display
        current_card = session.get_current_card()
        front_text = current_card.get_front_text(session.card_side) if current_card else ""
        
        self.flashcard_display = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Card type indicator
                    ft.Row([
                        ft.Icon(
                            ft.icons.TEXT_FIELDS if current_card and current_card.item_type == ItemType.WORD else ft.icons.CHAT,
                            color=ft.colors.PRIMARY
                        ),
                        ft.Text(
                            "単語" if current_card and current_card.item_type == ItemType.WORD else "フレーズ",
                            size=12,
                            color=ft.colors.GREY_700
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=20),
                    
                    # Main card content
                    ft.Container(
                        content=ft.Text(
                            front_text,
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        height=200,
                        alignment=ft.alignment.center
                    ),
                    
                    # Flip instruction
                    ft.Text(
                        "カードをクリックして答えを確認",
                        size=14,
                        color=ft.colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(30),
                on_click=self._flip_card
            ),
            elevation=5
        )
        
        # Session controls
        self.session_controls = ft.Row([
            ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                tooltip="前のカード",
                on_click=self._previous_card,
                disabled=not session.has_previous_card()
            ),
            ft.Container(width=20),
            ft.ElevatedButton(
                text="正解",
                icon=ft.icons.CHECK,
                style=ft.ButtonStyle(bgcolor=ft.colors.GREEN),
                on_click=lambda e: self._mark_result(True),
                disabled=not self.is_card_flipped
            ),
            ft.ElevatedButton(
                text="不正解",
                icon=ft.icons.CLOSE,
                style=ft.ButtonStyle(bgcolor=ft.colors.RED),
                on_click=lambda e: self._mark_result(False),
                disabled=not self.is_card_flipped
            ),
            ft.Container(width=20),
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="次のカード",
                on_click=self._next_card,
                disabled=not session.has_next_card()
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Session info
        session_info = ft.Row([
            ft.TextButton(
                text="セッション終了",
                icon=ft.icons.STOP,
                on_click=self._end_session
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Container(
            content=ft.Column([
                self.progress_info,
                ft.Container(height=20),
                self.flashcard_display,
                ft.Container(height=20),
                self.session_controls,
                ft.Container(height=10),
                session_info
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20)
        )
    
    def _start_review_session(self, e):
        """Start review session"""
        session = self.flashcard_manager.create_review_session()
        
        if not session.cards:
            self._show_dialog("復習項目なし", "復習が必要な項目がありません。")
            return
        
        self.current_session = session
        self.is_card_flipped = False
        self.card_start_time = time.time()
        
        # Switch to study interface
        self.main_container.content = self._create_study_interface(session)
        self.page.update()
    
    def _start_custom_session(self, status_filter: str):
        """Start custom session with specific status filter"""
        # Convert status filter
        status = None
        if status_filter == "not_started":
            status = LearningStatus.NOT_STARTED
        elif status_filter == "learning":
            status = LearningStatus.LEARNING
        elif status_filter == "mastered":
            status = LearningStatus.MASTERED
        
        session = self.flashcard_manager.create_session(
            mode=StudyMode.MIXED,
            card_side=CardSide.INDONESIAN,
            target_count=20,
            status_filter=status
        )
        
        if not session.cards:
            self._show_dialog("学習項目なし", "該当する学習項目がありません。")
            return
        
        self.current_session = session
        self.is_card_flipped = False
        self.card_start_time = time.time()
        
        # Switch to study interface
        self.main_container.content = self._create_study_interface(session)
        self.page.update()
    
    def _start_custom_session_from_ui(self, e):
        """Start session from UI configuration"""
        # Get UI values (this is simplified - in real implementation,
        # you'd get these from the dropdowns)
        session = self.flashcard_manager.create_session(
            mode=StudyMode.MIXED,
            card_side=CardSide.INDONESIAN,
            target_count=20
        )
        
        if not session.cards:
            self._show_dialog("学習項目なし", "学習項目がありません。まずファイルを分析してください。")
            return
        
        self.current_session = session
        self.is_card_flipped = False
        self.card_start_time = time.time()
        
        # Switch to study interface
        self.main_container.content = self._create_study_interface(session)
        self.page.update()
    
    def _flip_card(self, e):
        """Flip the current card"""
        if not self.current_session or self.is_card_flipped:
            return
        
        current_card = self.current_session.get_current_card()
        if not current_card:
            return
        
        # Show back side
        back_text = current_card.get_back_text(self.current_session.card_side)
        
        self.flashcard_display.content.content.controls[2].content.value = back_text
        self.flashcard_display.content.content.controls[2].content.color = ft.colors.PRIMARY
        self.flashcard_display.content.content.controls[3].value = "正解・不正解を選択してください"
        
        self.is_card_flipped = True
        
        # Enable result buttons
        self.session_controls.controls[2].disabled = False  # Correct button
        self.session_controls.controls[3].disabled = False  # Incorrect button
        
        self.page.update()
    
    def _mark_result(self, is_correct: bool):
        """Mark the result for current card"""
        if not self.current_session or not self.is_card_flipped:
            return
        
        current_card = self.current_session.get_current_card()
        if not current_card:
            return
        
        # Calculate response time
        response_time = time.time() - self.card_start_time if self.card_start_time else 0.0
        
        # Mark result
        self.flashcard_manager.mark_card_result(current_card, is_correct, response_time)
        
        # Auto-advance to next card after short delay
        if self.current_session.has_next_card():
            # Move to next card
            self._next_card(None)
        else:
            # Session completed
            self._complete_session()
    
    def _next_card(self, e):
        """Move to next card"""
        if not self.current_session:
            return
        
        if self.current_session.move_to_next():
            self._update_card_display()
        else:
            self._complete_session()
    
    def _previous_card(self, e):
        """Move to previous card"""
        if not self.current_session:
            return
        
        if self.current_session.move_to_previous():
            self._update_card_display()
    
    def _update_card_display(self):
        """Update card display for current card"""
        if not self.current_session:
            return
        
        current_card = self.current_session.get_current_card()
        if not current_card:
            return
        
        # Reset card state
        self.is_card_flipped = False
        self.card_start_time = time.time()
        
        # Update front text
        front_text = current_card.get_front_text(self.current_session.card_side)
        self.flashcard_display.content.content.controls[2].content.value = front_text
        self.flashcard_display.content.content.controls[2].content.color = ft.colors.BLACK
        self.flashcard_display.content.content.controls[3].value = "カードをクリックして答えを確認"
        
        # Update card type
        card_type = "単語" if current_card.item_type == ItemType.WORD else "フレーズ"
        self.flashcard_display.content.content.controls[0].controls[1].value = card_type
        
        # Update progress
        progress = self.current_session.get_progress_info()
        self.progress_info.controls[0].value = progress['current'] / progress['total']
        self.progress_info.controls[1].value = (
            f"{progress['current']} / {progress['total']} カード "
            f"(正解率: {progress['accuracy']:.1f}%)"
        )
        
        # Update navigation buttons
        self.session_controls.controls[0].disabled = not self.current_session.has_previous_card()
        self.session_controls.controls[2].disabled = True  # Correct button
        self.session_controls.controls[3].disabled = True  # Incorrect button
        self.session_controls.controls[4].disabled = not self.current_session.has_next_card()
        
        self.page.update()
    
    def _end_session(self, e):
        """End current session"""
        if not self.current_session:
            return
        
        # Show confirmation dialog
        def confirm_end(e):
            self._close_dialog()
            self._complete_session()
        
        def cancel_end(e):
            self._close_dialog()
        
        dialog = ft.AlertDialog(
            title=ft.Text("セッション終了確認"),
            content=ft.Text("現在のセッションを終了しますか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=cancel_end),
                ft.TextButton("終了", on_click=confirm_end)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _complete_session(self):
        """Complete current session"""
        if not self.current_session:
            return
        
        # End session and get summary
        summary = self.flashcard_manager.end_session()
        
        # Show results
        self._show_session_results(summary)
        
        # Reset state
        self.current_session = None
        
        # Return to setup
        self.main_container.content = self._create_session_setup()
        self.page.update()
    
    def _show_session_results(self, summary: Dict[str, any]):
        """Show session results dialog"""
        if not summary:
            return
        
        content = ft.Column([
            ft.Text(
                "学習セッション完了！",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREEN
            ),
            ft.Container(height=15),
            ft.Row([
                ft.Column([
                    ft.Text("学習カード数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(summary['cards_studied']), size=20, color=ft.colors.BLUE)
                ]),
                ft.Column([
                    ft.Text("正解数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(summary['correct_count']), size=20, color=ft.colors.GREEN)
                ]),
                ft.Column([
                    ft.Text("正解率", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{summary['accuracy']:.1f}%", size=20, color=ft.colors.PRIMARY)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Container(height=10),
            ft.Text(
                f"学習時間: {summary['total_time']:.1f}分",
                size=14,
                color=ft.colors.GREY_700
            )
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("セッション結果"),
            content=content,
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_dialog(self, title: str, message: str):
        """Show simple dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self):
        """Close current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def refresh(self):
        """Refresh view"""
        if not self.current_session:
            # Return to setup if no active session
            self.main_container.content = self._create_session_setup()
            self.page.update()
    
    def on_resize(self, width: int, height: int):
        """Handle resize"""
        pass
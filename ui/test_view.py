"""Enhanced test functionality view"""

import flet as ft
from typing import Optional, Dict, List
from datetime import datetime
import time

from data.database import Database
from config.settings import Settings
from core.test_engine import TestEngine, TestDifficulty, TestSession, TestQuestion, TestAnswer
from core.priority_manager import ItemType


class TestView(ft.UserControl):
    """Enhanced test functionality component"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Initialize test engine
        self.test_engine = TestEngine(database)
        
        # UI components
        self.main_container = None
        self.question_display = None
        self.answer_input = None
        self.timer_display = None
        self.progress_info = None
        
        # Test state
        self.current_session = None
        self.question_start_time = None
        
    def build(self):
        """Build test view UI"""
        
        # Create main container that switches between setup and test
        self.main_container = ft.Container(
            content=self._create_test_setup(),
            expand=True
        )
        
        return self.main_container
    
    def _create_test_setup(self) -> ft.Container:
        """Create test setup interface"""
        
        # Test type selection
        test_type_selection = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "テスト種類選択",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="typing", label="タイピングテスト（日→イ入力）"),
                            ft.Radio(value="typing_reverse", label="タイピングテスト（イ→日入力）"),
                            ft.Radio(value="multiple_choice", label="4択選択テスト")
                        ]),
                        value="typing"
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Difficulty selection
        difficulty_selection = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "難易度選択",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.RadioGroup(
                        content=ft.Column([
                            ft.Radio(value="easy", label="やさしい（基本単語）"),
                            ft.Radio(value="medium", label="ふつう（一般単語）"),
                            ft.Radio(value="hard", label="むずかしい（応用単語）")
                        ]),
                        value="medium"
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Test configuration
        config_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "テスト設定",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text("問題数", size=14, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=100,
                                value="10",
                                options=[
                                    ft.dropdown.Option("5", "5"),
                                    ft.dropdown.Option("10", "10"),
                                    ft.dropdown.Option("15", "15"),
                                    ft.dropdown.Option("20", "20")
                                ]
                            )
                        ]),
                        ft.Column([
                            ft.Text("種類", size=14, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=120,
                                value="all",
                                options=[
                                    ft.dropdown.Option("all", "すべて"),
                                    ft.dropdown.Option("word", "単語のみ"),
                                    ft.dropdown.Option("phrase", "フレーズのみ")
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
                        ])
                    ], spacing=20)
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Quick test options
        quick_tests = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "クイックテスト",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(
                            text="基本単語テスト",
                            icon=ft.icons.QUIZ,
                            on_click=lambda e: self._start_quick_test("word", "easy")
                        ),
                        ft.ElevatedButton(
                            text="ビジネステスト",
                            icon=ft.icons.BUSINESS,
                            on_click=lambda e: self._start_quick_test("business", "medium")
                        ),
                        ft.ElevatedButton(
                            text="総合テスト",
                            icon=ft.icons.ASSIGNMENT,
                            on_click=lambda e: self._start_quick_test("all", "medium")
                        )
                    ], spacing=10)
                ]),
                padding=ft.padding.all(20)
            )
        )
        
        # Start test button
        start_button = ft.Container(
            content=ft.ElevatedButton(
                text="テスト開始",
                icon=ft.icons.PLAY_ARROW,
                style=ft.ButtonStyle(
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.PRIMARY,
                    padding=ft.padding.all(15)
                ),
                on_click=self._start_custom_test
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20)
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "習得確認テスト",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                test_type_selection,
                difficulty_selection,
                config_section,
                quick_tests,
                start_button
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(20)
        )
    
    def _create_test_interface(self, session: TestSession) -> ft.Container:
        """Create test interface"""
        
        # Progress info
        progress = session.get_progress_info()
        self.progress_info = ft.Column([
            ft.ProgressBar(
                value=progress['current'] / progress['total'],
                color=ft.colors.PRIMARY
            ),
            ft.Text(
                f"問題 {progress['current']} / {progress['total']} "
                f"(正解率: {progress['accuracy']:.1f}%)",
                size=14,
                text_align=ft.TextAlign.CENTER
            )
        ])
        
        # Timer display
        self.timer_display = ft.Text(
            "30",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PRIMARY,
            text_align=ft.TextAlign.CENTER
        )
        
        # Question display
        current_question = session.get_current_question()
        question_text = current_question.question if current_question else ""
        
        self.question_display = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Question type indicator
                    ft.Text(
                        "タイピングテスト" if session.test_type.value == "typing" else "選択テスト",
                        size=14,
                        color=ft.colors.GREY_700,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=20),
                    
                    # Question text
                    ft.Container(
                        content=ft.Text(
                            question_text,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        height=100,
                        alignment=ft.alignment.center
                    ),
                    
                    # Timer
                    ft.Row([
                        ft.Icon(ft.icons.TIMER, color=ft.colors.PRIMARY),
                        self.timer_display
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(30)
            ),
            elevation=5
        )
        
        # Answer input/options
        if session.test_type.value == "typing":
            self.answer_input = self._create_typing_input()
        else:
            self.answer_input = self._create_multiple_choice_options(current_question)
        
        # Test controls
        test_controls = ft.Row([
            ft.ElevatedButton(
                text="スキップ",
                icon=ft.icons.SKIP_NEXT,
                on_click=self._skip_question
            ),
            ft.ElevatedButton(
                text="テスト終了",
                icon=ft.icons.STOP,
                style=ft.ButtonStyle(bgcolor=ft.colors.RED),
                on_click=self._end_test
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        
        return ft.Container(
            content=ft.Column([
                self.progress_info,
                ft.Container(height=20),
                self.question_display,
                ft.Container(height=20),
                self.answer_input,
                ft.Container(height=20),
                test_controls
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20)
        )
    
    def _create_typing_input(self) -> ft.Container:
        """Create typing input interface"""
        
        self.typing_field = ft.TextField(
            label="答えを入力してください",
            multiline=False,
            autofocus=True,
            on_submit=self._submit_typing_answer,
            width=400
        )
        
        submit_button = ft.ElevatedButton(
            text="回答",
            icon=ft.icons.SEND,
            on_click=self._submit_typing_answer
        )
        
        return ft.Container(
            content=ft.Column([
                self.typing_field,
                ft.Container(height=10),
                submit_button
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20)
        )
    
    def _create_multiple_choice_options(self, question: TestQuestion) -> ft.Container:
        """Create multiple choice options"""
        
        if not question or not question.options:
            return ft.Container()
        
        option_buttons = []
        for i, option in enumerate(question.options):
            button = ft.ElevatedButton(
                text=f"{chr(65 + i)}. {option}",
                width=400,
                height=60,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=16)
                ),
                on_click=lambda e, answer=option: self._submit_choice_answer(answer)
            )
            option_buttons.append(button)
        
        return ft.Container(
            content=ft.Column(
                option_buttons,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(20)
        )
    
    def _start_quick_test(self, category: str, difficulty: str):
        """Start quick test"""
        diff_map = {
            "easy": TestDifficulty.EASY,
            "medium": TestDifficulty.MEDIUM,
            "hard": TestDifficulty.HARD
        }
        
        cat_filter = None if category == "all" else category
        item_type = None
        if category == "word":
            item_type = ItemType.WORD
        elif category == "phrase":
            item_type = ItemType.PHRASE
        
        # Create typing test by default
        session = self.test_engine.create_typing_test(
            question_count=10,
            difficulty=diff_map[difficulty],
            item_type=item_type,
            category=cat_filter
        )
        
        if not session.questions:
            self._show_dialog("テスト項目なし", "該当するテスト項目がありません。")
            return
        
        self._start_test_session(session)
    
    def _start_custom_test(self, e):
        """Start custom test from UI configuration"""
        # This is simplified - in real implementation, get values from UI
        session = self.test_engine.create_typing_test(
            question_count=10,
            difficulty=TestDifficulty.MEDIUM
        )
        
        if not session.questions:
            self._show_dialog("テスト項目なし", "テスト項目がありません。まずファイルを分析してください。")
            return
        
        self._start_test_session(session)
    
    def _start_test_session(self, session: TestSession):
        """Start test session"""
        self.current_session = session
        self.question_start_time = time.time()
        
        # Switch to test interface
        self.main_container.content = self._create_test_interface(session)
        self.page.update()
        
        # Start timer
        self._start_question_timer()
    
    def _start_question_timer(self):
        """Start timer for current question"""
        if not self.current_session:
            return
        
        time_limit = self.current_session.time_limit or 30
        
        def update_timer():
            if not self.current_session:
                return
            
            elapsed = time.time() - self.question_start_time
            remaining = max(0, time_limit - elapsed)
            
            if self.timer_display:
                self.timer_display.value = str(int(remaining))
                self.timer_display.color = ft.colors.RED if remaining < 10 else ft.colors.PRIMARY
                self.page.update()
            
            if remaining <= 0:
                # Time up - auto skip
                self._skip_question(None)
            else:
                # Continue timer
                self.page.run_thread_safe(
                    lambda: self.page.add(ft.Container()),  # Dummy update
                    callback=lambda: self.page.after(1000, update_timer)
                )
        
        # Start timer
        self.page.after(1000, update_timer)
    
    def _submit_typing_answer(self, e):
        """Submit typing test answer"""
        if not self.current_session or not self.typing_field:
            return
        
        user_answer = self.typing_field.value.strip()
        if not user_answer:
            return
        
        # Calculate response time
        response_time = time.time() - self.question_start_time
        
        # Submit answer
        answer = self.test_engine.submit_answer(user_answer, response_time)
        
        # Show result briefly
        self._show_answer_result(answer)
        
        # Move to next question
        self._next_question()
    
    def _submit_choice_answer(self, selected_option: str):
        """Submit multiple choice answer"""
        if not self.current_session:
            return
        
        # Calculate response time
        response_time = time.time() - self.question_start_time
        
        # Submit answer
        answer = self.test_engine.submit_answer(selected_option, response_time)
        
        # Show result briefly
        self._show_answer_result(answer)
        
        # Move to next question
        self._next_question()
    
    def _show_answer_result(self, answer: TestAnswer):
        """Show answer result briefly"""
        current_question = self.current_session.get_current_question()
        if not current_question:
            return
        
        # Update question display with result
        result_text = "正解！" if answer.is_correct else f"不正解\n正解: {current_question.correct_answer}"
        result_color = ft.colors.GREEN if answer.is_correct else ft.colors.RED
        
        self.question_display.content.content.controls[2].content.value = result_text
        self.question_display.content.content.controls[2].content.color = result_color
        self.page.update()
        
        # Brief pause to show result
        time.sleep(1.5)
    
    def _skip_question(self, e):
        """Skip current question"""
        if not self.current_session:
            return
        
        # Submit empty answer
        response_time = time.time() - self.question_start_time
        self.test_engine.submit_answer("", response_time)
        
        # Move to next question
        self._next_question()
    
    def _next_question(self):
        """Move to next question"""
        if not self.current_session:
            return
        
        if self.current_session.move_to_next():
            # Update question display
            self._update_question_display()
            # Reset timer
            self.question_start_time = time.time()
            self._start_question_timer()
        else:
            # Test completed
            self._complete_test()
    
    def _update_question_display(self):
        """Update display for current question"""
        if not self.current_session:
            return
        
        current_question = self.current_session.get_current_question()
        if not current_question:
            return
        
        # Update question text
        self.question_display.content.content.controls[2].content.value = current_question.question
        self.question_display.content.content.controls[2].content.color = ft.colors.BLACK
        
        # Update progress
        progress = self.current_session.get_progress_info()
        self.progress_info.controls[0].value = progress['current'] / progress['total']
        self.progress_info.controls[1].value = (
            f"問題 {progress['current']} / {progress['total']} "
            f"(正解率: {progress['accuracy']:.1f}%)"
        )
        
        # Update answer input
        if self.current_session.test_type.value == "typing":
            self.typing_field.value = ""
            self.typing_field.focus()
        else:
            # Update multiple choice options
            new_options = self._create_multiple_choice_options(current_question)
            self.answer_input.content = new_options.content
        
        self.page.update()
    
    def _end_test(self, e):
        """End test early"""
        if not self.current_session:
            return
        
        # Show confirmation
        def confirm_end(e):
            self._close_dialog()
            self._complete_test()
        
        def cancel_end(e):
            self._close_dialog()
        
        dialog = ft.AlertDialog(
            title=ft.Text("テスト終了確認"),
            content=ft.Text("現在のテストを終了しますか？"),
            actions=[
                ft.TextButton("キャンセル", on_click=cancel_end),
                ft.TextButton("終了", on_click=confirm_end)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _complete_test(self):
        """Complete test and show results"""
        if not self.current_session:
            return
        
        # End test and get summary
        summary = self.test_engine.end_test()
        
        # Show results
        self._show_test_results(summary)
        
        # Reset state
        self.current_session = None
        
        # Return to setup
        self.main_container.content = self._create_test_setup()
        self.page.update()
    
    def _show_test_results(self, summary: Dict[str, any]):
        """Show test results dialog"""
        if not summary:
            return
        
        # Calculate grade
        accuracy = summary['accuracy']
        if accuracy >= 90:
            grade = "A"
            grade_color = ft.colors.GREEN
        elif accuracy >= 80:
            grade = "B"
            grade_color = ft.colors.BLUE
        elif accuracy >= 70:
            grade = "C"
            grade_color = ft.colors.ORANGE
        else:
            grade = "D"
            grade_color = ft.colors.RED
        
        content = ft.Column([
            ft.Text(
                "テスト完了！",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREEN
            ),
            ft.Container(height=10),
            
            # Grade
            ft.Row([
                ft.Text("評価:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(grade, size=32, weight=ft.FontWeight.BOLD, color=grade_color)
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=15),
            
            # Statistics
            ft.Row([
                ft.Column([
                    ft.Text("回答数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{summary['answered']}/{summary['total_questions']}", 
                           size=18, color=ft.colors.BLUE)
                ]),
                ft.Column([
                    ft.Text("正解数", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(str(summary['correct']), size=18, color=ft.colors.GREEN)
                ]),
                ft.Column([
                    ft.Text("正解率", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{summary['accuracy']:.1f}%", size=18, color=ft.colors.PRIMARY)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            
            ft.Container(height=10),
            ft.Text(
                f"平均回答時間: {summary['average_time']:.1f}秒",
                size=14,
                color=ft.colors.GREY_700
            )
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("テスト結果"),
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
            self.main_container.content = self._create_test_setup()
            self.page.update()
    
    def on_resize(self, width: int, height: int):
        """Handle resize"""
        pass
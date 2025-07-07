"""Tutorial/onboarding view for first-time users"""

import flet as ft
from typing import Callable, Optional
from config.settings import Settings


class TutorialView:
    """Interactive tutorial for new users"""
    
    def __init__(self, page: ft.Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.current_step = 0
        self.dialog = None
        self.on_close_callback = None
        
        # Tutorial steps
        self.steps = [
            {
                "title": "インドネシア語学習支援ツールへようこそ！",
                "content": "このツールは、インドネシア語のテキストファイルから効率的に学習教材を作成し、体系的な学習をサポートします。",
                "image": "tutorial_welcome.png"
            },
            {
                "title": "1. ファイル処理機能",
                "content": "テキストファイルを読み込んで語幹抽出・頻度分析を行います。複数ファイルの一括処理も可能です。",
                "image": "tutorial_file.png"
            },
            {
                "title": "2. 優先順位付き学習リスト",
                "content": "頻出度と重要度に基づいて自動的に学習優先順位を決定。効率的な学習順序を提案します。",
                "image": "tutorial_priority.png"
            },
            {
                "title": "3. フラッシュカード学習",
                "content": "単語とフレーズを効率的に記憶するためのフラッシュカード機能。習得状態を自動で追跡します。",
                "image": "tutorial_flashcard.png"
            },
            {
                "title": "4. テスト機能",
                "content": "タイピングテストと4択問題で学習効果を測定。正解率に基づいて習得判定を行います。",
                "image": "tutorial_test.png"
            },
            {
                "title": "5. 進捗管理",
                "content": "学習進捗を可視化し、モチベーションを維持。達成度をグラフで確認できます。",
                "image": "tutorial_progress.png"
            },
            {
                "title": "学習を始めましょう！",
                "content": "まずは「ファイル処理」タブからテキストファイルを読み込んで分析してみてください。従来の5倍の学習効率を実現しましょう！",
                "image": "tutorial_start.png"
            }
        ]
    
    def show(self, on_close: Optional[Callable] = None):
        """Show tutorial dialog"""
        self.on_close_callback = on_close
        self.current_step = 0
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("初回セットアップ"),
            content=self._create_step_content(),
            actions=[
                ft.TextButton("スキップ", on_click=self._skip_tutorial),
                ft.TextButton("戻る", on_click=self._previous_step),
                ft.TextButton("次へ", on_click=self._next_step),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        self._update_action_buttons()
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _create_step_content(self) -> ft.Container:
        """Create content for current step"""
        step = self.steps[self.current_step]
        
        # Step indicator
        step_indicator = ft.Row(
            [
                ft.Container(
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor=ft.colors.PRIMARY if i <= self.current_step else ft.colors.GREY_300,
                    content=ft.Text(
                        str(i + 1),
                        color=ft.colors.WHITE if i <= self.current_step else ft.colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                        size=12
                    ),
                    alignment=ft.alignment.center
                )
                for i in range(len(self.steps))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # Content
        content = ft.Column(
            [
                step_indicator,
                ft.Container(height=20),
                ft.Text(
                    step["title"],
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=10),
                ft.Text(
                    step["content"],
                    size=14,
                    text_align=ft.TextAlign.LEFT
                ),
                ft.Container(height=20),
                # Placeholder for image
                ft.Container(
                    width=300,
                    height=200,
                    border_radius=10,
                    bgcolor=ft.colors.GREY_100,
                    content=ft.Icon(
                        ft.icons.IMAGE,
                        size=50,
                        color=ft.colors.GREY_400
                    ),
                    alignment=ft.alignment.center
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        )
        
        return ft.Container(
            content=content,
            width=400,
            height=400,
            padding=ft.padding.all(20)
        )
    
    def _update_action_buttons(self):
        """Update action buttons based on current step"""
        if self.dialog is None:
            return
            
        # Update button states
        back_button = self.dialog.actions[1]
        next_button = self.dialog.actions[2]
        
        # Back button
        back_button.disabled = self.current_step == 0
        
        # Next button
        if self.current_step == len(self.steps) - 1:
            next_button.text = "完了"
        else:
            next_button.text = "次へ"
    
    def _skip_tutorial(self, e):
        """Skip tutorial"""
        self.close()
    
    def _previous_step(self, e):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_tutorial()
    
    def _next_step(self, e):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._update_tutorial()
        else:
            # Tutorial completed
            self.close()
    
    def _update_tutorial(self):
        """Update tutorial display"""
        if self.dialog:
            self.dialog.content = self._create_step_content()
            self._update_action_buttons()
            self.page.update()
    
    def close(self):
        """Close tutorial dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
            
        if self.on_close_callback:
            self.on_close_callback(None)
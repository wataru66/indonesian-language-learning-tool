"""Priority learning list view"""

import flet as ft
from typing import List, Optional
from datetime import datetime

from data.database import Database
from data.models import LearningStatus, Category
from config.settings import Settings
from core.priority_manager import PriorityManager, ItemType, PriorityItem


class PriorityListView(ft.UserControl):
    """Priority learning list component"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Initialize priority manager
        self.priority_manager = PriorityManager(database)
        
        # UI components
        self.filter_type = None
        self.filter_category = None
        self.filter_status = None
        self.items_list = None
        self.summary_cards = None
        
        # Data
        self.current_items = []
        
    def build(self):
        """Build priority list UI"""
        
        # Summary cards
        self.summary_cards = ft.Row(
            [
                self._create_summary_card("総アイテム数", "0", ft.colors.BLUE),
                self._create_summary_card("未学習", "0", ft.colors.ORANGE),
                self._create_summary_card("学習中", "0", ft.colors.GREEN),
                self._create_summary_card("習得済み", "0", ft.colors.GREY)
            ],
            spacing=10
        )
        
        # Filters section
        filters = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "フィルター",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Row([
                        # Item type filter
                        ft.Column([
                            ft.Text("種類", size=12, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=120,
                                value="all",
                                options=[
                                    ft.dropdown.Option("all", "すべて"),
                                    ft.dropdown.Option("word", "単語"),
                                    ft.dropdown.Option("phrase", "フレーズ")
                                ],
                                on_change=self._on_type_filter_change
                            )
                        ]),
                        
                        # Category filter
                        ft.Column([
                            ft.Text("カテゴリ", size=12, weight=ft.FontWeight.BOLD),
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
                                ],
                                on_change=self._on_category_filter_change
                            )
                        ]),
                        
                        # Status filter
                        ft.Column([
                            ft.Text("学習状態", size=12, weight=ft.FontWeight.BOLD),
                            ft.Dropdown(
                                width=120,
                                value="all",
                                options=[
                                    ft.dropdown.Option("all", "すべて"),
                                    ft.dropdown.Option("not_started", "未学習"),
                                    ft.dropdown.Option("learning", "学習中"),
                                    ft.dropdown.Option("mastered", "習得済み")
                                ],
                                on_change=self._on_status_filter_change
                            )
                        ]),
                        
                        # Refresh button
                        ft.ElevatedButton(
                            text="更新",
                            icon=ft.icons.REFRESH,
                            on_click=self._refresh_list
                        )
                    ], spacing=15)
                ]),
                padding=ft.padding.all(15)
            )
        )
        
        # Learning recommendations
        recommendations = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "今日の学習推奨",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        text="今日の学習セットを表示",
                        icon=ft.icons.TODAY,
                        on_click=self._show_daily_recommendations
                    )
                ]),
                padding=ft.padding.all(15)
            )
        )
        
        # Items list
        self.items_list = ft.ListView(
            expand=True,
            spacing=5,
            padding=ft.padding.all(10)
        )
        
        items_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "学習リスト（優先順位順）",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=self.items_list,
                        height=400,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5
                    )
                ]),
                padding=ft.padding.all(15)
            )
        )
        
        # Main layout
        return ft.Column([
            self.summary_cards,
            recommendations,
            filters,
            items_section
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def did_mount(self):
        """Called when component is mounted"""
        self._load_initial_data()
    
    def _create_summary_card(self, title: str, value: str, color) -> ft.Card:
        """Create summary card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=12, color=ft.colors.GREY_700),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(15),
                width=150
            )
        )
    
    def _load_initial_data(self):
        """Load initial data"""
        self._refresh_list(None)
    
    def _refresh_list(self, e):
        """Refresh priority list"""
        # Determine filters
        item_type = None
        if self.filter_type == "word":
            item_type = ItemType.WORD
        elif self.filter_type == "phrase":
            item_type = ItemType.PHRASE
        
        category = self.filter_category if self.filter_category != "all" else None
        
        status = None
        if self.filter_status == "not_started":
            status = LearningStatus.NOT_STARTED
        elif self.filter_status == "learning":
            status = LearningStatus.LEARNING
        elif self.filter_status == "mastered":
            status = LearningStatus.MASTERED
        
        # Get priority items
        self.current_items = self.priority_manager.get_priority_list(
            item_type=item_type,
            category=category,
            status_filter=status,
            limit=100  # Limit for performance
        )
        
        # Update UI
        self._update_summary_cards()
        self._update_items_list()
    
    def _update_summary_cards(self):
        """Update summary statistics"""
        if not self.summary_cards:
            return
        
        total = len(self.current_items)
        not_started = len([i for i in self.current_items if i.learning_status == LearningStatus.NOT_STARTED])
        learning = len([i for i in self.current_items if i.learning_status == LearningStatus.LEARNING])
        mastered = len([i for i in self.current_items if i.learning_status == LearningStatus.MASTERED])
        
        # Update card values
        self.summary_cards.controls[0].content.content.controls[1].value = str(total)
        self.summary_cards.controls[1].content.content.controls[1].value = str(not_started)
        self.summary_cards.controls[2].content.content.controls[1].value = str(learning)
        self.summary_cards.controls[3].content.content.controls[1].value = str(mastered)
        
        self.page.update()
    
    def _update_items_list(self):
        """Update items list display"""
        if not self.items_list:
            return
        
        self.items_list.controls.clear()
        
        for i, item in enumerate(self.current_items):
            # Create item tile
            item_tile = self._create_item_tile(item, i + 1)
            self.items_list.controls.append(item_tile)
        
        if not self.current_items:
            # Show empty state
            empty_state = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.INBOX, size=50, color=ft.colors.GREY_400),
                    ft.Text(
                        "該当するアイテムが見つかりません",
                        size=16,
                        color=ft.colors.GREY_600
                    ),
                    ft.Text(
                        "フィルターを変更するか、ファイルを分析してください",
                        size=12,
                        color=ft.colors.GREY_500
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(30),
                alignment=ft.alignment.center
            )
            self.items_list.controls.append(empty_state)
        
        self.page.update()
    
    def _create_item_tile(self, item: PriorityItem, rank: int) -> ft.Card:
        """Create item tile"""
        
        # Status color and icon
        status_colors = {
            LearningStatus.NOT_STARTED: ft.colors.ORANGE,
            LearningStatus.LEARNING: ft.colors.BLUE,
            LearningStatus.MASTERED: ft.colors.GREEN
        }
        
        status_icons = {
            LearningStatus.NOT_STARTED: ft.icons.CIRCLE_OUTLINED,
            LearningStatus.LEARNING: ft.icons.PLAY_CIRCLE_OUTLINE,
            LearningStatus.MASTERED: ft.icons.CHECK_CIRCLE
        }
        
        status_color = status_colors.get(item.learning_status, ft.colors.GREY)
        status_icon = status_icons.get(item.learning_status, ft.icons.HELP)
        
        # Item type icon
        type_icon = ft.icons.TEXT_FIELDS if item.item_type == ItemType.WORD else ft.icons.CHAT
        
        # Progress info
        progress_text = ""
        if item.review_count > 0:
            progress_text = f"正解率: {item.accuracy_rate:.1f}% ({item.review_count}回)"
        else:
            progress_text = "未学習"
        
        # Create tile
        tile = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    # Rank
                    ft.Container(
                        content=ft.Text(
                            str(rank),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.PRIMARY
                        ),
                        width=40,
                        alignment=ft.alignment.center
                    ),
                    
                    # Status icon
                    ft.Icon(status_icon, color=status_color),
                    
                    # Type icon
                    ft.Icon(type_icon, size=16, color=ft.colors.GREY_600),
                    
                    # Content
                    ft.Expanded(
                        child=ft.Column([
                            ft.Text(
                                item.content,
                                size=14,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                item.translation if item.translation else "翻訳なし",
                                size=12,
                                color=ft.colors.GREY_700
                            ),
                            ft.Text(
                                progress_text,
                                size=11,
                                color=ft.colors.GREY_600
                            )
                        ], spacing=2)
                    ),
                    
                    # Priority score
                    ft.Container(
                        content=ft.Text(
                            f"{item.learning_priority:.2f}",
                            size=12,
                            color=ft.colors.PRIMARY
                        ),
                        width=50,
                        alignment=ft.alignment.center
                    ),
                    
                    # Actions
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.SCHOOL,
                            tooltip="学習開始",
                            on_click=lambda e, item_id=item.id, item_type=item.item_type: 
                                self._start_learning(item_id, item_type)
                        ),
                        ft.IconButton(
                            icon=ft.icons.QUIZ,
                            tooltip="テスト",
                            on_click=lambda e, item_id=item.id, item_type=item.item_type: 
                                self._start_test(item_id, item_type)
                        )
                    ], spacing=0)
                    
                ], alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.all(10)
            )
        )
        
        return tile
    
    def _on_type_filter_change(self, e):
        """Handle type filter change"""
        self.filter_type = e.control.value
        self._refresh_list(None)
    
    def _on_category_filter_change(self, e):
        """Handle category filter change"""
        self.filter_category = e.control.value
        self._refresh_list(None)
    
    def _on_status_filter_change(self, e):
        """Handle status filter change"""
        self.filter_status = e.control.value
        self._refresh_list(None)
    
    def _show_daily_recommendations(self, e):
        """Show daily learning recommendations"""
        daily_goal = self.settings.daily_goal
        recommendations = self.priority_manager.get_learning_recommendations(
            daily_goal=daily_goal
        )
        
        # Create recommendations dialog
        content = ft.Column([
            ft.Text(
                f"今日の学習目標: {daily_goal}アイテム",
                size=16,
                weight=ft.FontWeight.BOLD
            ),
            ft.Container(height=10),
            
            # New items
            ft.Text("新規学習項目", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"{len(recommendations['new_items'])}個", size=12, color=ft.colors.ORANGE),
            ft.Container(height=5),
            
            # Review items
            ft.Text("復習項目", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"{len(recommendations['review_items'])}個", size=12, color=ft.colors.BLUE),
            ft.Container(height=5),
            
            # Struggling items
            ft.Text("重点強化項目", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"{len(recommendations['struggling_items'])}個", size=12, color=ft.colors.RED),
            ft.Container(height=15),
            
            ft.ElevatedButton(
                text="学習開始",
                icon=ft.icons.PLAY_ARROW,
                on_click=lambda e: self._start_daily_session(recommendations)
            )
        ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("今日の学習推奨"),
            content=content,
            actions=[
                ft.TextButton("閉じる", on_click=lambda e: self._close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _start_learning(self, item_id: int, item_type: ItemType):
        """Start learning specific item"""
        # Switch to flashcard tab with specific item
        if hasattr(self.page, 'main_window'):
            self.page.main_window.switch_to_tab('flashcard')
    
    def _start_test(self, item_id: int, item_type: ItemType):
        """Start test for specific item"""
        # Switch to test tab with specific item
        if hasattr(self.page, 'main_window'):
            self.page.main_window.switch_to_tab('test')
    
    def _start_daily_session(self, recommendations):
        """Start daily learning session"""
        self._close_dialog()
        # Switch to flashcard tab for daily session
        if hasattr(self.page, 'main_window'):
            self.page.main_window.switch_to_tab('flashcard')
    
    def _close_dialog(self):
        """Close dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def refresh(self):
        """Refresh view"""
        self._refresh_list(None)
    
    def on_resize(self, width: int, height: int):
        """Handle resize"""
        pass
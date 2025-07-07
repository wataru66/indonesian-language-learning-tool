"""Enhanced progress tracking and visualization view"""

import flet as ft
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import math

from data.database import Database
from data.models import LearningStatus
from config.settings import Settings
from core.priority_manager import PriorityManager


class ProgressView(ft.UserControl):
    """Enhanced progress tracking component"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Initialize managers
        self.priority_manager = PriorityManager(database)
        
        # UI components
        self.stats_cards = None
        self.charts_container = None
        self.achievements_section = None
        self.study_calendar = None
        
    def build(self):
        """Build progress view UI"""
        
        # Overall statistics cards
        self.stats_cards = self._create_stats_cards()
        
        # Charts and visualizations
        self.charts_container = self._create_charts_section()
        
        # Study calendar
        self.study_calendar = self._create_study_calendar()
        
        # Achievements and milestones
        self.achievements_section = self._create_achievements_section()
        
        # Category breakdown
        category_breakdown = self._create_category_breakdown()
        
        # Recent activity
        recent_activity = self._create_recent_activity()
        
        return ft.Column([
            ft.Text(
                "学習進捗管理",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            self.stats_cards,
            ft.Container(height=20),
            ft.Row([
                ft.Container(
                    content=self.charts_container,
                    width=600,
                    expand=True
                ),
                ft.Container(
                    content=self.achievements_section,
                    width=300
                )
            ], spacing=20),
            ft.Container(height=20),
            self.study_calendar,
            ft.Container(height=20),
            ft.Row([
                ft.Container(
                    content=category_breakdown,
                    expand=True
                ),
                ft.Container(
                    content=recent_activity,
                    expand=True
                )
            ], spacing=20)
        ], scroll=ft.ScrollMode.AUTO, spacing=0)
    
    def did_mount(self):
        """Called when component is mounted"""
        self._load_data()
    
    def _create_stats_cards(self) -> ft.Row:
        """Create statistics summary cards"""
        
        # Get learning statistics
        stats = self.database.get_learning_stats()
        
        # Calculate overall progress
        total_items = stats['total_words'] + stats['total_phrases']
        mastered_items = stats['words_mastered'] + stats['phrases_mastered']
        learning_items = stats['words_learning'] + stats['phrases_learning']
        
        mastery_rate = (mastered_items / max(total_items, 1)) * 100
        
        cards = ft.Row([
            self._create_stat_card(
                "総学習項目",
                str(total_items),
                ft.icons.LIBRARY_BOOKS,
                ft.colors.BLUE
            ),
            self._create_stat_card(
                "習得済み",
                f"{mastered_items} ({mastery_rate:.1f}%)",
                ft.icons.CHECK_CIRCLE,
                ft.colors.GREEN
            ),
            self._create_stat_card(
                "学習中",
                str(learning_items),
                ft.icons.PLAY_CIRCLE,
                ft.colors.ORANGE
            ),
            self._create_stat_card(
                "今日の目標",
                f"{self.settings.daily_goal}語",
                ft.icons.TODAY,
                ft.colors.PRIMARY
            )
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        return cards
    
    def _create_stat_card(self, title: str, value: str, icon, color) -> ft.Card:
        """Create individual statistics card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=24),
                        ft.Text(title, size=12, color=ft.colors.GREY_700)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=5),
                    ft.Text(
                        value,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(15),
                width=150,
                height=100
            )
        )
    
    def _create_charts_section(self) -> ft.Card:
        """Create charts and visualizations section"""
        
        # Progress chart (simplified representation)
        progress_chart = self._create_progress_chart()
        
        # Accuracy chart
        accuracy_chart = self._create_accuracy_chart()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "学習進捗グラフ",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Tabs(
                        selected_index=0,
                        tabs=[
                            ft.Tab(
                                text="習得進捗",
                                content=progress_chart
                            ),
                            ft.Tab(
                                text="正解率推移",
                                content=accuracy_chart
                            )
                        ]
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
    
    def _create_progress_chart(self) -> ft.Container:
        """Create progress chart (simplified)"""
        
        # Get learning statistics
        stats = self.database.get_learning_stats()
        
        # Calculate percentages
        total = stats['total_words'] + stats['total_phrases']
        if total == 0:
            return ft.Container(
                content=ft.Text("データがありません"),
                height=200,
                alignment=ft.alignment.center
            )
        
        mastered = (stats['words_mastered'] + stats['phrases_mastered']) / total * 100
        learning = (stats['words_learning'] + stats['phrases_learning']) / total * 100
        not_started = 100 - mastered - learning
        
        # Create simple bar chart representation
        return ft.Container(
            content=ft.Column([
                ft.Text("学習状態の分布", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                
                # Progress bars
                ft.Column([
                    # Mastered
                    ft.Row([
                        ft.Container(
                            content=ft.Text("習得済み", size=12),
                            width=80
                        ),
                        ft.Container(
                            content=ft.ProgressBar(
                                value=mastered/100,
                                color=ft.colors.GREEN,
                                height=20
                            ),
                            expand=True
                        ),
                        ft.Text(f"{mastered:.1f}%", size=12)
                    ]),
                    
                    # Learning
                    ft.Row([
                        ft.Container(
                            content=ft.Text("学習中", size=12),
                            width=80
                        ),
                        ft.Container(
                            content=ft.ProgressBar(
                                value=learning/100,
                                color=ft.colors.ORANGE,
                                height=20
                            ),
                            expand=True
                        ),
                        ft.Text(f"{learning:.1f}%", size=12)
                    ]),
                    
                    # Not started
                    ft.Row([
                        ft.Container(
                            content=ft.Text("未学習", size=12),
                            width=80
                        ),
                        ft.Container(
                            content=ft.ProgressBar(
                                value=not_started/100,
                                color=ft.colors.GREY,
                                height=20
                            ),
                            expand=True
                        ),
                        ft.Text(f"{not_started:.1f}%", size=12)
                    ])
                ], spacing=10)
            ]),
            height=200,
            padding=ft.padding.all(20)
        )
    
    def _create_accuracy_chart(self) -> ft.Container:
        """Create accuracy chart (simplified)"""
        
        # This would show accuracy trends over time
        # For now, showing a simple representation
        return ft.Container(
            content=ft.Column([
                ft.Text("正解率推移", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Icon(
                    ft.icons.TRENDING_UP,
                    size=80,
                    color=ft.colors.GREEN
                ),
                ft.Text(
                    "学習データが蓄積されると\n正解率の推移グラフが表示されます",
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                    color=ft.colors.GREY_600
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            height=200,
            alignment=ft.alignment.center
        )
    
    def _create_study_calendar(self) -> ft.Card:
        """Create study calendar"""
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "学習カレンダー",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    self._create_calendar_grid()
                ]),
                padding=ft.padding.all(20)
            )
        )
    
    def _create_calendar_grid(self) -> ft.Container:
        """Create calendar grid showing study days"""
        
        # Create a simple 7x5 grid for current month
        today = datetime.now()
        
        # Days of week header
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        header = ft.Row([
            ft.Container(
                content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD),
                width=40,
                height=30,
                alignment=ft.alignment.center
            ) for day in weekdays
        ])
        
        # Calendar days (simplified - just current week)
        calendar_rows = []
        for week in range(4):  # 4 weeks
            row_days = []
            for day in range(7):
                day_num = week * 7 + day + 1
                if day_num <= 31:  # Valid day
                    # Simulate study activity
                    has_activity = (day_num + week) % 3 == 0
                    
                    day_container = ft.Container(
                        content=ft.Text(
                            str(day_num),
                            size=10,
                            color=ft.colors.WHITE if has_activity else ft.colors.BLACK
                        ),
                        width=40,
                        height=30,
                        bgcolor=ft.colors.GREEN if has_activity else ft.colors.GREY_200,
                        border_radius=5,
                        alignment=ft.alignment.center
                    )
                else:
                    day_container = ft.Container(width=40, height=30)
                
                row_days.append(day_container)
            
            calendar_rows.append(ft.Row(row_days))
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(height=5),
                *calendar_rows,
                ft.Container(height=10),
                ft.Row([
                    ft.Container(
                        width=15,
                        height=15,
                        bgcolor=ft.colors.GREEN,
                        border_radius=3
                    ),
                    ft.Text("学習日", size=10),
                    ft.Container(width=20),
                    ft.Container(
                        width=15,
                        height=15,
                        bgcolor=ft.colors.GREY_200,
                        border_radius=3
                    ),
                    ft.Text("未学習", size=10)
                ], alignment=ft.MainAxisAlignment.CENTER)
            ]),
            padding=ft.padding.all(10)
        )
    
    def _create_achievements_section(self) -> ft.Card:
        """Create achievements and milestones section"""
        
        # Get current stats for achievements
        stats = self.database.get_learning_stats()
        total_mastered = stats['words_mastered'] + stats['phrases_mastered']
        
        # Define achievements
        achievements = [
            {"title": "学習開始", "description": "初回学習完了", "target": 1, "achieved": total_mastered >= 1},
            {"title": "10語習得", "description": "10語をマスター", "target": 10, "achieved": total_mastered >= 10},
            {"title": "50語習得", "description": "50語をマスター", "target": 50, "achieved": total_mastered >= 50},
            {"title": "100語習得", "description": "100語をマスター", "target": 100, "achieved": total_mastered >= 100},
            {"title": "500語習得", "description": "500語をマスター", "target": 500, "achieved": total_mastered >= 500}
        ]
        
        achievement_items = []
        for achievement in achievements:
            icon_color = ft.colors.GOLD if achievement["achieved"] else ft.colors.GREY_400
            text_color = ft.colors.BLACK if achievement["achieved"] else ft.colors.GREY_500
            
            item = ft.ListTile(
                leading=ft.Icon(
                    ft.icons.EMOJI_EVENTS if achievement["achieved"] else ft.icons.RADIO_BUTTON_UNCHECKED,
                    color=icon_color
                ),
                title=ft.Text(
                    achievement["title"],
                    color=text_color,
                    weight=ft.FontWeight.BOLD if achievement["achieved"] else ft.FontWeight.NORMAL
                ),
                subtitle=ft.Text(
                    achievement["description"],
                    color=text_color
                )
            )
            achievement_items.append(item)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "実績・マイルストーン",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Column(achievement_items, spacing=5)
                ]),
                padding=ft.padding.all(20)
            )
        )
    
    def _create_category_breakdown(self) -> ft.Card:
        """Create category-wise progress breakdown"""
        
        breakdown = self.priority_manager.get_category_breakdown()
        
        category_items = []
        for category, stats in breakdown.items():
            if stats['total'] > 0:
                progress_bar = ft.ProgressBar(
                    value=stats['mastery_rate'] / 100,
                    color=ft.colors.PRIMARY,
                    height=10
                )
                
                item = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                category.title(),
                                size=14,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                f"{stats['mastery_rate']:.1f}%",
                                size=12,
                                color=ft.colors.PRIMARY
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        progress_bar,
                        ft.Text(
                            f"習得: {stats['mastered']}/{stats['total']}",
                            size=10,
                            color=ft.colors.GREY_600
                        )
                    ], spacing=3),
                    padding=ft.padding.symmetric(vertical=5)
                )
                category_items.append(item)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "カテゴリ別進捗",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Column(category_items, spacing=5) if category_items else ft.Text(
                        "データがありません",
                        color=ft.colors.GREY_600
                    )
                ]),
                padding=ft.padding.all(20)
            )
        )
    
    def _create_recent_activity(self) -> ft.Card:
        """Create recent learning activity feed"""
        
        # This would show recent learning activities
        # For now, showing placeholder
        activities = [
            {"action": "フラッシュカード学習", "count": "20語", "time": "2時間前"},
            {"action": "タイピングテスト", "count": "正解率85%", "time": "昨日"},
            {"action": "新規学習", "count": "15語", "time": "2日前"},
            {"action": "復習セッション", "count": "30語", "time": "3日前"}
        ]
        
        activity_items = []
        for activity in activities:
            item = ft.ListTile(
                leading=ft.Icon(ft.icons.HISTORY, color=ft.colors.PRIMARY),
                title=ft.Text(activity["action"]),
                subtitle=ft.Text(activity["count"]),
                trailing=ft.Text(
                    activity["time"],
                    size=12,
                    color=ft.colors.GREY_600
                )
            )
            activity_items.append(item)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "最近の学習履歴",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Column(activity_items, spacing=5)
                ]),
                padding=ft.padding.all(20)
            )
        )
    
    def _load_data(self):
        """Load and refresh all data"""
        # This would trigger a full refresh of all components
        pass
    
    def refresh(self):
        """Refresh view with latest data"""
        # Update stats cards
        if self.stats_cards:
            new_stats = self._create_stats_cards()
            self.stats_cards.controls = new_stats.controls
        
        # Update charts
        if self.charts_container:
            new_charts = self._create_charts_section()
            self.charts_container.content = new_charts.content
        
        # Update achievements
        if self.achievements_section:
            new_achievements = self._create_achievements_section()
            self.achievements_section.content = new_achievements.content
        
        self.page.update()
    
    def on_resize(self, width: int, height: int):
        """Handle resize"""
        pass
"""Main application window"""

import flet as ft
from typing import List, Dict, Optional
from pathlib import Path

from data.database import Database
from config.settings import Settings
from ui.tutorial_view import TutorialView
from ui.help_view import HelpView
from ui.file_tab import FileTab
from ui.flashcard_view import FlashcardView
from ui.test_view import TestView
from ui.progress_view import ProgressView
from ui.settings_view import SettingsView


class MainWindow(ft.UserControl):
    """Main application window with tabbed interface"""
    
    def __init__(self, page: ft.Page, database: Database, settings: Settings):
        super().__init__()
        self.page = page
        self.database = database
        self.settings = settings
        
        # Apply theme
        self.settings.apply_theme(self.page)
        
        # Initialize components
        self.tutorial_view = None
        self.help_view = None
        self.tabs = None
        self.tab_contents = {}
        
        # Check if this is first run
        self.is_first_run = self._check_first_run()
        
    def build(self):
        """Build the main window UI"""
        # Create app bar
        self.app_bar = ft.AppBar(
            title=ft.Text("インドネシア語学習支援ツール v1.0"),
            center_title=True,
            actions=[
                ft.IconButton(
                    icon=ft.icons.HELP,
                    tooltip="ヘルプ",
                    on_click=self._show_help
                ),
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    tooltip="設定",
                    on_click=self._show_settings
                )
            ]
        )
        
        # Create tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="ファイル処理",
                    icon=ft.icons.FOLDER_OPEN,
                    content=self._create_file_tab()
                ),
                ft.Tab(
                    text="学習リスト",
                    icon=ft.icons.LIST,
                    content=self._create_learning_list_tab()
                ),
                ft.Tab(
                    text="フラッシュカード",
                    icon=ft.icons.STYLE,
                    content=self._create_flashcard_tab()
                ),
                ft.Tab(
                    text="テスト",
                    icon=ft.icons.QUIZ,
                    content=self._create_test_tab()
                ),
                ft.Tab(
                    text="進捗管理",
                    icon=ft.icons.ANALYTICS,
                    content=self._create_progress_tab()
                )
            ]
        )
        
        # Create main layout
        main_layout = ft.Column(
            [
                self.app_bar,
                ft.Container(
                    content=self.tabs,
                    expand=True,
                    padding=ft.padding.all(10)
                )
            ],
            spacing=0
        )
        
        # Show tutorial if first run
        if self.is_first_run:
            self._show_tutorial()
            
        return main_layout
    
    def _create_file_tab(self) -> ft.Container:
        """Create file processing tab"""
        file_tab = FileTab(self.page, self.database, self.settings)
        self.tab_contents['file'] = file_tab
        return ft.Container(
            content=file_tab,
            padding=ft.padding.all(10)
        )
    
    def _create_learning_list_tab(self) -> ft.Container:
        """Create learning list tab (priority list)"""
        from ui.priority_list_view import PriorityListView
        priority_view = PriorityListView(self.page, self.database, self.settings)
        self.tab_contents['learning_list'] = priority_view
        return ft.Container(
            content=priority_view,
            padding=ft.padding.all(10)
        )
    
    def _create_flashcard_tab(self) -> ft.Container:
        """Create flashcard tab"""
        flashcard_view = FlashcardView(self.page, self.database, self.settings)
        self.tab_contents['flashcard'] = flashcard_view
        return ft.Container(
            content=flashcard_view,
            padding=ft.padding.all(10)
        )
    
    def _create_test_tab(self) -> ft.Container:
        """Create test tab"""
        test_view = TestView(self.page, self.database, self.settings)
        self.tab_contents['test'] = test_view
        return ft.Container(
            content=test_view,
            padding=ft.padding.all(10)
        )
    
    def _create_progress_tab(self) -> ft.Container:
        """Create progress tab"""
        progress_view = ProgressView(self.page, self.database, self.settings)
        self.tab_contents['progress'] = progress_view
        return ft.Container(
            content=progress_view,
            padding=ft.padding.all(10)
        )
    
    def _check_first_run(self) -> bool:
        """Check if this is the first run of the application"""
        # Check if settings file exists and has first_run flag
        settings_path = Path("settings.json")
        if not settings_path.exists():
            return True
        
        # Check database for existing data
        try:
            stats = self.database.get_learning_stats()
            if stats['total_words'] == 0 and stats['total_phrases'] == 0:
                return True
        except:
            return True
        
        return False
    
    def _show_tutorial(self):
        """Show tutorial dialog"""
        def close_tutorial(e):
            self.tutorial_view.close()
            # Mark as not first run
            self.settings.save()
            
        self.tutorial_view = TutorialView(self.page, self.settings)
        self.tutorial_view.show(on_close=close_tutorial)
    
    def _show_help(self, e):
        """Show help dialog"""
        def close_help(e):
            self.help_view.close()
            
        self.help_view = HelpView(self.page, self.settings)
        self.help_view.show(on_close=close_help)
    
    def _show_settings(self, e):
        """Show settings dialog"""
        def close_settings(e):
            # Apply any changed settings
            self.settings.apply_theme(self.page)
            self.page.update()
            
        settings_view = SettingsView(self.page, self.settings)
        settings_view.show(on_close=close_settings)
    
    def on_resize(self, width: int, height: int):
        """Handle window resize"""
        # Update any size-dependent components
        for tab_content in self.tab_contents.values():
            if hasattr(tab_content, 'on_resize'):
                tab_content.on_resize(width, height)
    
    def switch_to_tab(self, tab_name: str):
        """Switch to specific tab"""
        tab_map = {
            'file': 0,
            'learning_list': 1,
            'flashcard': 2,
            'test': 3,
            'progress': 4
        }
        
        if tab_name in tab_map:
            self.tabs.selected_index = tab_map[tab_name]
            self.page.update()
    
    def refresh_all_tabs(self):
        """Refresh all tab contents"""
        for tab_content in self.tab_contents.values():
            if hasattr(tab_content, 'refresh'):
                tab_content.refresh()
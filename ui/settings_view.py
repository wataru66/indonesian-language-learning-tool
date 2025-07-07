"""Enhanced settings configuration view"""

import flet as ft
from typing import Callable, Optional
from config.settings import Settings


class SettingsView:
    """Enhanced settings configuration dialog"""
    
    def __init__(self, page: ft.Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.dialog = None
        self.on_close_callback = None
        
        # UI components
        self.theme_radio = None
        self.language_radio = None
        self.daily_goal_field = None
        self.difficulty_radio = None
        self.strictness_radio = None
        self.sound_switch = None
        self.notifications_switch = None
        
    def show(self, on_close: Optional[Callable] = None):
        """Show settings dialog"""
        self.on_close_callback = on_close
        
        # Create settings content
        settings_content = self._create_settings_content()
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("設定"),
            content=settings_content,
            actions=[
                ft.TextButton("キャンセル", on_click=self._cancel_settings),
                ft.TextButton("保存", on_click=self._save_settings),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _create_settings_content(self) -> ft.Container:
        """Create settings content with tabs"""
        
        # General settings tab
        general_tab = self._create_general_settings()
        
        # Learning settings tab
        learning_tab = self._create_learning_settings()
        
        # Display settings tab
        display_tab = self._create_display_settings()
        
        # Test settings tab
        test_tab = self._create_test_settings()
        
        # Create tabs
        settings_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="一般",
                    icon=ft.icons.SETTINGS,
                    content=general_tab
                ),
                ft.Tab(
                    text="学習",
                    icon=ft.icons.SCHOOL,
                    content=learning_tab
                ),
                ft.Tab(
                    text="表示",
                    icon=ft.icons.DISPLAY_SETTINGS,
                    content=display_tab
                ),
                ft.Tab(
                    text="テスト",
                    icon=ft.icons.QUIZ,
                    content=test_tab
                )
            ]
        )
        
        return ft.Container(
            content=settings_tabs,
            width=500,
            height=400,
            padding=ft.padding.all(10)
        )
    
    def _create_general_settings(self) -> ft.Container:
        """Create general settings tab"""
        
        # Theme selection
        self.theme_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="light", label="ライトモード"),
                ft.Radio(value="dark", label="ダークモード"),
                ft.Radio(value="auto", label="自動（システム設定に従う）")
            ]),
            value=self.settings.theme_mode
        )
        
        # Language selection
        self.language_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="ja", label="日本語"),
                ft.Radio(value="en", label="English")
            ]),
            value=self.settings.language
        )
        
        # Sound settings
        self.sound_switch = ft.Switch(
            label="効果音を有効にする",
            value=self.settings.sound_effects
        )
        
        self.notifications_switch = ft.Switch(
            label="通知を有効にする",
            value=self.settings.notifications_enabled
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("テーマ", size=16, weight=ft.FontWeight.BOLD),
                self.theme_radio,
                ft.Container(height=15),
                
                ft.Text("言語", size=16, weight=ft.FontWeight.BOLD),
                self.language_radio,
                ft.Container(height=15),
                
                ft.Text("音声・通知", size=16, weight=ft.FontWeight.BOLD),
                self.sound_switch,
                self.notifications_switch
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(15)
        )
    
    def _create_learning_settings(self) -> ft.Container:
        """Create learning settings tab"""
        
        # Daily goal
        self.daily_goal_field = ft.TextField(
            label="1日の学習目標（語数）",
            value=str(self.settings.daily_goal),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        # Review interval
        review_interval_field = ft.TextField(
            label="復習間隔（日）",
            value=str(self.settings.review_interval),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        # Auto play audio
        auto_audio_switch = ft.Switch(
            label="音声を自動再生する",
            value=self.settings.auto_play_audio
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("学習目標", size=16, weight=ft.FontWeight.BOLD),
                self.daily_goal_field,
                review_interval_field,
                ft.Container(height=15),
                
                ft.Text("音声設定", size=16, weight=ft.FontWeight.BOLD),
                auto_audio_switch,
                
                ft.Row([
                    ft.Text("音声速度:", size=14),
                    ft.Slider(
                        min=0.5,
                        max=2.0,
                        divisions=6,
                        value=self.settings.audio_speed,
                        label="{value}x",
                        width=200
                    )
                ])
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(15)
        )
    
    def _create_display_settings(self) -> ft.Container:
        """Create display settings tab"""
        
        # Font size
        font_size_slider = ft.Slider(
            min=10,
            max=20,
            divisions=10,
            value=self.settings.font_size,
            label="{value}px",
            width=300
        )
        
        # Show hints
        show_hints_switch = ft.Switch(
            label="ヒントを表示する",
            value=self.settings.show_hints
        )
        
        # Show romanization
        show_romanization_switch = ft.Switch(
            label="ローマ字表記を表示する",
            value=self.settings.show_romanization
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("フォント設定", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text("フォントサイズ:", size=14),
                    font_size_slider
                ]),
                ft.Container(height=15),
                
                ft.Text("表示オプション", size=16, weight=ft.FontWeight.BOLD),
                show_hints_switch,
                show_romanization_switch
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(15)
        )
    
    def _create_test_settings(self) -> ft.Container:
        """Create test settings tab"""
        
        # Difficulty selection
        self.difficulty_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="1", label="やさしい"),
                ft.Radio(value="2", label="ふつう"),
                ft.Radio(value="3", label="むずかしい")
            ]),
            value=str(self.settings.test_difficulty)
        )
        
        # Typing strictness
        self.strictness_radio = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="partial", label="部分一致（推奨）"),
                ft.Radio(value="exact", label="完全一致")
            ]),
            value=self.settings.typing_strictness
        )
        
        # Time limit
        time_limit_field = ft.TextField(
            label="制限時間（秒）",
            value=str(self.settings.test_time_limit),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("テスト難易度", size=16, weight=ft.FontWeight.BOLD),
                self.difficulty_radio,
                ft.Container(height=15),
                
                ft.Text("タイピングテスト設定", size=16, weight=ft.FontWeight.BOLD),
                self.strictness_radio,
                time_limit_field
            ], scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(15)
        )
    
    def _save_settings(self, e):
        """Save settings and close dialog"""
        try:
            # Update settings from UI
            self.settings.theme_mode = self.theme_radio.value
            self.settings.language = self.language_radio.value
            self.settings.sound_effects = self.sound_switch.value
            self.settings.notifications_enabled = self.notifications_switch.value
            
            # Learning settings
            if self.daily_goal_field.value.isdigit():
                self.settings.daily_goal = int(self.daily_goal_field.value)
            
            # Test settings
            if self.difficulty_radio.value:
                self.settings.test_difficulty = int(self.difficulty_radio.value)
            
            if self.strictness_radio.value:
                self.settings.typing_strictness = self.strictness_radio.value
            
            # Save to file
            self.settings.save()
            
            # Close dialog
            self.close()
            
            # Show success message
            self._show_message("設定を保存しました")
            
        except Exception as ex:
            self._show_message(f"設定の保存に失敗しました: {str(ex)}")
    
    def _cancel_settings(self, e):
        """Cancel settings changes"""
        self.close()
    
    def _show_message(self, message: str):
        """Show message to user"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=3000
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
    
    def close(self):
        """Close settings dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
            
        if self.on_close_callback:
            self.on_close_callback(None)
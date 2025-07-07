"""Application settings management"""

import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict
import flet as ft


@dataclass
class Settings:
    """Application settings"""
    # UI Settings
    theme_mode: str = "light"
    language: str = "ja"
    
    # Learning Settings  
    daily_goal: int = 20
    review_interval: int = 1  # days
    auto_play_audio: bool = False
    
    # Test Settings
    test_difficulty: int = 2  # 1-3
    typing_strictness: str = "partial"  # partial or exact
    test_time_limit: int = 30  # seconds
    
    # Display Settings
    font_size: int = 14
    show_romanization: bool = False
    show_hints: bool = True
    
    # Audio Settings
    audio_speed: float = 1.0
    audio_voice: str = "default"
    
    # Notification Settings
    notifications_enabled: bool = True
    sound_effects: bool = True
    
    # Data Settings
    backup_enabled: bool = True
    backup_interval: int = 7  # days
    
    # Advanced Settings
    debug_mode: bool = False
    
    def __init__(self, settings_file: str = "settings.json"):
        """Initialize settings from file"""
        self.settings_file = Path(settings_file)
        self.load()
        
    def load(self) -> None:
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                print(f"Error loading settings: {e}")
                
    def save(self) -> None:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'theme_mode': self.theme_mode,
            'language': self.language,
            'daily_goal': self.daily_goal,
            'review_interval': self.review_interval,
            'auto_play_audio': self.auto_play_audio,
            'test_difficulty': self.test_difficulty,
            'typing_strictness': self.typing_strictness,
            'test_time_limit': self.test_time_limit,
            'font_size': self.font_size,
            'show_romanization': self.show_romanization,
            'show_hints': self.show_hints,
            'audio_speed': self.audio_speed,
            'audio_voice': self.audio_voice,
            'notifications_enabled': self.notifications_enabled,
            'sound_effects': self.sound_effects,
            'backup_enabled': self.backup_enabled,
            'backup_interval': self.backup_interval,
            'debug_mode': self.debug_mode
        }
        
    def apply_theme(self, page: ft.Page) -> None:
        """Apply theme settings to page"""
        if self.theme_mode == "dark":
            page.theme_mode = ft.ThemeMode.DARK
        elif self.theme_mode == "light":
            page.theme_mode = ft.ThemeMode.LIGHT
        else:  # auto
            page.theme_mode = ft.ThemeMode.SYSTEM
            
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme-specific colors"""
        if self.theme_mode == "dark":
            return {
                'primary': '#BB86FC',
                'secondary': '#03DAC6',
                'background': '#121212',
                'surface': '#1E1E1E',
                'error': '#CF6679',
                'on_primary': '#000000',
                'on_secondary': '#000000',
                'on_background': '#FFFFFF',
                'on_surface': '#FFFFFF',
                'on_error': '#000000',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'info': '#2196F3'
            }
        else:  # light theme
            return {
                'primary': '#6200EE',
                'secondary': '#03DAC6',
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'error': '#B00020',
                'on_primary': '#FFFFFF',
                'on_secondary': '#000000',
                'on_background': '#000000',
                'on_surface': '#000000',
                'on_error': '#FFFFFF',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'info': '#2196F3'
            }
            
    def get_font_size(self, size_type: str = "normal") -> int:
        """Get font size based on type and settings"""
        base_size = self.font_size
        
        sizes = {
            'tiny': base_size - 4,
            'small': base_size - 2,
            'normal': base_size,
            'large': base_size + 2,
            'huge': base_size + 6,
            'title': base_size + 8,
            'heading': base_size + 12
        }
        
        return sizes.get(size_type, base_size)
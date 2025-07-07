"""Data models for Indonesian Language Learning Application"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LearningStatus(Enum):
    """Learning status enum"""
    NOT_STARTED = "not_started"
    LEARNING = "learning"
    MASTERED = "mastered"


class TestType(Enum):
    """Test type enum"""
    TYPING = "typing"
    MULTIPLE_CHOICE = "multiple_choice"


class Category(Enum):
    """Word/Phrase category enum"""
    GENERAL = "general"
    BUSINESS = "business"
    MEETING = "meeting"
    PRODUCTION = "production"
    QUALITY = "quality"
    SAFETY = "safety"
    TECHNICAL = "technical"
    DAILY = "daily"


@dataclass
class Word:
    """Word model"""
    id: Optional[int] = None
    indonesian: str = ""
    japanese: str = ""
    stem: str = ""
    category: Category = Category.GENERAL
    frequency: int = 0
    priority: float = 0.0
    difficulty: int = 1  # 1-5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_priority(self) -> float:
        """Calculate priority based on frequency and difficulty"""
        # Higher frequency and lower difficulty = higher priority
        return (self.frequency * 100) / (self.difficulty + 1)


@dataclass
class Phrase:
    """Phrase model"""
    id: Optional[int] = None
    indonesian: str = ""
    japanese: str = ""
    category: Category = Category.GENERAL
    frequency: int = 0
    priority: float = 0.0
    difficulty: int = 1  # 1-5
    word_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_priority(self) -> float:
        """Calculate priority based on frequency and difficulty"""
        return (self.frequency * 100) / (self.difficulty + 1)


@dataclass
class LearningProgress:
    """Learning progress model"""
    id: Optional[int] = None
    user_id: int = 1  # Default user
    item_type: str = "word"  # "word" or "phrase"
    item_id: int = 0
    status: LearningStatus = LearningStatus.NOT_STARTED
    learning_started_at: Optional[datetime] = None
    mastered_at: Optional[datetime] = None
    last_reviewed_at: Optional[datetime] = None
    correct_count: int = 0
    incorrect_count: int = 0
    consecutive_correct: int = 0
    accuracy_rate: float = 0.0
    review_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def calculate_accuracy(self) -> float:
        """Calculate accuracy rate"""
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0.0
        return (self.correct_count / total) * 100
    
    def update_status(self) -> None:
        """Update learning status based on performance"""
        if self.consecutive_correct >= 3:
            self.status = LearningStatus.MASTERED
            self.mastered_at = datetime.now()
        elif self.correct_count > 0 or self.incorrect_count > 0:
            self.status = LearningStatus.LEARNING
            if self.learning_started_at is None:
                self.learning_started_at = datetime.now()


@dataclass
class TestResult:
    """Test result model"""
    id: Optional[int] = None
    user_id: int = 1
    test_type: TestType = TestType.MULTIPLE_CHOICE
    item_type: str = "word"  # "word" or "phrase"
    item_id: int = 0
    question: str = ""
    correct_answer: str = ""
    user_answer: str = ""
    is_correct: bool = False
    response_time: float = 0.0  # seconds
    tested_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class StudySession:
    """Study session model"""
    id: Optional[int] = None
    user_id: int = 1
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    cards_studied: int = 0
    tests_taken: int = 0
    correct_answers: int = 0
    total_time: float = 0.0  # minutes
    created_at: Optional[datetime] = None


@dataclass
class UserSettings:
    """User settings model"""
    id: Optional[int] = None
    user_id: int = 1
    theme_mode: str = "light"
    daily_goal: int = 20  # cards per day
    test_difficulty: int = 2  # 1-3
    typing_strictness: str = "partial"  # "partial" or "exact"
    sound_enabled: bool = True
    notification_enabled: bool = True
    language: str = "ja"  # "ja" or "en"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
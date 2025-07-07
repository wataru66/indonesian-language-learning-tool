"""Flashcard learning system with spaced repetition"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random

from data.models import Word, Phrase, LearningProgress, LearningStatus
from data.database import Database
from core.priority_manager import ItemType, PriorityItem


class CardSide(Enum):
    """Which side of the card is shown"""
    INDONESIAN = "indonesian"
    JAPANESE = "japanese"


class StudyMode(Enum):
    """Study mode type"""
    WORD_ONLY = "word_only"
    PHRASE_ONLY = "phrase_only"
    MIXED = "mixed"


@dataclass
class FlashCard:
    """Individual flashcard"""
    id: int
    item_type: ItemType
    indonesian: str
    japanese: str
    category: str
    difficulty: int
    learning_status: LearningStatus
    accuracy_rate: float
    consecutive_correct: int
    last_reviewed: Optional[datetime] = None
    
    def get_front_text(self, card_side: CardSide) -> str:
        """Get text for front of card"""
        if card_side == CardSide.INDONESIAN:
            return self.indonesian
        else:
            return self.japanese
    
    def get_back_text(self, card_side: CardSide) -> str:
        """Get text for back of card"""
        if card_side == CardSide.INDONESIAN:
            return self.japanese
        else:
            return self.indonesian


@dataclass
class StudySession:
    """Study session configuration and state"""
    mode: StudyMode
    card_side: CardSide
    target_count: int
    cards: List[FlashCard]
    current_index: int = 0
    cards_studied: int = 0
    correct_count: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    def get_current_card(self) -> Optional[FlashCard]:
        """Get current card"""
        if 0 <= self.current_index < len(self.cards):
            return self.cards[self.current_index]
        return None
    
    def has_next_card(self) -> bool:
        """Check if there are more cards"""
        return self.current_index < len(self.cards) - 1
    
    def has_previous_card(self) -> bool:
        """Check if we can go back"""
        return self.current_index > 0
    
    def move_to_next(self) -> bool:
        """Move to next card"""
        if self.has_next_card():
            self.current_index += 1
            return True
        return False
    
    def move_to_previous(self) -> bool:
        """Move to previous card"""
        if self.has_previous_card():
            self.current_index -= 1
            return True
        return False
    
    def get_progress_info(self) -> Dict[str, any]:
        """Get session progress information"""
        return {
            'current': self.current_index + 1,
            'total': len(self.cards),
            'studied': self.cards_studied,
            'correct': self.correct_count,
            'accuracy': (self.correct_count / max(self.cards_studied, 1)) * 100,
            'remaining': len(self.cards) - self.current_index - 1
        }


class FlashcardManager:
    """Manages flashcard learning sessions"""
    
    def __init__(self, database: Database):
        self.database = database
        self.current_session = None
        
    def create_session(self, 
                      mode: StudyMode,
                      card_side: CardSide = CardSide.INDONESIAN,
                      target_count: int = 20,
                      category_filter: Optional[str] = None,
                      status_filter: Optional[LearningStatus] = None,
                      priority_items: Optional[List[PriorityItem]] = None) -> StudySession:
        """Create new study session"""
        
        # Get cards based on filters
        if priority_items:
            cards = self._convert_priority_items_to_cards(priority_items)
        else:
            cards = self._get_cards_by_filters(mode, category_filter, status_filter)
        
        # Shuffle cards for variety
        random.shuffle(cards)
        
        # Limit to target count
        if len(cards) > target_count:
            cards = cards[:target_count]
        
        # Create session
        session = StudySession(
            mode=mode,
            card_side=card_side,
            target_count=target_count,
            cards=cards,
            started_at=datetime.now()
        )
        
        self.current_session = session
        return session
    
    def create_review_session(self, user_id: int = 1) -> StudySession:
        """Create session for items that need review"""
        
        # Get items that need review (low accuracy or not reviewed recently)
        cards = []
        
        # Get words that need review
        words = self.database.get_all_words()
        for word in words:
            progress = self.database.get_or_create_progress(user_id, "word", word.id)
            if self._needs_review(progress):
                card = self._create_flashcard_from_word(word, progress)
                cards.append(card)
        
        # Get phrases that need review
        phrases = self.database.get_all_phrases()
        for phrase in phrases:
            progress = self.database.get_or_create_progress(user_id, "phrase", phrase.id)
            if self._needs_review(progress):
                card = self._create_flashcard_from_phrase(phrase, progress)
                cards.append(card)
        
        # Sort by review priority (worse performance first)
        cards.sort(key=lambda c: (c.accuracy_rate, c.consecutive_correct))
        
        # Limit to reasonable number
        cards = cards[:30]
        
        session = StudySession(
            mode=StudyMode.MIXED,
            card_side=CardSide.INDONESIAN,
            target_count=len(cards),
            cards=cards,
            started_at=datetime.now()
        )
        
        self.current_session = session
        return session
    
    def mark_card_result(self, card: FlashCard, is_correct: bool, 
                        response_time: float = 0.0) -> None:
        """Mark card result and update progress"""
        
        # Update session stats
        if self.current_session:
            self.current_session.cards_studied += 1
            if is_correct:
                self.current_session.correct_count += 1
        
        # Update database progress
        progress = self.database.get_or_create_progress(
            1, card.item_type.value, card.id
        )
        
        if is_correct:
            progress.correct_count += 1
            progress.consecutive_correct += 1
        else:
            progress.incorrect_count += 1
            progress.consecutive_correct = 0
        
        progress.last_reviewed_at = datetime.now()
        progress.review_count += 1
        
        # Update learning status based on performance
        progress.update_status()
        
        # Save to database
        self.database.update_progress(progress)
    
    def end_session(self) -> Optional[Dict[str, any]]:
        """End current session and return summary"""
        if not self.current_session:
            return None
        
        self.current_session.ended_at = datetime.now()
        
        # Calculate session summary
        total_time = (self.current_session.ended_at - 
                     self.current_session.started_at).total_seconds() / 60.0  # minutes
        
        summary = {
            'cards_studied': self.current_session.cards_studied,
            'correct_count': self.current_session.correct_count,
            'total_cards': len(self.current_session.cards),
            'accuracy': (self.current_session.correct_count / 
                        max(self.current_session.cards_studied, 1)) * 100,
            'total_time': total_time,
            'started_at': self.current_session.started_at,
            'ended_at': self.current_session.ended_at
        }
        
        # Save session to database
        self._save_session_summary(summary)
        
        # Clear current session
        self.current_session = None
        
        return summary
    
    def get_current_session(self) -> Optional[StudySession]:
        """Get current active session"""
        return self.current_session
    
    def _convert_priority_items_to_cards(self, items: List[PriorityItem]) -> List[FlashCard]:
        """Convert priority items to flashcards"""
        cards = []
        
        for item in items:
            card = FlashCard(
                id=item.id,
                item_type=item.item_type,
                indonesian=item.content,
                japanese=item.translation,
                category=item.category,
                difficulty=item.difficulty,
                learning_status=item.learning_status,
                accuracy_rate=item.accuracy_rate,
                consecutive_correct=item.consecutive_correct,
                last_reviewed=datetime.fromisoformat(item.last_reviewed) if item.last_reviewed else None
            )
            cards.append(card)
        
        return cards
    
    def _get_cards_by_filters(self, 
                             mode: StudyMode,
                             category_filter: Optional[str],
                             status_filter: Optional[LearningStatus]) -> List[FlashCard]:
        """Get cards based on filters"""
        cards = []
        
        # Get words if needed
        if mode in [StudyMode.WORD_ONLY, StudyMode.MIXED]:
            words = self.database.get_all_words(order_by="priority")
            for word in words:
                if category_filter and word.category.value != category_filter:
                    continue
                
                progress = self.database.get_or_create_progress(1, "word", word.id)
                if status_filter and progress.status != status_filter:
                    continue
                
                card = self._create_flashcard_from_word(word, progress)
                cards.append(card)
        
        # Get phrases if needed
        if mode in [StudyMode.PHRASE_ONLY, StudyMode.MIXED]:
            phrases = self.database.get_all_phrases(order_by="priority")
            for phrase in phrases:
                if category_filter and phrase.category.value != category_filter:
                    continue
                
                progress = self.database.get_or_create_progress(1, "phrase", phrase.id)
                if status_filter and progress.status != status_filter:
                    continue
                
                card = self._create_flashcard_from_phrase(phrase, progress)
                cards.append(card)
        
        return cards
    
    def _create_flashcard_from_word(self, word: Word, progress: LearningProgress) -> FlashCard:
        """Create flashcard from word and progress"""
        return FlashCard(
            id=word.id,
            item_type=ItemType.WORD,
            indonesian=word.indonesian,
            japanese=word.japanese,
            category=word.category.value,
            difficulty=word.difficulty,
            learning_status=progress.status,
            accuracy_rate=progress.accuracy_rate,
            consecutive_correct=progress.consecutive_correct,
            last_reviewed=progress.last_reviewed_at
        )
    
    def _create_flashcard_from_phrase(self, phrase: Phrase, progress: LearningProgress) -> FlashCard:
        """Create flashcard from phrase and progress"""
        return FlashCard(
            id=phrase.id,
            item_type=ItemType.PHRASE,
            indonesian=phrase.indonesian,
            japanese=phrase.japanese,
            category=phrase.category.value,
            difficulty=phrase.difficulty,
            learning_status=progress.status,
            accuracy_rate=progress.accuracy_rate,
            consecutive_correct=progress.consecutive_correct,
            last_reviewed=progress.last_reviewed_at
        )
    
    def _needs_review(self, progress: LearningProgress) -> bool:
        """Check if item needs review"""
        
        # Never reviewed - needs review
        if progress.review_count == 0:
            return True
        
        # Low accuracy - needs review
        if progress.accuracy_rate < 70:
            return True
        
        # Not reviewed recently - needs review
        if progress.last_reviewed_at:
            days_since_review = (datetime.now() - progress.last_reviewed_at).days
            if days_since_review > 3:  # More than 3 days
                return True
        
        # Learning status but low consecutive correct
        if (progress.status == LearningStatus.LEARNING and 
            progress.consecutive_correct < 2):
            return True
        
        return False
    
    def _save_session_summary(self, summary: Dict[str, any]) -> None:
        """Save session summary to database"""
        # This would save to study_sessions table
        # Implementation depends on database schema
        pass
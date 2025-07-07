"""Priority management system for learning items"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from data.models import Word, Phrase, LearningProgress, LearningStatus
from data.database import Database


class ItemType(Enum):
    """Learning item type"""
    WORD = "word"
    PHRASE = "phrase"


@dataclass
class PriorityItem:
    """Priority learning item"""
    id: int
    item_type: ItemType
    content: str  # Indonesian text
    translation: str  # Japanese translation
    category: str
    frequency: int
    base_priority: float
    learning_priority: float  # Adjusted priority based on learning progress
    difficulty: int
    learning_status: LearningStatus
    accuracy_rate: float
    last_reviewed: Optional[str] = None
    consecutive_correct: int = 0
    review_count: int = 0


class PriorityManager:
    """Manages learning priority calculation and item sorting"""
    
    def __init__(self, database: Database):
        self.database = database
        
        # Priority calculation weights
        self.weights = {
            'frequency': 0.4,      # How often word appears
            'difficulty': 0.2,     # Difficulty level (inverse)
            'learning_status': 0.3, # Learning progress
            'accuracy': 0.1        # User's accuracy with this item
        }
        
        # Status multipliers
        self.status_multipliers = {
            LearningStatus.NOT_STARTED: 1.0,   # High priority for new items
            LearningStatus.LEARNING: 1.2,      # Higher priority for items being learned
            LearningStatus.MASTERED: 0.3       # Lower priority for mastered items
        }
        
    def get_priority_list(self, 
                         item_type: Optional[ItemType] = None,
                         category: Optional[str] = None,
                         status_filter: Optional[LearningStatus] = None,
                         limit: Optional[int] = None) -> List[PriorityItem]:
        """Get prioritized learning list"""
        
        priority_items = []
        
        # Get words if requested
        if item_type is None or item_type == ItemType.WORD:
            words = self.database.get_all_words(order_by="frequency")
            for word in words:
                if category and word.category.value != category:
                    continue
                    
                progress = self.database.get_or_create_progress(1, "word", word.id)
                
                if status_filter and progress.status != status_filter:
                    continue
                
                priority_item = self._create_priority_item(word, progress, ItemType.WORD)
                priority_items.append(priority_item)
        
        # Get phrases if requested
        if item_type is None or item_type == ItemType.PHRASE:
            phrases = self.database.get_all_phrases(order_by="frequency")
            for phrase in phrases:
                if category and phrase.category.value != category:
                    continue
                    
                progress = self.database.get_or_create_progress(1, "phrase", phrase.id)
                
                if status_filter and progress.status != status_filter:
                    continue
                
                priority_item = self._create_priority_item(phrase, progress, ItemType.PHRASE)
                priority_items.append(priority_item)
        
        # Sort by learning priority
        priority_items.sort(key=lambda x: x.learning_priority, reverse=True)
        
        # Apply limit
        if limit:
            priority_items = priority_items[:limit]
        
        return priority_items
    
    def _create_priority_item(self, item, progress: LearningProgress, 
                            item_type: ItemType) -> PriorityItem:
        """Create priority item from word/phrase and progress"""
        
        # Calculate learning-adjusted priority
        learning_priority = self._calculate_learning_priority(item, progress)
        
        return PriorityItem(
            id=item.id,
            item_type=item_type,
            content=item.indonesian,
            translation=item.japanese,
            category=item.category.value,
            frequency=item.frequency,
            base_priority=item.priority,
            learning_priority=learning_priority,
            difficulty=item.difficulty,
            learning_status=progress.status,
            accuracy_rate=progress.accuracy_rate,
            last_reviewed=progress.last_reviewed_at.isoformat() if progress.last_reviewed_at else None,
            consecutive_correct=progress.consecutive_correct,
            review_count=progress.review_count
        )
    
    def _calculate_learning_priority(self, item, progress: LearningProgress) -> float:
        """Calculate learning-adjusted priority score"""
        
        # Base priority components
        frequency_score = min(item.frequency / 10.0, 10.0)  # Normalize to 0-10
        difficulty_score = (6 - item.difficulty) / 5.0  # Inverse difficulty (easier = higher)
        
        # Learning status adjustment
        status_multiplier = self.status_multipliers.get(progress.status, 1.0)
        
        # Accuracy adjustment (lower accuracy = higher priority)
        accuracy_adjustment = 1.0
        if progress.review_count > 0:
            if progress.accuracy_rate < 50:
                accuracy_adjustment = 1.5  # Boost priority for struggling items
            elif progress.accuracy_rate > 80:
                accuracy_adjustment = 0.7  # Lower priority for well-known items
        
        # Time since last review (items not reviewed recently get boost)
        time_boost = 1.0
        if progress.last_reviewed_at:
            # Simple time boost - items not reviewed get slight priority boost
            time_boost = 1.1
        
        # Calculate weighted score
        priority = (
            frequency_score * self.weights['frequency'] +
            difficulty_score * self.weights['difficulty'] +
            status_multiplier * self.weights['learning_status'] +
            accuracy_adjustment * self.weights['accuracy']
        ) * time_boost
        
        return priority
    
    def get_learning_recommendations(self, user_id: int = 1, 
                                   daily_goal: int = 20) -> Dict[str, List[PriorityItem]]:
        """Get learning recommendations for today"""
        
        recommendations = {
            'new_items': [],
            'review_items': [],
            'struggling_items': []
        }
        
        # Get items that need review (learning status)
        review_items = self.get_priority_list(
            status_filter=LearningStatus.LEARNING,
            limit=daily_goal // 2
        )
        recommendations['review_items'] = review_items
        
        # Get struggling items (low accuracy)
        all_learning = self.get_priority_list(status_filter=LearningStatus.LEARNING)
        struggling = [item for item in all_learning if item.accuracy_rate < 60]
        struggling.sort(key=lambda x: x.accuracy_rate)  # Worst first
        recommendations['struggling_items'] = struggling[:5]
        
        # Get new items to learn
        remaining_goal = daily_goal - len(review_items)
        if remaining_goal > 0:
            new_items = self.get_priority_list(
                status_filter=LearningStatus.NOT_STARTED,
                limit=remaining_goal
            )
            recommendations['new_items'] = new_items
        
        return recommendations
    
    def get_category_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get learning progress breakdown by category"""
        
        breakdown = {}
        
        # Get all categories
        words = self.database.get_all_words()
        phrases = self.database.get_all_phrases()
        
        all_categories = set()
        for item in words + phrases:
            all_categories.add(item.category.value)
        
        # Calculate stats for each category
        for category in all_categories:
            category_stats = {
                'total': 0,
                'not_started': 0,
                'learning': 0,
                'mastered': 0,
                'mastery_rate': 0.0
            }
            
            # Count words in this category
            category_words = [w for w in words if w.category.value == category]
            category_phrases = [p for p in phrases if p.category.value == category]
            
            category_stats['total'] = len(category_words) + len(category_phrases)
            
            # Count learning status
            for item in category_words:
                progress = self.database.get_or_create_progress(1, "word", item.id)
                category_stats[progress.status.value] += 1
            
            for item in category_phrases:
                progress = self.database.get_or_create_progress(1, "phrase", item.id)
                category_stats[progress.status.value] += 1
            
            # Calculate mastery rate
            if category_stats['total'] > 0:
                category_stats['mastery_rate'] = (
                    category_stats['mastered'] / category_stats['total'] * 100
                )
            
            breakdown[category] = category_stats
        
        return breakdown
    
    def update_item_priority(self, item_id: int, item_type: ItemType, 
                           new_priority: float) -> bool:
        """Manually update item priority"""
        
        try:
            if item_type == ItemType.WORD:
                word = self.database.get_word(item_id)
                if word:
                    word.priority = new_priority
                    return self.database.update_word(word)
            else:
                phrase = self.database.get_phrase(item_id)
                if phrase:
                    phrase.priority = new_priority
                    return self.database.update_phrase(phrase)
            
            return False
        except Exception:
            return False
    
    def mark_for_review(self, item_id: int, item_type: ItemType) -> bool:
        """Mark an item for priority review"""
        
        progress = self.database.get_or_create_progress(1, item_type.value, item_id)
        
        # Reset some progress to bring item back to learning status
        if progress.status == LearningStatus.MASTERED:
            progress.status = LearningStatus.LEARNING
            progress.consecutive_correct = 0
            
        return self.database.update_progress(progress)
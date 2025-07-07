"""Test engine for typing and multiple choice tests"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import random
import difflib

from data.models import Word, Phrase, LearningProgress, LearningStatus, TestResult, TestType
from data.database import Database
from core.priority_manager import ItemType


class TestDifficulty(Enum):
    """Test difficulty levels"""
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class TestQuestion:
    """Single test question"""
    id: int
    item_type: ItemType
    question: str
    correct_answer: str
    options: Optional[List[str]] = None  # For multiple choice
    category: str = ""
    difficulty: int = 1
    
    def is_typing_test(self) -> bool:
        """Check if this is a typing test question"""
        return self.options is None


@dataclass
class TestAnswer:
    """User's answer to a test question"""
    question_id: int
    user_answer: str
    is_correct: bool
    response_time: float  # seconds
    similarity_score: float = 0.0  # For typing tests
    answered_at: Optional[datetime] = None


@dataclass
class TestSession:
    """Test session configuration and state"""
    test_type: TestType
    difficulty: TestDifficulty
    item_type: Optional[ItemType]  # None for mixed
    category: Optional[str]
    questions: List[TestQuestion]
    answers: List[TestAnswer]
    current_index: int = 0
    started_at: Optional[datetime] = None
    time_limit: Optional[int] = None  # seconds per question
    
    def get_current_question(self) -> Optional[TestQuestion]:
        """Get current question"""
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None
    
    def has_next_question(self) -> bool:
        """Check if there are more questions"""
        return self.current_index < len(self.questions) - 1
    
    def move_to_next(self) -> bool:
        """Move to next question"""
        if self.has_next_question():
            self.current_index += 1
            return True
        return False
    
    def get_progress_info(self) -> Dict[str, any]:
        """Get test progress information"""
        answered = len(self.answers)
        correct = sum(1 for a in self.answers if a.is_correct)
        
        return {
            'current': self.current_index + 1,
            'total': len(self.questions),
            'answered': answered,
            'correct': correct,
            'accuracy': (correct / max(answered, 1)) * 100,
            'remaining': len(self.questions) - self.current_index - 1
        }


class TestEngine:
    """Manages test creation and evaluation"""
    
    def __init__(self, database: Database):
        self.database = database
        self.current_session = None
        
        # Typing test settings
        self.typing_strictness = "partial"  # "partial" or "exact"
        self.similarity_threshold = 0.7  # For partial matching
        
    def create_typing_test(self,
                          question_count: int = 10,
                          difficulty: TestDifficulty = TestDifficulty.MEDIUM,
                          item_type: Optional[ItemType] = None,
                          category: Optional[str] = None,
                          direction: str = "ja_to_id") -> TestSession:
        """Create typing test session"""
        
        # Get test items
        items = self._get_test_items(question_count, difficulty, item_type, category)
        
        # Create questions
        questions = []
        for i, item in enumerate(items):
            if direction == "ja_to_id":
                # Japanese to Indonesian
                question_text = item.japanese if item.japanese else "翻訳なし"
                correct_answer = item.indonesian
            else:
                # Indonesian to Japanese
                question_text = item.indonesian
                correct_answer = item.japanese if item.japanese else "翻訳なし"
            
            question = TestQuestion(
                id=item.id,
                item_type=ItemType.WORD if hasattr(item, 'stem') else ItemType.PHRASE,
                question=question_text,
                correct_answer=correct_answer,
                category=item.category.value,
                difficulty=item.difficulty
            )
            questions.append(question)
        
        # Create session
        session = TestSession(
            test_type=TestType.TYPING,
            difficulty=difficulty,
            item_type=item_type,
            category=category,
            questions=questions,
            answers=[],
            started_at=datetime.now(),
            time_limit=30  # 30 seconds per question
        )
        
        self.current_session = session
        return session
    
    def create_multiple_choice_test(self,
                                  question_count: int = 10,
                                  difficulty: TestDifficulty = TestDifficulty.MEDIUM,
                                  item_type: Optional[ItemType] = None,
                                  category: Optional[str] = None) -> TestSession:
        """Create multiple choice test session"""
        
        # Get test items
        items = self._get_test_items(question_count, difficulty, item_type, category)
        
        # Get all items for wrong answers
        all_items = self._get_all_items()
        
        # Create questions
        questions = []
        for i, item in enumerate(items):
            # Indonesian question with Japanese choices
            question_text = item.indonesian
            correct_answer = item.japanese if item.japanese else "翻訳なし"
            
            # Generate wrong answers
            wrong_answers = self._generate_wrong_answers(item, all_items, 3)
            
            # Combine and shuffle options
            options = [correct_answer] + wrong_answers
            random.shuffle(options)
            
            question = TestQuestion(
                id=item.id,
                item_type=ItemType.WORD if hasattr(item, 'stem') else ItemType.PHRASE,
                question=question_text,
                correct_answer=correct_answer,
                options=options,
                category=item.category.value,
                difficulty=item.difficulty
            )
            questions.append(question)
        
        # Create session
        session = TestSession(
            test_type=TestType.MULTIPLE_CHOICE,
            difficulty=difficulty,
            item_type=item_type,
            category=category,
            questions=questions,
            answers=[],
            started_at=datetime.now(),
            time_limit=15  # 15 seconds per question
        )
        
        self.current_session = session
        return session
    
    def submit_answer(self, user_answer: str, response_time: float) -> TestAnswer:
        """Submit answer for current question"""
        if not self.current_session:
            raise ValueError("No active test session")
        
        current_question = self.current_session.get_current_question()
        if not current_question:
            raise ValueError("No current question")
        
        # Evaluate answer
        if current_question.is_typing_test():
            is_correct, similarity = self._evaluate_typing_answer(
                user_answer, current_question.correct_answer
            )
        else:
            is_correct = user_answer.strip() == current_question.correct_answer.strip()
            similarity = 1.0 if is_correct else 0.0
        
        # Create answer record
        answer = TestAnswer(
            question_id=current_question.id,
            user_answer=user_answer.strip(),
            is_correct=is_correct,
            response_time=response_time,
            similarity_score=similarity,
            answered_at=datetime.now()
        )
        
        # Add to session
        self.current_session.answers.append(answer)
        
        # Save to database
        self._save_test_result(current_question, answer)
        
        # Update learning progress
        self._update_learning_progress(current_question, answer)
        
        return answer
    
    def end_test(self) -> Optional[Dict[str, any]]:
        """End current test and return summary"""
        if not self.current_session:
            return None
        
        # Calculate summary
        total_questions = len(self.current_session.questions)
        answered = len(self.current_session.answers)
        correct = sum(1 for a in self.current_session.answers if a.is_correct)
        
        total_time = sum(a.response_time for a in self.current_session.answers)
        avg_time = total_time / max(answered, 1)
        
        accuracy = (correct / max(answered, 1)) * 100
        
        summary = {
            'test_type': self.current_session.test_type.value,
            'total_questions': total_questions,
            'answered': answered,
            'correct': correct,
            'accuracy': accuracy,
            'total_time': total_time,
            'average_time': avg_time,
            'started_at': self.current_session.started_at,
            'ended_at': datetime.now(),
            'questions': self.current_session.questions,
            'answers': self.current_session.answers
        }
        
        # Clear session
        self.current_session = None
        
        return summary
    
    def get_current_session(self) -> Optional[TestSession]:
        """Get current test session"""
        return self.current_session
    
    def _get_test_items(self, count: int, difficulty: TestDifficulty,
                       item_type: Optional[ItemType], category: Optional[str]) -> List:
        """Get items for test questions"""
        items = []
        
        # Get words if needed
        if item_type is None or item_type == ItemType.WORD:
            words = self.database.get_all_words(order_by="priority")
            for word in words:
                if category and word.category.value != category:
                    continue
                if self._matches_difficulty(word.difficulty, difficulty):
                    items.append(word)
        
        # Get phrases if needed
        if item_type is None or item_type == ItemType.PHRASE:
            phrases = self.database.get_all_phrases(order_by="priority")
            for phrase in phrases:
                if category and phrase.category.value != category:
                    continue
                if self._matches_difficulty(phrase.difficulty, difficulty):
                    items.append(phrase)
        
        # Filter items with translations
        items = [item for item in items if item.japanese and item.japanese.strip()]
        
        # Shuffle and limit
        random.shuffle(items)
        return items[:count]
    
    def _get_all_items(self) -> List:
        """Get all items for generating wrong answers"""
        words = self.database.get_all_words()
        phrases = self.database.get_all_phrases()
        
        all_items = []
        all_items.extend([w for w in words if w.japanese and w.japanese.strip()])
        all_items.extend([p for p in phrases if p.japanese and p.japanese.strip()])
        
        return all_items
    
    def _matches_difficulty(self, item_difficulty: int, test_difficulty: TestDifficulty) -> bool:
        """Check if item difficulty matches test difficulty"""
        if test_difficulty == TestDifficulty.EASY:
            return item_difficulty <= 2
        elif test_difficulty == TestDifficulty.MEDIUM:
            return 2 <= item_difficulty <= 4
        else:  # HARD
            return item_difficulty >= 3
    
    def _generate_wrong_answers(self, correct_item, all_items: List, count: int) -> List[str]:
        """Generate wrong answers for multiple choice"""
        wrong_answers = []
        
        # Get items from same category first
        same_category = [item for item in all_items 
                        if (item.category == correct_item.category and 
                            item.id != correct_item.id and
                            item.japanese != correct_item.japanese)]
        
        # Add some from same category
        if same_category:
            wrong_from_category = random.sample(
                same_category, min(count - len(wrong_answers), len(same_category))
            )
            wrong_answers.extend([item.japanese for item in wrong_from_category])
        
        # Fill remaining with random items
        if len(wrong_answers) < count:
            other_items = [item for item in all_items 
                          if (item.id != correct_item.id and 
                              item.japanese != correct_item.japanese and
                              item.japanese not in wrong_answers)]
            
            if other_items:
                remaining = count - len(wrong_answers)
                random_items = random.sample(other_items, min(remaining, len(other_items)))
                wrong_answers.extend([item.japanese for item in random_items])
        
        # Ensure we have enough answers
        while len(wrong_answers) < count:
            wrong_answers.append(f"選択肢{len(wrong_answers) + 1}")
        
        return wrong_answers[:count]
    
    def _evaluate_typing_answer(self, user_answer: str, correct_answer: str) -> Tuple[bool, float]:
        """Evaluate typing test answer"""
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        # Exact match
        if user_answer == correct_answer:
            return True, 1.0
        
        # If strict mode, return false for non-exact matches
        if self.typing_strictness == "exact":
            return False, 0.0
        
        # Calculate similarity for partial matching
        similarity = difflib.SequenceMatcher(None, user_answer, correct_answer).ratio()
        
        # Accept if similarity is above threshold
        is_correct = similarity >= self.similarity_threshold
        
        return is_correct, similarity
    
    def _save_test_result(self, question: TestQuestion, answer: TestAnswer):
        """Save test result to database"""
        result = TestResult(
            user_id=1,
            test_type=self.current_session.test_type,
            item_type=question.item_type.value,
            item_id=question.id,
            question=question.question,
            correct_answer=question.correct_answer,
            user_answer=answer.user_answer,
            is_correct=answer.is_correct,
            response_time=answer.response_time,
            tested_at=answer.answered_at
        )
        
        self.database.add_test_result(result)
    
    def _update_learning_progress(self, question: TestQuestion, answer: TestAnswer):
        """Update learning progress based on test result"""
        progress = self.database.get_or_create_progress(
            1, question.item_type.value, question.id
        )
        
        # Update progress
        if answer.is_correct:
            progress.correct_count += 1
            progress.consecutive_correct += 1
        else:
            progress.incorrect_count += 1
            progress.consecutive_correct = 0
        
        progress.last_reviewed_at = datetime.now()
        progress.review_count += 1
        
        # Update status
        progress.update_status()
        
        # Save
        self.database.update_progress(progress)
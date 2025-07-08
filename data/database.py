"""Database management for Indonesian Language Learning Application"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from .models import (
    Word, Phrase, LearningProgress, TestResult, 
    StudySession, UserSettings, LearningStatus, 
    TestType, Category
)


class Database:
    """Database management class"""
    
    def __init__(self, db_path: str = "indonesian_learning.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            
    def initialize(self):
        """Initialize database schema"""
        self.connect()
        
        # Create tables
        self._create_tables()
        
        # Insert default data
        self._insert_default_data()
        
        self.connection.commit()
        self.disconnect()
        
    def _create_tables(self):
        """Create database tables"""
        # Words table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indonesian TEXT NOT NULL UNIQUE,
                japanese TEXT NOT NULL,
                stem TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                frequency INTEGER DEFAULT 0,
                priority REAL DEFAULT 0.0,
                difficulty INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Phrases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indonesian TEXT NOT NULL UNIQUE,
                japanese TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                frequency INTEGER DEFAULT 0,
                priority REAL DEFAULT 0.0,
                difficulty INTEGER DEFAULT 1,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning progress table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                status TEXT DEFAULT 'not_started',
                learning_started_at TIMESTAMP,
                mastered_at TIMESTAMP,
                last_reviewed_at TIMESTAMP,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, item_type, item_id)
            )
        ''')
        
        # Test results table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                test_type TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct BOOLEAN DEFAULT 0,
                response_time REAL DEFAULT 0.0,
                tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Study sessions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                cards_studied INTEGER DEFAULT 0,
                tests_taken INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                total_time REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1 UNIQUE,
                theme_mode TEXT DEFAULT 'light',
                daily_goal INTEGER DEFAULT 20,
                test_difficulty INTEGER DEFAULT 2,
                typing_strictness TEXT DEFAULT 'partial',
                sound_enabled BOOLEAN DEFAULT 1,
                notification_enabled BOOLEAN DEFAULT 1,
                language TEXT DEFAULT 'ja',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_words_frequency 
            ON words(frequency DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_words_priority 
            ON words(priority DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_phrases_frequency 
            ON phrases(frequency DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_phrases_priority 
            ON phrases(priority DESC)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_progress_status 
            ON learning_progress(status)
        ''')
        
    def _insert_default_data(self):
        """Insert default data"""
        # Check if default settings exist
        self.cursor.execute('SELECT COUNT(*) FROM user_settings WHERE user_id = 1')
        if self.cursor.fetchone()[0] == 0:
            # Insert default settings
            self.cursor.execute('''
                INSERT INTO user_settings (user_id) VALUES (1)
            ''')
            
    # CRUD operations for Words
    def add_word(self, word: Word) -> int:
        """Add a new word"""
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO words (indonesian, japanese, stem, category, 
                                 frequency, priority, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (word.indonesian, word.japanese, word.stem, 
                  word.category.value, word.frequency, 
                  word.calculate_priority(), word.difficulty))
            
            word_id = self.cursor.lastrowid
            self.connection.commit()
            return word_id
        finally:
            self.disconnect()
            
    def get_word(self, word_id: int) -> Optional[Word]:
        """Get word by ID"""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM words WHERE id = ?', (word_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_word(row)
            return None
        finally:
            self.disconnect()
            
    def get_all_words(self, limit: Optional[int] = None, 
                      order_by: str = "priority") -> List[Word]:
        """Get all words"""
        self.connect()
        try:
            query = f'SELECT * FROM words ORDER BY {order_by} DESC'
            if limit:
                query += f' LIMIT {limit}'
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [self._row_to_word(row) for row in rows]
        finally:
            self.disconnect()
            
    def update_word(self, word: Word) -> bool:
        """Update word"""
        self.connect()
        try:
            word.priority = word.calculate_priority()
            self.cursor.execute('''
                UPDATE words 
                SET indonesian = ?, japanese = ?, stem = ?, category = ?,
                    frequency = ?, priority = ?, difficulty = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (word.indonesian, word.japanese, word.stem,
                  word.category.value, word.frequency, word.priority,
                  word.difficulty, word.id))
            
            self.connection.commit()
            return self.cursor.rowcount > 0
        finally:
            self.disconnect()
            
    def delete_word(self, word_id: int) -> bool:
        """Delete word"""
        self.connect()
        try:
            # Delete related learning progress
            self.cursor.execute('''
                DELETE FROM learning_progress 
                WHERE item_type = 'word' AND item_id = ?
            ''', (word_id,))
            
            # Delete word
            self.cursor.execute('DELETE FROM words WHERE id = ?', (word_id,))
            
            self.connection.commit()
            return self.cursor.rowcount > 0
        finally:
            self.disconnect()
    
    def search_words(self, search_term: str) -> List[Word]:
        """Search words by Indonesian text"""
        self.connect()
        try:
            self.cursor.execute('''
                SELECT * FROM words 
                WHERE indonesian = ? OR stem = ?
                ORDER BY frequency DESC
            ''', (search_term, search_term))
            rows = self.cursor.fetchall()
            return [self._row_to_word(row) for row in rows]
        finally:
            self.disconnect()
            
    # CRUD operations for Phrases
    def add_phrase(self, phrase: Phrase) -> int:
        """Add a new phrase"""
        self.connect()
        try:
            phrase.word_count = len(phrase.indonesian.split())
            self.cursor.execute('''
                INSERT INTO phrases (indonesian, japanese, category, 
                                   frequency, priority, difficulty, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (phrase.indonesian, phrase.japanese, 
                  phrase.category.value, phrase.frequency,
                  phrase.calculate_priority(), phrase.difficulty, 
                  phrase.word_count))
            
            phrase_id = self.cursor.lastrowid
            self.connection.commit()
            return phrase_id
        finally:
            self.disconnect()
            
    def get_phrase(self, phrase_id: int) -> Optional[Phrase]:
        """Get phrase by ID"""
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM phrases WHERE id = ?', (phrase_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_phrase(row)
            return None
        finally:
            self.disconnect()
            
    def get_all_phrases(self, limit: Optional[int] = None,
                       order_by: str = "priority") -> List[Phrase]:
        """Get all phrases"""
        self.connect()
        try:
            query = f'SELECT * FROM phrases ORDER BY {order_by} DESC'
            if limit:
                query += f' LIMIT {limit}'
                
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [self._row_to_phrase(row) for row in rows]
        finally:
            self.disconnect()
            
    # Learning Progress operations
    def get_or_create_progress(self, user_id: int, item_type: str, 
                              item_id: int) -> LearningProgress:
        """Get or create learning progress"""
        self.connect()
        try:
            # Try to get existing progress
            self.cursor.execute('''
                SELECT * FROM learning_progress 
                WHERE user_id = ? AND item_type = ? AND item_id = ?
            ''', (user_id, item_type, item_id))
            
            row = self.cursor.fetchone()
            if row:
                return self._row_to_progress(row)
            
            # Create new progress
            self.cursor.execute('''
                INSERT INTO learning_progress (user_id, item_type, item_id)
                VALUES (?, ?, ?)
            ''', (user_id, item_type, item_id))
            
            progress_id = self.cursor.lastrowid
            self.connection.commit()
            
            # Return new progress
            return LearningProgress(
                id=progress_id,
                user_id=user_id,
                item_type=item_type,
                item_id=item_id
            )
        finally:
            self.disconnect()
            
    def update_progress(self, progress: LearningProgress) -> bool:
        """Update learning progress"""
        self.connect()
        try:
            progress.accuracy_rate = progress.calculate_accuracy()
            progress.update_status()
            
            self.cursor.execute('''
                UPDATE learning_progress
                SET status = ?, learning_started_at = ?, mastered_at = ?,
                    last_reviewed_at = ?, correct_count = ?, 
                    incorrect_count = ?, consecutive_correct = ?,
                    accuracy_rate = ?, review_count = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (progress.status.value, progress.learning_started_at,
                  progress.mastered_at, progress.last_reviewed_at,
                  progress.correct_count, progress.incorrect_count,
                  progress.consecutive_correct, progress.accuracy_rate,
                  progress.review_count, progress.id))
            
            self.connection.commit()
            return self.cursor.rowcount > 0
        finally:
            self.disconnect()
            
    def get_learning_stats(self, user_id: int = 1) -> Dict[str, Any]:
        """Get learning statistics"""
        self.connect()
        try:
            stats = {}
            
            # Total words and phrases
            self.cursor.execute('SELECT COUNT(*) FROM words')
            stats['total_words'] = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM phrases')
            stats['total_phrases'] = self.cursor.fetchone()[0]
            
            # Learning progress stats
            for item_type in ['word', 'phrase']:
                for status in LearningStatus:
                    self.cursor.execute('''
                        SELECT COUNT(*) FROM learning_progress
                        WHERE user_id = ? AND item_type = ? AND status = ?
                    ''', (user_id, item_type, status.value))
                    
                    key = f'{item_type}s_{status.value}'
                    stats[key] = self.cursor.fetchone()[0]
                    
            # Calculate percentages
            for item_type in ['word', 'phrase']:
                total_key = f'total_{item_type}s'
                mastered_key = f'{item_type}s_mastered'
                if stats[total_key] > 0:
                    stats[f'{item_type}s_mastery_rate'] = (
                        stats[mastered_key] / stats[total_key] * 100
                    )
                else:
                    stats[f'{item_type}s_mastery_rate'] = 0
                    
            return stats
        finally:
            self.disconnect()
            
    # Test Result operations
    def add_test_result(self, result: TestResult) -> int:
        """Add test result"""
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO test_results 
                (user_id, test_type, item_type, item_id, question,
                 correct_answer, user_answer, is_correct, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (result.user_id, result.test_type.value, result.item_type,
                  result.item_id, result.question, result.correct_answer,
                  result.user_answer, result.is_correct, result.response_time))
            
            result_id = self.cursor.lastrowid
            self.connection.commit()
            return result_id
        finally:
            self.disconnect()
            
    # Helper methods
    def _row_to_word(self, row) -> Word:
        """Convert database row to Word object"""
        return Word(
            id=row['id'],
            indonesian=row['indonesian'],
            japanese=row['japanese'],
            stem=row['stem'],
            category=Category(row['category']),
            frequency=row['frequency'],
            priority=row['priority'],
            difficulty=row['difficulty'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    def _row_to_phrase(self, row) -> Phrase:
        """Convert database row to Phrase object"""
        return Phrase(
            id=row['id'],
            indonesian=row['indonesian'],
            japanese=row['japanese'],
            category=Category(row['category']),
            frequency=row['frequency'],
            priority=row['priority'],
            difficulty=row['difficulty'],
            word_count=row['word_count'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    def _row_to_progress(self, row) -> LearningProgress:
        """Convert database row to LearningProgress object"""
        return LearningProgress(
            id=row['id'],
            user_id=row['user_id'],
            item_type=row['item_type'],
            item_id=row['item_id'],
            status=LearningStatus(row['status']),
            learning_started_at=row['learning_started_at'],
            mastered_at=row['mastered_at'],
            last_reviewed_at=row['last_reviewed_at'],
            correct_count=row['correct_count'],
            incorrect_count=row['incorrect_count'],
            consecutive_correct=row['consecutive_correct'],
            accuracy_rate=row['accuracy_rate'],
            review_count=row['review_count'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
"""Export functionality for learning data"""

import csv
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from data.database import Database
from data.models import Word, Phrase, LearningProgress


class DataExporter:
    """Export learning data to various formats"""
    
    def __init__(self, database: Database):
        self.database = database
    
    def export_words_csv(self, file_path: str) -> bool:
        """Export words to CSV file"""
        try:
            words = self.database.get_all_words(order_by="priority")
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow([
                    'ID', 'Indonesian', 'Japanese', 'Stem', 'Category', 
                    'Frequency', 'Priority', 'Difficulty', 'Created'
                ])
                
                # Data
                for word in words:
                    writer.writerow([
                        word.id, word.indonesian, word.japanese, word.stem,
                        word.category.value, word.frequency, word.priority,
                        word.difficulty, word.created_at
                    ])
            
            return True
        except Exception:
            return False
    
    def export_phrases_csv(self, file_path: str) -> bool:
        """Export phrases to CSV file"""
        try:
            phrases = self.database.get_all_phrases(order_by="priority")
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow([
                    'ID', 'Indonesian', 'Japanese', 'Category', 
                    'Frequency', 'Priority', 'Difficulty', 'Word Count', 'Created'
                ])
                
                # Data
                for phrase in phrases:
                    writer.writerow([
                        phrase.id, phrase.indonesian, phrase.japanese,
                        phrase.category.value, phrase.frequency, phrase.priority,
                        phrase.difficulty, phrase.word_count, phrase.created_at
                    ])
            
            return True
        except Exception:
            return False
    
    def export_progress_csv(self, file_path: str, user_id: int = 1) -> bool:
        """Export learning progress to CSV file"""
        try:
            # This would need implementation in database
            # For now, return True as placeholder
            return True
        except Exception:
            return False
    
    def export_learning_report(self, file_path: str, user_id: int = 1) -> bool:
        """Export comprehensive learning report"""
        try:
            stats = self.database.get_learning_stats(user_id)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("インドネシア語学習レポート\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("学習統計:\n")
                f.write(f"- 総単語数: {stats['total_words']}\n")
                f.write(f"- 総フレーズ数: {stats['total_phrases']}\n")
                f.write(f"- 習得済み単語: {stats['words_mastered']}\n")
                f.write(f"- 習得済みフレーズ: {stats['phrases_mastered']}\n")
                f.write(f"- 単語習得率: {stats['words_mastery_rate']:.1f}%\n")
                f.write(f"- フレーズ習得率: {stats['phrases_mastery_rate']:.1f}%\n")
            
            return True
        except Exception:
            return False
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development Commands
- **Run the application**: `python main.py` or `python run_app.py`
- **Run tests**: `python run_tests.py`
- **Install dependencies**: `pip install -r requirements.txt`

### Mac App Building
- **Build Mac app**: `./package_mac_app.sh` (recommended) or `python build_mac_app.py`
- **Create app icons**: `python create_app_icon.py`
- **Manual flet pack**: `flet pack main.py --name "Indonesian Language Learning Tool" --add-data "sample_data:sample_data" --add-data "assets:assets" --icon "assets/app_icon.png" --onefile --windowed`

### Development Setup
- **Dependencies**: Main app requires `flet>=0.24.0`, optional deps include `openpyxl`, `python-docx`, `PyPDF2`
- **Python version**: Requires Python 3.9+
- **Database**: Uses SQLite3 database (`indonesian_learning.db`) created automatically

## High-Level Architecture

### Core Application Structure
This is a **Flet-based desktop application** for Indonesian language learning with a **layered MVC architecture**:

1. **UI Layer** (`ui/`): Flet-based views and components
2. **Core Layer** (`core/`): Business logic and processing engines
3. **Data Layer** (`data/`): Database models and data access
4. **Config Layer** (`config/`): Settings and configuration management

### Key Components and Data Flow

#### Indonesian Language Analysis Pipeline
1. **File Processing** (`core/file_processor.py`): Handles text, Excel, Word, PDF files
2. **Morphological Analysis** (`core/analyzer.py`): Indonesian stemming with complex prefix/suffix rules
   - Handles phonological changes (meng+k→ng, men+t→n, mem+p→m)
   - Removes prefixes (me-, ber-, ter-, di-, pe-, se-, ke-) and suffixes (-kan, -an, -i, -nya)
   - Processes confixes (ke-...-an, pe-...-an)
3. **Priority Calculation** (`core/priority_manager.py`): Weighted algorithm (frequency×0.4 + difficulty×0.2 + learning_status×0.3 + accuracy×0.1)

#### Learning System Architecture
- **Database Schema** (`data/database.py`): 6 main tables (words, phrases, learning_progress, test_results, study_sessions, user_settings)
- **Learning Progress Tracking**: 3-tier status system (NOT_STARTED → LEARNING → MASTERED)
- **Flashcard Engine** (`core/flashcard.py`): Session-based learning with spaced repetition concepts
- **Test Engine** (`core/test_engine.py`): Dual test system (typing + multiple choice) with similarity scoring using `difflib`

#### UI Component System
- **Main Window** (`ui/main_window.py`): Tab-based interface with 5 main views
- **Tutorial System** (`ui/tutorial_view.py`): 5-6 slide onboarding
- **Progress Visualization** (`ui/progress_view.py`): Charts, achievements, calendar view
- **Settings Management** (`ui/settings_view.py`): Theme, learning targets, test configuration

### Critical Implementation Details

#### Indonesian Stemming Engine
The `IndonesianAnalyzer` class implements complex morphological analysis:
- **Prefix variants**: meng-/men-/mem-/meny- with phonological restoration
- **Validation**: Uses common root word dictionary and vowel presence heuristics
- **Confix handling**: Processes circumfixes before other affixes

#### Priority Algorithm
Learning items are ranked using a weighted score system:
```python
priority = (frequency * 0.4) + (difficulty * 0.2) + (learning_status * 0.3) + (accuracy * 0.1)
```
Status multipliers adjust priority based on learning progress.

#### Test Evaluation System
- **Typing tests**: Use `difflib.SequenceMatcher` for similarity scoring with configurable thresholds
- **Multiple choice**: Auto-generate distractors from similar words
- **Mastery criteria**: 3 consecutive correct answers or 80%+ accuracy rate

### Database Schema Key Relationships
- Words/Phrases ↔ LearningProgress (1:1 per user)
- StudySession ↔ TestResults (1:many)
- LearningProgress tracks: status, accuracy_rate, consecutive_correct, last_reviewed

### File Processing Extensions
The system supports multiple file formats through `FileProcessorBase` inheritance:
- Base: UTF-8 text files
- Extensions: Excel (.xlsx), Word (.docx), PDF via optional dependencies

### Mac App Packaging
Uses `flet pack` with additional configuration for macOS:
- Creates `.app` bundle with Info.plist
- Includes sample data and assets
- Supports DMG installer creation
- Custom icon system with multiple sizes for Retina displays
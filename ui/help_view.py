"""Help and documentation view"""

import flet as ft
from typing import Callable, Optional
from config.settings import Settings


class HelpView:
    """Help and documentation dialog"""
    
    def __init__(self, page: ft.Page, settings: Settings):
        self.page = page
        self.settings = settings
        self.dialog = None
        self.on_close_callback = None
        
        # Help content
        self.help_sections = {
            "basic_usage": {
                "title": "基本的な使い方",
                "content": """
1. **ファイル処理**: テキストファイルを選択して「分析開始」ボタンをクリック
2. **学習リスト**: 分析結果から優先順位付きの学習リストを確認
3. **フラッシュカード**: 学習したい単語・フレーズを選んで学習開始
4. **テスト**: 習得度を確認するためのテスト実行
5. **進捗管理**: 学習状況の確認と目標管理
                """
            },
            "file_processing": {
                "title": "ファイル処理の詳細",
                "content": """
**対応ファイル形式**:
- .txt (テキストファイル)
- .xlsx/.xls (Excel) ※要openpyxlライブラリ
- .docx (Word) ※要python-docxライブラリ
- .pdf (PDF) ※要PyPDF2ライブラリ

**使用方法**:
1. 「ファイル選択」ボタンで単一ファイルまたは複数ファイルを選択
2. 「フォルダ選択」ボタンでフォルダ全体を指定
3. 「分析開始」ボタンで語幹抽出・頻度分析を実行

**分析結果**:
- 語幹別の頻度統計
- 単語・フレーズの重要度評価
- カテゴリ別の分類
                """
            },
            "learning_methods": {
                "title": "効果的な学習方法",
                "content": """
**段階的学習アプローチ**:
1. **語幹学習**: 最重要な語幹から順番に学習
2. **フレーズ学習**: 実用的なフレーズを文脈で理解
3. **テスト実行**: 定期的な習得度確認
4. **復習**: 忘却曲線に基づく復習タイミング

**学習のコツ**:
- 毎日少しずつ継続する（目標: 20語/日）
- 間違えた問題は繰り返し練習
- 実際の会話で使用してみる
- 進捗グラフでモチベーション維持
                """
            },
            "troubleshooting": {
                "title": "トラブルシューティング",
                "content": """
**よくある問題**:

Q: ファイルが読み込めない
A: ファイル形式と文字エンコーディングを確認してください。UTF-8推奨。

Q: 語幹抽出が正しくない
A: インドネシア語の活用形が複雑な場合、完全な抽出は困難な場合があります。

Q: 学習進捗が保存されない
A: データベースファイルの書き込み権限を確認してください。

Q: 音声が再生されない
A: システムの音声設定と、音声ライブラリのインストールを確認してください。

Q: アプリが重い
A: 大量のファイルを処理する際は、メモリ使用量が増加します。
                """
            }
        }
    
    def show(self, on_close: Optional[Callable] = None):
        """Show help dialog"""
        self.on_close_callback = on_close
        
        # Create help content
        help_content = self._create_help_content()
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ヘルプ・使い方"),
            content=help_content,
            actions=[
                ft.TextButton("閉じる", on_click=self._close_help),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def _create_help_content(self) -> ft.Container:
        """Create help content with tabs"""
        # Create tabs for different help sections
        help_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="基本操作",
                    icon=ft.icons.HELP_OUTLINE,
                    content=self._create_section_content("basic_usage")
                ),
                ft.Tab(
                    text="ファイル処理",
                    icon=ft.icons.FOLDER_OPEN,
                    content=self._create_section_content("file_processing")
                ),
                ft.Tab(
                    text="学習方法",
                    icon=ft.icons.SCHOOL,
                    content=self._create_section_content("learning_methods")
                ),
                ft.Tab(
                    text="FAQ",
                    icon=ft.icons.QUESTION_ANSWER,
                    content=self._create_section_content("troubleshooting")
                )
            ]
        )
        
        return ft.Container(
            content=help_tabs,
            width=600,
            height=500,
            padding=ft.padding.all(10)
        )
    
    def _create_section_content(self, section_key: str) -> ft.Container:
        """Create content for a help section"""
        section = self.help_sections[section_key]
        
        content = ft.Column(
            [
                ft.Text(
                    section["title"],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.PRIMARY
                ),
                ft.Container(height=10),
                ft.Text(
                    section["content"],
                    size=14,
                    selectable=True
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0
        )
        
        return ft.Container(
            content=content,
            padding=ft.padding.all(15)
        )
    
    def _close_help(self, e):
        """Close help dialog"""
        self.close()
    
    def close(self):
        """Close help dialog"""
        if self.dialog:
            self.dialog.open = False
            self.page.update()
            
        if self.on_close_callback:
            self.on_close_callback(None)
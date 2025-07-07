"""Common Indonesian phrase patterns for learning"""

from typing import List, Dict


class PhrasePatterns:
    """Common Indonesian phrase patterns by category"""
    
    BUSINESS_PHRASES = [
        # Meetings
        ("Selamat pagi, mari kita mulai rapat", "おはようございます、会議を始めましょう"),
        ("Apakah ada pertanyaan?", "質問はありますか？"),
        ("Tolong jelaskan lebih detail", "もっと詳しく説明してください"),
        ("Saya setuju dengan pendapat Anda", "あなたの意見に賛成です"),
        ("Mari kita diskusikan hal ini", "これについて話し合いましょう"),
        ("Bagaimana pendapat Anda?", "あなたの意見はどうですか？"),
        ("Terima kasih atas presentasinya", "プレゼンテーションありがとうございました"),
        ("Apakah ada masukan lain?", "他に意見はありますか？"),
        ("Mari kita lanjutkan ke topik berikutnya", "次のトピックに進みましょう"),
        ("Mohon maaf, bisa diulangi?", "すみません、もう一度言っていただけますか？"),
        
        # General Business
        ("Saya akan konfirmasi dulu", "確認させていただきます"),
        ("Mohon ditunggu sebentar", "少々お待ちください"),
        ("Baik, saya mengerti", "はい、分かりました"),
        ("Akan saya sampaikan ke atasan", "上司に伝えます"),
        ("Kapan deadline-nya?", "締切はいつですか？"),
        ("Tolong kirim by email", "メールで送ってください"),
        ("Saya akan follow up", "フォローアップします"),
        ("Mari kita koordinasi", "調整しましょう"),
    ]
    
    PRODUCTION_PHRASES = [
        # Production Floor
        ("Produksi hari ini berapa?", "今日の生産数はいくつですか？"),
        ("Ada masalah di mesin", "機械に問題があります"),
        ("Tolong cek kualitasnya", "品質をチェックしてください"),
        ("Material sudah datang?", "材料は届きましたか？"),
        ("Target hari ini tercapai", "今日の目標は達成しました"),
        ("Mesin sedang maintenance", "機械はメンテナンス中です"),
        ("Stok barang kurang", "在庫が不足しています"),
        ("Proses produksi lancar", "生産プロセスは順調です"),
        ("Ada reject berapa?", "不良品はいくつありますか？"),
        ("Shift malam mulai jam berapa?", "夜勤は何時から始まりますか？"),
        
        # Quality Control
        ("Kualitas harus dijaga", "品質を維持しなければなりません"),
        ("Ada defect di produk ini", "この製品に欠陥があります"),
        ("Tolong inspeksi ulang", "再検査してください"),
        ("Standar kualitas terpenuhi", "品質基準を満たしています"),
        ("Perlu perbaikan di bagian ini", "この部分は改善が必要です"),
    ]
    
    SAFETY_PHRASES = [
        # Safety Instructions
        ("Pakai alat pelindung diri", "保護具を着用してください"),
        ("Hati-hati, lantai licin", "注意、床が滑りやすいです"),
        ("Jangan lupa helm safety", "安全ヘルメットを忘れないでください"),
        ("Area berbahaya, dilarang masuk", "危険エリア、立入禁止"),
        ("Matikan mesin sebelum perbaikan", "修理前に機械を止めてください"),
        ("Ikuti prosedur keselamatan", "安全手順に従ってください"),
        ("Ada kecelakaan kerja", "労働災害が発生しました"),
        ("Panggil tim safety", "安全チームを呼んでください"),
        ("Jaga kebersihan area kerja", "作業エリアを清潔に保ってください"),
        ("Laporkan jika ada bahaya", "危険があれば報告してください"),
    ]
    
    DAILY_PHRASES = [
        # Greetings
        ("Selamat pagi", "おはようございます"),
        ("Selamat siang", "こんにちは"),
        ("Selamat sore", "こんにちは（夕方）"),
        ("Selamat malam", "こんばんは"),
        ("Apa kabar?", "お元気ですか？"),
        ("Sampai jumpa", "さようなら"),
        ("Sampai besok", "また明日"),
        ("Terima kasih", "ありがとうございます"),
        ("Sama-sama", "どういたしまして"),
        ("Permisi", "すみません"),
        
        # Common Expressions
        ("Tidak apa-apa", "大丈夫です"),
        ("Maaf, saya tidak mengerti", "すみません、分かりません"),
        ("Bisa tolong bantu?", "手伝ってもらえますか？"),
        ("Saya sedang belajar bahasa Indonesia", "インドネシア語を勉強しています"),
        ("Mohon maaf atas keterlambatan", "遅れて申し訳ありません"),
        ("Silakan duduk", "どうぞお座りください"),
        ("Mari makan siang bersama", "一緒にランチしましょう"),
        ("Hati-hati di jalan", "道中お気をつけて"),
    ]
    
    TECHNICAL_PHRASES = [
        # Technical Terms
        ("Sistem error", "システムエラー"),
        ("Perlu restart komputer", "コンピュータの再起動が必要です"),
        ("Update software terbaru", "最新のソフトウェアをアップデート"),
        ("Backup data penting", "重要なデータをバックアップ"),
        ("Koneksi internet lambat", "インターネット接続が遅い"),
        ("Setting konfigurasi", "設定の構成"),
        ("Install aplikasi baru", "新しいアプリをインストール"),
        ("Cek spesifikasi teknis", "技術仕様を確認"),
        ("Perbaiki bug program", "プログラムのバグを修正"),
        ("Test fungsi sistem", "システム機能をテスト"),
    ]
    
    @classmethod
    def get_all_phrases(cls) -> List[tuple]:
        """Get all phrases from all categories"""
        all_phrases = []
        all_phrases.extend(cls.BUSINESS_PHRASES)
        all_phrases.extend(cls.PRODUCTION_PHRASES)
        all_phrases.extend(cls.SAFETY_PHRASES)
        all_phrases.extend(cls.DAILY_PHRASES)
        all_phrases.extend(cls.TECHNICAL_PHRASES)
        return all_phrases
    
    @classmethod
    def get_phrases_by_category(cls, category: str) -> List[tuple]:
        """Get phrases by category"""
        category_map = {
            'business': cls.BUSINESS_PHRASES,
            'production': cls.PRODUCTION_PHRASES,
            'safety': cls.SAFETY_PHRASES,
            'daily': cls.DAILY_PHRASES,
            'technical': cls.TECHNICAL_PHRASES
        }
        return category_map.get(category.lower(), [])
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get list of available categories"""
        return ['business', 'production', 'safety', 'daily', 'technical']
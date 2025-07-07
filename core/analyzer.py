"""Indonesian language analyzer with stemming capabilities"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter, defaultdict


class IndonesianAnalyzer:
    """Indonesian language morphological analyzer"""
    
    def __init__(self):
        """Initialize analyzer with prefix/suffix rules"""
        # Prefixes with their removal rules
        self.prefixes = {
            # me- variants
            'meng': ['meng', 'me'],  # meng- before vowels, g, h
            'men': ['men', 'me'],    # men- before c, d, j, t
            'mem': ['mem', 'me'],    # mem- before b, p, f
            'me': ['me'],            # me- before l, m, n, r, w, y
            'meny': ['meny', 'me'],  # meny- before s (becomes ny)
            
            # ber- variants
            'ber': ['ber', 'be'],
            'bel': ['bel'],          # belajar
            
            # ter- variants
            'ter': ['ter'],
            
            # di- passive
            'di': ['di'],
            
            # pe- variants  
            'peng': ['peng', 'pe'],
            'pen': ['pen', 'pe'],
            'pem': ['pem', 'pe'],
            'pe': ['pe'],
            'peny': ['peny', 'pe'],
            'pel': ['pel', 'pe'],
            
            # per- variants
            'per': ['per'],
            
            # se- variants
            'se': ['se'],
            
            # ke- variants
            'ke': ['ke'],
        }
        
        # Suffixes
        self.suffixes = {
            'kan': ['kan'],
            'an': ['an'],
            'i': ['i'],
            'nya': ['nya'],
            'lah': ['lah'],
            'kah': ['kah'],
        }
        
        # Confixes (circumfixes)
        self.confixes = [
            ('ke', 'an'),     # ke-...-an
            ('pe', 'an'),     # pe-...-an
            ('per', 'an'),    # per-...-an
            ('ber', 'an'),    # ber-...-an
            ('se', 'nya'),    # se-...-nya
        ]
        
        # Common Indonesian root words for validation
        self.common_roots = {
            'makan', 'minum', 'tidur', 'kerja', 'jalan', 'baca', 'tulis',
            'lihat', 'dengar', 'bicara', 'pikir', 'rasa', 'buat', 'beli',
            'jual', 'kirim', 'terima', 'buka', 'tutup', 'mulai', 'akhir',
            'masuk', 'keluar', 'naik', 'turun', 'datang', 'pergi', 'duduk',
            'berdiri', 'lari', 'terbang', 'renang', 'main', 'bantu', 'ajar',
            'belajar', 'paham', 'tahu', 'ingat', 'lupa', 'cinta', 'suka',
            'benci', 'takut', 'berani', 'marah', 'sedih', 'senang', 'bahagia'
        }
        
        # Phonological rules for prefix modifications
        self.phonological_rules = {
            'meng': {
                'k': 'ng',  # mengkopi -> mengopi
                'g': 'ng',  # menggambar stays
                'h': 'ng',  # menghitung stays
                'vowel': 'ng'  # mengambil stays
            },
            'men': {
                't': 'n',   # mentranslate -> mentranslate
                'd': 'n',   # mendapat stays
                'c': 'n',   # mencari stays
                'j': 'n',   # menjadi stays
            },
            'mem': {
                'p': 'm',   # memukul (pukul)
                'b': 'm',   # membaca stays
                'f': 'm',   # memfoto stays
                'v': 'm',   # memvonis stays
            },
            'meny': {
                's': 'ny',  # menyapu (sapu)
            }
        }
        
    def analyze_text(self, text: str) -> Dict[str, any]:
        """Analyze Indonesian text and return word statistics"""
        # Normalize text
        text = self._normalize_text(text)
        
        # Tokenize
        words = self._tokenize(text)
        
        # Get stems and frequencies
        stems = []
        stem_to_words = defaultdict(set)
        word_freq = Counter(words)
        
        for word in words:
            stem = self.stem(word)
            stems.append(stem)
            stem_to_words[stem].add(word)
            
        stem_freq = Counter(stems)
        
        # Calculate statistics
        results = {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'total_stems': len(stems),
            'unique_stems': len(stem_freq),
            'word_frequency': dict(word_freq.most_common()),
            'stem_frequency': dict(stem_freq.most_common()),
            'stem_to_words': {k: list(v) for k, v in stem_to_words.items()},
            'top_words': word_freq.most_common(20),
            'top_stems': stem_freq.most_common(20)
        }
        
        return results
        
    def stem(self, word: str) -> str:
        """Stem an Indonesian word"""
        if not word or len(word) < 3:
            return word
            
        original = word.lower()
        
        # Try to remove confixes first
        for prefix, suffix in self.confixes:
            if word.startswith(prefix) and word.endswith(suffix):
                stem = word[len(prefix):-len(suffix)]
                if len(stem) >= 3:
                    # Check if it's a valid stem
                    if self._is_valid_stem(stem):
                        return stem
                        
        # Remove suffixes
        word = self._remove_suffix(word)
        
        # Remove prefixes
        word = self._remove_prefix(word)
        
        # If result is too short, return original
        if len(word) < 3:
            return original
            
        return word
        
    def _normalize_text(self, text: str) -> str:
        """Normalize text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers (but keep words with numbers)
        text = re.sub(r'\b\d+\b', '', text)
        
        # Keep only letters and basic punctuation
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
        
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Split by whitespace and punctuation
        words = re.findall(r'\b\w+\b', text)
        
        # Filter out very short words and numbers
        words = [w for w in words if len(w) > 2 and not w.isdigit()]
        
        return words
        
    def _remove_prefix(self, word: str) -> str:
        """Remove prefix from word"""
        # Try each prefix pattern
        for prefix_group, patterns in self.prefixes.items():
            for pattern in patterns:
                if word.startswith(pattern):
                    # Get the stem candidate
                    stem = word[len(pattern):]
                    
                    # Apply phonological restoration if needed
                    if prefix_group in self.phonological_rules:
                        stem = self._restore_phonology(stem, prefix_group)
                        
                    # Validate stem
                    if len(stem) >= 3:
                        return stem
                        
        return word
        
    def _remove_suffix(self, word: str) -> str:
        """Remove suffix from word"""
        for suffix, patterns in self.suffixes.items():
            for pattern in patterns:
                if word.endswith(pattern) and len(word) > len(pattern) + 2:
                    return word[:-len(pattern)]
                    
        return word
        
    def _restore_phonology(self, stem: str, prefix_type: str) -> str:
        """Restore original consonant after prefix removal"""
        if prefix_type == 'meng' and not stem:
            return stem
            
        rules = self.phonological_rules.get(prefix_type, {})
        
        # Check if we need to restore a consonant
        if prefix_type == 'meng' and stem.startswith(('k', 'g', 'h')):
            # These don't need restoration
            return stem
        elif prefix_type == 'meny' and len(stem) > 0:
            # Restore 's' if stem starts with compatible sound
            if stem[0] in 'aeiou':
                return 's' + stem
        elif prefix_type == 'mem' and stem.startswith('m'):
            # Could be memukul -> pukul
            return 'p' + stem[1:] if len(stem) > 1 else stem
        elif prefix_type == 'men' and stem.startswith('n'):
            # Could be menerjemah -> terjemah  
            return 't' + stem[1:] if len(stem) > 1 else stem
            
        return stem
        
    def _is_valid_stem(self, stem: str) -> bool:
        """Check if a stem is valid"""
        # Check length
        if len(stem) < 3:
            return False
            
        # Check if it's a known root
        if stem in self.common_roots:
            return True
            
        # Basic heuristics - Indonesian words typically have vowels
        vowels = set('aeiou')
        if not any(c in vowels for c in stem):
            return False
            
        return True
        
    def extract_phrases(self, text: str, min_length: int = 2, 
                       max_length: int = 5) -> List[Tuple[str, int]]:
        """Extract common phrases from text"""
        words = self._tokenize(self._normalize_text(text))
        phrases = []
        
        # Generate n-grams
        for n in range(min_length, min(max_length + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i + n])
                phrases.append(phrase)
                
        # Count frequencies
        phrase_freq = Counter(phrases)
        
        # Filter by minimum frequency
        common_phrases = [(phrase, freq) for phrase, freq in phrase_freq.items() 
                         if freq >= 2]
        
        # Sort by frequency
        common_phrases.sort(key=lambda x: x[1], reverse=True)
        
        return common_phrases[:50]  # Return top 50 phrases
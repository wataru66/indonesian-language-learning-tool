#!/usr/bin/env python3
"""
Translation service using multiple APIs
"""

import requests
import json
from typing import Optional, Dict
from indonesian_dictionary import get_japanese_translation, INDONESIAN_JAPANESE_DICT


class TranslationService:
    """Multi-provider translation service"""
    
    def __init__(self):
        self.providers = {
            'local': self._local_translate,
            'google_free': self._google_translate_free,
            'mymemory': self._mymemory_translate,
            'libretranslate': self._libretranslate,
        }
        
        # Fallback order
        self.fallback_order = ['local', 'google_free', 'mymemory', 'libretranslate']
    
    def translate(self, text: str, source_lang: str = 'id', target_lang: str = 'ja') -> str:
        """Translate text using fallback providers"""
        
        # Skip translation for very short or invalid text
        if not text or len(text.strip()) < 2:
            return text
        
        text = text.strip().lower()
        
        # Try each provider in order
        for provider_name in self.fallback_order:
            try:
                provider = self.providers[provider_name]
                result = provider(text, source_lang, target_lang)
                
                if result and result != text:
                    print(f"Translation: {text} -> {result} (via {provider_name})")
                    return result
                    
            except Exception as e:
                print(f"Translation error with {provider_name}: {e}")
                continue
        
        # If all fail, return original with indicator
        return f"{text}（翻訳取得失敗）"
    
    def _local_translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Use local dictionary"""
        if source_lang == 'id' and target_lang == 'ja':
            result = get_japanese_translation(text)
            if not result.endswith('（翻訳未登録）'):
                return result
        return None
    
    def _google_translate_free(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Google Translate (free web scraping - may be rate limited)"""
        try:
            # Note: This is a simple approach, may need User-Agent headers
            url = f"https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                result = json.loads(response.text)
                if result and result[0] and result[0][0]:
                    return result[0][0][0]
                    
        except Exception as e:
            print(f"Google Translate error: {e}")
        
        return None
    
    def _mymemory_translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """MyMemory Translation API (free tier)"""
        try:
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('responseStatus') == 200:
                    return data['responseData']['translatedText']
                    
        except Exception as e:
            print(f"MyMemory translate error: {e}")
        
        return None
    
    def _libretranslate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """LibreTranslate API (self-hosted or public instance)"""
        try:
            # Public instance (may be slow or unavailable)
            url = "https://libretranslate.de/translate"
            
            data = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('translatedText')
                
        except Exception as e:
            print(f"LibreTranslate error: {e}")
        
        return None


class GoogleTranslateAPI:
    """Google Cloud Translation API (requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate(self, text: str, target_lang: str = 'ja', source_lang: str = 'id') -> Optional[str]:
        """Translate using Google Cloud Translation API"""
        if not self.api_key:
            print("Google Cloud API key not provided")
            return None
        
        try:
            url = f"{self.base_url}?key={self.api_key}"
            
            data = {
                'q': text,
                'target': target_lang,
                'source': source_lang
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and 'translations' in result['data']:
                    return result['data']['translations'][0]['translatedText']
            else:
                print(f"Google API error: {response.status_code}")
                
        except Exception as e:
            print(f"Google Cloud Translate error: {e}")
        
        return None


class DeepLAPI:
    """DeepL Translation API (requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api-free.deepl.com/v2/translate"  # Free tier
        # For Pro: "https://api.deepl.com/v2/translate"
    
    def translate(self, text: str, target_lang: str = 'JA', source_lang: str = 'ID') -> Optional[str]:
        """Translate using DeepL API"""
        if not self.api_key:
            print("DeepL API key not provided")
            return None
        
        try:
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'text': text,
                'target_lang': target_lang,
                'source_lang': source_lang
            }
            
            response = requests.post(self.base_url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'translations' in result:
                    return result['translations'][0]['text']
            else:
                print(f"DeepL API error: {response.status_code}")
                
        except Exception as e:
            print(f"DeepL API error: {e}")
        
        return None


# Configuration
def get_translation_service(google_api_key: Optional[str] = None, 
                          deepl_api_key: Optional[str] = None) -> TranslationService:
    """Get configured translation service"""
    service = TranslationService()
    
    # Add paid APIs if keys are provided
    if google_api_key:
        google_api = GoogleTranslateAPI(google_api_key)
        service.providers['google_api'] = lambda text, sl, tl: google_api.translate(text, tl, sl)
        service.fallback_order.insert(1, 'google_api')  # High priority
    
    if deepl_api_key:
        deepl_api = DeepLAPI(deepl_api_key)
        service.providers['deepl'] = lambda text, sl, tl: deepl_api.translate(text, tl.upper(), sl.upper())
        service.fallback_order.insert(1, 'deepl')  # High priority
    
    return service


# Example usage and testing
if __name__ == "__main__":
    # Test translation service
    service = TranslationService()
    
    test_words = [
        "makan", "kerja", "selamat", "pagi", "terima", "kasih",
        "produksi", "kualitas", "keselamatan", "pabrik", "mesin"
    ]
    
    print("Testing Translation Service:")
    print("=" * 50)
    
    for word in test_words:
        translation = service.translate(word)
        print(f"{word:<15} -> {translation}")
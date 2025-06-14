import asyncio
from googletrans import Translator

async def translate_text(text, target_language, source_language=None):
    """Translate text to target language using Google Translate API asynchronously."""
    try:
        translator = Translator()
        result = await translator.translate(text, dest=target_language, src=source_language if source_language else 'auto')
        
        print(f"\nOriginal text ({result.src}):")
        print(text)
        print(f"\nTranslated text ({result.dest}):")
        print(result.text)
        
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def list_common_languages():
    """List common language codes for translation"""
    languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }
    
    print("\nCommon language codes:")
    for code, name in languages.items():
        print(f"{code}: {name}")
    
    return languages

import os
import json
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API transcription and translation functions removed. Running offline.

def transcribe_and_translate_local(audio_path: str, source_lang_code: str = "zh") -> List[Dict[str, Any]]:
    """
    Transcribes audio using local Whisper model and translates using Google Translate (deep-translator).
    - source_lang_code: 'zh' for Chinese, 'en' for English, 'ja' for Japanese, etc.
    """
    logger.info("Using local Whisper model for Speech-to-Text...")
    try:
        import whisper
    except ImportError:
        raise ImportError("whisper library is not installed. Please run pip install openai-whisper.")

    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise ImportError("deep-translator library is not installed. Please run pip install deep-translator.")

    # Load a lightweight model (base is good for local CPU/GPU balance)
    logger.info("Loading Whisper 'base' model (this might take a few moments on first run)...")
    model = whisper.load_model("base")
    
    logger.info(f"Transcribing audio file: {audio_path}")
    # Whisper and GoogleTranslator use different language codes for Chinese:
    # - Whisper: 'zh'
    # - GoogleTranslator (deep-translator): 'zh-CN'
    whisper_code = source_lang_code
    translator_code = source_lang_code
    if source_lang_code.lower() in ("zh-cn", "zh"):
        whisper_code = "zh"
        translator_code = "zh-CN"
    logger.info(f"[System] Language codes - Whisper: {whisper_code}, Translator: {translator_code}")
    # Run transcription
    result = model.transcribe(audio_path, language=whisper_code)
    
    raw_segments = result.get("segments", [])
    logger.info(f"Transcription finished. Transcribed {len(raw_segments)} segments.")
    
    # Translate segments to Vietnamese
    logger.info("Translating segments to Vietnamese using Google Translate...")
    translator = GoogleTranslator(source=translator_code, target='vi')
    
    processed_segments = []
    for i, seg in enumerate(raw_segments):
        original_text = seg.get("text", "").strip()
        if not original_text:
            continue
            
        try:
            translated_text = translator.translate(original_text)
        except Exception as e:
            logger.warning(f"Translation failed for segment {i}: {e}. Falling back to original.")
            translated_text = original_text
            
        processed_segments.append({
            "start": seg.get("start", 0.0),
            "end": seg.get("end", 0.0),
            "text": original_text,
            "translation": translated_text
        })
        
    logger.info("Local transcription and translation completed successfully.")
    return processed_segments

def translate_video_audio(audio_path: str, source_lang: str = "Chinese") -> List[Dict[str, Any]]:
    """
    Main entry point for translation.
    Transcribes audio using local Whisper model and translates using Google Translate (offline/local fallback).
    """
    # Map friendly language name to Whisper code
    lang_map = {
        "Chinese": "zh",
        "English": "en",
        "Japanese": "ja",
        "Korean": "ko"
    }
    lang_code = lang_map.get(source_lang, "zh")
    return transcribe_and_translate_local(audio_path, lang_code)

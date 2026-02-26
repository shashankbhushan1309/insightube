#!/usr/bin/env python3
"""
qa.py
Answer user questions strictly based on the video transcript.

Usage: python3 qa.py VIDEO_ID "QUESTION" [LANGUAGE_CODE]
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from gemini_helper import call_gemini

LANG_INSTRUCTIONS = {
    'en': 'Answer in English.',
    'hi': 'Answer in Hindi.',
    'ta': 'Answer in Tamil.',
    'kn': 'Answer in Kannada.',
    'te': 'Answer in Telugu.',
    'mr': 'Answer in Marathi.',
}

NOT_FOUND_MESSAGES = {
    'en': '⚠️ This topic is not covered in the video.',
    'hi': '⚠️ यह विषय वीडियो में शामिल नहीं है।',
    'ta': '⚠️ இந்த தலைப்பு வீடியோவில் உள்ளடக்கப்படவில்லை.',
    'kn': '⚠️ ಈ ವಿಷಯವನ್ನು ವೀಡಿಯೊದಲ್ಲಿ ಒಳಗೊಂಡಿಲ್ಲ.',
    'te': '⚠️ ఈ అంశం వీడియోలో కవర్ చేయబడలేదు.',
    'mr': '⚠️ हा विषय व्हिडिओमध्ये समाविष्ट केलेला नाही.',
}

def answer(video_id: str, question: str, lang: str = 'en') -> str:
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.json")

    if not os.path.exists(cache_path):
        return "⚠️ Transcript not found in cache. Please fetch it first."

    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    transcript = data.get('transcript_text', '')
    lang_instruction = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS['en'])
    not_found = NOT_FOUND_MESSAGES.get(lang, NOT_FOUND_MESSAGES['en'])

    # Use up to 8000 chars of transcript for Q&A context
    transcript_chunk = transcript[:8000]

    prompt = f"""You are a Q&A assistant for a YouTube video. Answer ONLY using information found in the transcript below.

STRICT RULES:
1. If the answer IS in the transcript → give a clear, specific, helpful answer
2. If the answer is NOT in the transcript → respond with ONLY: "{not_found}"
3. NEVER make up, infer, or add information not explicitly in the transcript
4. Do not use your own knowledge about the topic — only use the transcript
5. Keep answers concise (under 200 words) unless depth is needed
6. {lang_instruction}

Transcript:
{transcript_chunk}

Question: {question}

Answer:"""

    return call_gemini(prompt, max_tokens=1024)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('⚠️ Usage: python3 qa.py VIDEO_ID "QUESTION" [LANGUAGE_CODE]')
        sys.exit(1)

    video_id = sys.argv[1]
    user_question = sys.argv[2]
    language_code = sys.argv[3] if len(sys.argv) > 3 else 'en'

    result = answer(video_id, user_question, language_code)
    print(result)

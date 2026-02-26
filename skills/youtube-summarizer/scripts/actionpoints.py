#!/usr/bin/env python3
"""
actionpoints.py
Extract concrete, actionable items from the video transcript.

Usage: python3 actionpoints.py VIDEO_ID [LANGUAGE_CODE]
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from gemini_helper import call_gemini

LANG_INSTRUCTIONS = {
    'en': 'Respond in English.',
    'hi': 'Respond entirely in Hindi.',
    'ta': 'Respond entirely in Tamil.',
    'kn': 'Respond entirely in Kannada.',
    'te': 'Respond entirely in Telugu.',
    'mr': 'Respond entirely in Marathi.',
}

def actionpoints(video_id: str, lang: str = 'en') -> str:
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.json")

    if not os.path.exists(cache_path):
        return "⚠️ Transcript not found in cache. Please fetch it first."

    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    transcript = data.get('transcript_text', '')
    lang_instruction = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS['en'])
    transcript_chunk = transcript[:8000]

    prompt = f"""{lang_instruction}

You are an expert at extracting actionable insights. From this YouTube video transcript, extract concrete actions the viewer should take.

Transcript:
{transcript_chunk}

Provide this exact structure:

✅ **Action Points from This Video**

⚡ **Immediate Actions** (do today):
- [Specific action]
- [Specific action]

📅 **Short-Term Actions** (this week):
- [Specific action]
- [Specific action]

🎯 **Long-Term Actions** (this month or beyond):
- [Specific action]
- [Specific action]

💡 **Tools & Resources Mentioned:**
- [Any tools, apps, books, websites, or services referenced in the video]

🚫 **What to Avoid** (mistakes or pitfalls mentioned):
- [Any warnings or things the speaker says not to do]

Note: Only include actions and resources actually mentioned or clearly implied in the transcript."""

    return call_gemini(prompt, max_tokens=2048)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('⚠️ Usage: python3 actionpoints.py VIDEO_ID [LANGUAGE_CODE]')
        sys.exit(1)

    video_id = sys.argv[1]
    language_code = sys.argv[2] if len(sys.argv) > 2 else 'en'

    result = actionpoints(video_id, language_code)
    print(result)

#!/usr/bin/env python3
"""
deepdive.py
Generate a deep analytical breakdown of the video transcript.

Usage: python3 deepdive.py VIDEO_ID [LANGUAGE_CODE]
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

def deepdive(video_id: str, lang: str = 'en') -> str:
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

You are an expert analyst. Perform a DEEP DIVE analysis of this YouTube video transcript. Go beyond the surface — find the real substance.

Transcript:
{transcript_chunk}

Provide this exact structure:

🔬 **Deep Dive Analysis**

🔍 **Core Arguments:**
[What is the main thesis? What key claims does the speaker make?]

📊 **Evidence & Data Mentioned:**
[Any statistics, studies, facts, numbers, or research cited in the video]

🧩 **Non-Obvious Insights:**
[What are the subtle, less-obvious points most viewers would miss?]

⚡ **What's Being Challenged:**
[What conventional wisdom, myths, or assumptions does the speaker push back on?]

🔗 **How the Topics Connect:**
[How do the different sections/ideas in the video relate to each other?]

💎 **Top 3 Most Valuable Takeaways:**
1. [Most valuable insight]
2. [Second most valuable insight]
3. [Third most valuable insight]"""

    return call_gemini(prompt, max_tokens=2048)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('⚠️ Usage: python3 deepdive.py VIDEO_ID [LANGUAGE_CODE]')
        sys.exit(1)

    video_id = sys.argv[1]
    language_code = sys.argv[2] if len(sys.argv) > 2 else 'en'

    result = deepdive(video_id, language_code)
    print(result)

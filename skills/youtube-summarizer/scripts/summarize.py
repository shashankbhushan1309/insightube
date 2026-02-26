#!/usr/bin/env python3
"""
summarize.py
Generate a structured summary of a YouTube transcript using Gemini.

Usage: python3 summarize.py VIDEO_ID LANGUAGE_CODE
Language codes: en, hi, ta, kn, te, mr
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from gemini_helper import call_gemini

LANG_INSTRUCTIONS = {
    'en': 'Respond in English.',
    'hi': 'Respond entirely in Hindi (हिंदी में उत्तर दें).',
    'ta': 'Respond entirely in Tamil (தமிழில் பதில் அளிக்கவும்).',
    'kn': 'Respond entirely in Kannada (ಕನ್ನಡದಲ್ಲಿ ಉತ್ತರಿಸಿ).',
    'te': 'Respond entirely in Telugu (తెలుగులో సమాధానం ఇవ్వండి).',
    'mr': 'Respond entirely in Marathi (मराठीत उत्तर द्या).',
}

def summarize(video_id: str, lang: str = 'en') -> str:
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.json")

    if not os.path.exists(cache_path):
        return "⚠️ Transcript not found in cache. Please fetch it first."

    with open(cache_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    transcript = data.get('transcript_text', '')
    lang_instruction = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS['en'])

    # Use first 10000 chars for summary — efficient token use
    transcript_chunk = transcript[:10000]

    prompt = f"""{lang_instruction}

You are an expert video analyst. Analyze this YouTube video transcript and produce a structured summary.

Transcript:
{transcript_chunk}

Output EXACTLY this format (fill in all sections with real content from the transcript):

🎥 **[Infer a descriptive title from the transcript content]**

📌 **5 Key Points:**
1. [Specific, informative point from the video]
2. [Specific, informative point from the video]
3. [Specific, informative point from the video]
4. [Specific, informative point from the video]
5. [Specific, informative point from the video]

⏱ **Important Timestamps:**
• [MM:SS] — [What is being discussed at this point]
• [MM:SS] — [What is being discussed at this point]
• [MM:SS] — [What is being discussed at this point]
• [MM:SS] — [What is being discussed at this point]

🧠 **Core Takeaway:**
[One powerful, specific sentence capturing the central insight of the video]

💡 **Why It Matters:**
[2-3 sentences explaining the real-world relevance of this video's content]

---
_💬 Ask me any questions about this video! Try /deepdive or /actionpoints for more._"""

    return call_gemini(prompt, max_tokens=2048)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('⚠️ Usage: python3 summarize.py VIDEO_ID [LANGUAGE_CODE]')
        sys.exit(1)

    video_id = sys.argv[1]
    language_code = sys.argv[2] if len(sys.argv) > 2 else 'en'

    result = summarize(video_id, language_code)
    print(result)

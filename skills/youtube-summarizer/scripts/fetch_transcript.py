#!/usr/bin/env python3
"""
fetch_transcript.py
Fetches YouTube transcript and caches it to disk.
Outputs JSON status.

Usage: python3 fetch_transcript.py VIDEO_ID
"""

import sys
import json
import subprocess
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def ensure_deps():
    try:
        import youtube_transcript_api
    except ImportError:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'youtube-transcript-api', '-q', '--break-system-packages'],
            capture_output=True
        )

ensure_deps()

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

LANGUAGE_PRIORITY = ['en', 'en-US', 'en-GB', 'hi', 'ta', 'kn', 'te', 'mr']
MAX_CHARS = 45000  # ~10k tokens, safe for Gemini

def format_timestamp(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f'{h:02d}:{m:02d}:{sec:02d}'
    return f'{m:02d}:{sec:02d}'

def fetch(video_id: str) -> dict:
    cache_path = os.path.join(CACHE_DIR, f"{video_id}.json")
    if os.path.exists(cache_path):
        return {'error': None, 'cached': True}

    try:
        tlist = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return {'error': 'TRANSCRIPTS_DISABLED'}
    except NoTranscriptFound:
        return {'error': 'NO_TRANSCRIPT_FOUND'}
    except Exception as e:
        msg = str(e).lower()
        if 'unavailable' in msg or 'private' in msg or 'removed' in msg:
            return {'error': 'VIDEO_UNAVAILABLE'}
        return {'error': f'FETCH_ERROR: {e}'}

    transcript = None
    for lang in LANGUAGE_PRIORITY:
        try:
            transcript = tlist.find_transcript([lang])
            break
        except Exception:
            continue

    if transcript is None:
        try:
            available = list(tlist)
            if not available:
                return {'error': 'NO_TRANSCRIPT'}
            t = available[0]
            try:
                transcript = t.translate('en')
            except Exception:
                transcript = t
        except Exception as e:
            return {'error': f'FETCH_ERROR: {e}'}

    try:
        data = transcript.fetch()
    except Exception as e:
        return {'error': f'FETCH_ERROR: {e}'}

    texts = []
    segments = []
    for item in data:
        text = item.get('text', '').replace('\n', ' ').strip()
        start = item.get('start', 0)
        if text:
            texts.append(text)
            segments.append({
                'text': text,
                'start': start,
                'timestamp': format_timestamp(start)
            })

    full_text = ' '.join(texts)
    truncated = False
    if len(full_text) > MAX_CHARS:
        full_text = full_text[:MAX_CHARS]
        truncated = True

    cache_data = {
        'transcript_text': full_text,
        'segments': segments[:60]
    }
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False)

    return {
        'error': None,
        'cached': False,
        'language': getattr(transcript, 'language_code', 'unknown'),
        'truncated': truncated
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'NO_VIDEO_ID'}))
        sys.exit(1)
    
    res = fetch(sys.argv[1].strip())
    print(json.dumps(res, ensure_ascii=False))

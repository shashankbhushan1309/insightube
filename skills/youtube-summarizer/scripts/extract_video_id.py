#!/usr/bin/env python3
"""
extract_video_id.py
Extract YouTube video ID from a message/URL.
Outputs the 11-char video ID, or "INVALID" if not found.

Usage: python3 extract_video_id.py "https://youtube.com/watch?v=dQw4w9WgXcQ"
"""

# SECURITY MANIFEST:
# Environment variables accessed: none
# External endpoints called: none
# Local files read: none
# Local files written: none

import sys
import re

PATTERNS = [
    r'(?:v=)([a-zA-Z0-9_-]{11})',
    r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
    r'(?:embed/)([a-zA-Z0-9_-]{11})',
    r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    r'(?:/v/)([a-zA-Z0-9_-]{11})',
]

def extract_video_id(text: str) -> str:
    # Must contain a YouTube domain
    if 'youtube.com' not in text and 'youtu.be' not in text:
        return 'INVALID'
    for pattern in PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return 'INVALID'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('INVALID')
        sys.exit(0)
    result = extract_video_id(sys.argv[1])
    print(result)

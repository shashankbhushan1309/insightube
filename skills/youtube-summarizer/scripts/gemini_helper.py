#!/usr/bin/env python3
"""
gemini_helper.py
Shared Gemini API caller used by all skill scripts.
Model: gemini-2.0-flash (fast, cheap, multilingual)
"""

# SECURITY MANIFEST:
# Environment variables accessed: GEMINI_API_KEY
# External endpoints called: generativelanguage.googleapis.com
# Local files read: none
# Local files written: none

import os
import sys
import time
import subprocess

def ensure_deps():
    try:
        import google.generativeai
    except ImportError:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'google-generativeai', '-q', '--break-system-packages'],
            capture_output=True
        )

ensure_deps()

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

MODEL = 'gemini-2.0-flash'
MAX_RETRIES = 3


def call_gemini(prompt: str, max_tokens: int = 2048) -> str:
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return '⚠️ GEMINI_API_KEY is not set. Please configure it in OpenClaw settings.'

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config={
            'max_output_tokens': max_tokens,
            'temperature': 0.3,
            'top_p': 0.8,
        }
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text
            return '⚠️ Empty response from AI. Please try again.'
        except google_exceptions.ResourceExhausted:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return '⚠️ Gemini API rate limit reached. Please wait a moment and try again.'
        except google_exceptions.InvalidArgument as e:
            return f'⚠️ Invalid request: {e}'
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)
            else:
                return f'⚠️ AI service error: {e}'

    return '⚠️ Failed after multiple attempts. Please try again.'

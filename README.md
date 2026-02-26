# 🎥 YouTube Summarizer & Q&A — OpenClaw Skill

A fully functional YouTube AI Research Assistant built as a **proper OpenClaw skill**. Powered by **Gemini 2.0 Flash**. Deployed on Telegram via OpenClaw's native gateway — no custom bot framework needed.

---

## What is OpenClaw?

OpenClaw is an open-source autonomous AI agent (162k+ GitHub stars). It runs a Node.js **gateway** that connects to Telegram (and other platforms) and routes messages to an LLM. Skills are the way you extend what the agent can do.

**How skills work:**
- A skill = a folder with a `SKILL.md` + optional `scripts/` (Python/Bash) + `references/` (docs)
- `SKILL.md` tells the LLM *when* and *how* to use the skill
- `scripts/` contains the actual runnable code the LLM executes via the `exec` tool
- OpenClaw injects the skill instructions into the LLM's system prompt at runtime

This is NOT a Python chatbot. OpenClaw handles all of Telegram, sessions, and message routing.

---

## Project Structure

```
yt-openclaw/
├── skills/
│   └── youtube-summarizer/          ← The OpenClaw skill
│       ├── SKILL.md                 ← Instructions for the LLM (when/how to activate)
│       ├── scripts/
│       │   ├── extract_video_id.py  ← Validates YouTube URLs, extracts video ID
│       │   ├── fetch_transcript.py  ← Fetches transcript via youtube-transcript-api
│       │   ├── gemini_helper.py     ← Shared Gemini API caller (retry + rate limit)
│       │   ├── summarize.py         ← Generates structured summary via Gemini
│       │   ├── qa.py                ← Answers questions grounded in transcript
│       │   ├── deepdive.py          ← Deep analysis (/deepdive command)
│       │   └── actionpoints.py      ← Action item extraction (/actionpoints command)
│       └── references/
│           ├── errors.md            ← Error handling reference (loaded by LLM on-demand)
│           └── languages.md         ← Language codes and detection triggers
├── config/
│   ├── openclaw.json                ← OpenClaw gateway config (Telegram, model, skills)
│   └── SOUL.md                      ← Agent personality and greeting
├── Dockerfile                       ← Cloud deployment (Node 22 + Python + OpenClaw)
├── railway.toml                     ← Railway one-click deploy config
├── .env.example                     ← Environment variable template
└── README.md                        ← This file
```

---

## Architecture

```
User sends Telegram message
         │
         ▼
┌─────────────────────────────────────────┐
│          OpenClaw Gateway               │
│  (Node.js process — handles Telegram    │
│   via grammY, sessions, routing)        │
└────────────┬────────────────────────────┘
             │ Message routed to agent
             ▼
┌─────────────────────────────────────────┐
│          LLM: Gemini 2.0 Flash          │
│  System prompt includes:                │
│  • SOUL.md (personality)                │
│  • youtube-summarizer SKILL.md          │
│  • Tool schemas (exec, read, write)     │
└────────────┬────────────────────────────┘
             │ LLM decides to run a script
             ▼
┌─────────────────────────────────────────┐
│          exec tool (sandboxed)          │
│                                         │
│  python3 scripts/extract_video_id.py   │
│  python3 scripts/fetch_transcript.py   │→ youtube-transcript-api
│  python3 scripts/summarize.py          │→ Gemini API
│  python3 scripts/qa.py                 │→ Gemini API
│  python3 scripts/deepdive.py           │→ Gemini API
│  python3 scripts/actionpoints.py       │→ Gemini API
└─────────────────────────────────────────┘
             │ Script output returned to LLM
             ▼
       OpenClaw sends response to Telegram
```

### Why This Architecture

| Decision | Reason |
|---|---|
| **Separate Python scripts** | LLM runs them via `exec` tool — clean separation of logic from instructions |
| **gemini_helper.py shared module** | Single retry/rate-limit logic reused across all scripts |
| **references/ folder** | LLM loads error/language docs on-demand — saves tokens |
| **`metadata.clawdbot`** | Correct OpenClaw frontmatter key (not `metadata.openclaw`) |
| **Gemini 2.0 Flash** | Natively multilingual, fast, cheap — no translation layer needed |
| **dmPolicy: open** | Anyone can DM the bot without manual pairing |
| **Session TTL 1hr** | Auto-clears stale video context |

---

## Setup Guide

### Step 1 — Get API Keys

**Telegram Bot Token:**
1. Open Telegram → search **@BotFather**
2. Send `/newbot` → follow prompts
3. Copy the token: `7123456789:AAH...`

**Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API Key**
3. Copy it: `AIza...`

---

### Step 2 — Deploy to Cloud (No Local Terminal Needed)

#### ⭐ Option A: Railway (Recommended — Free Tier)

1. Push this repo to GitHub:
   ```bash
   git init
   git add .
   git commit -m "YouTube summarizer OpenClaw skill"
   git remote add origin https://github.com/YOUR_NAME/yt-openclaw
   git push -u origin main
   ```

2. Go to https://railway.app → **New Project → Deploy from GitHub Repo**

3. Select your repo — Railway auto-detects the Dockerfile

4. Go to **Variables** tab → add:
   ```
   TELEGRAM_BOT_TOKEN = 7123456789:AAH...your_token
   GEMINI_API_KEY     = AIza...your_key
   ```

5. Click **Deploy** — wait ~2 minutes for the build

6. In **Logs**, you should see:
   ```
   Skills loaded: youtube-summarizer ✓
   Telegram: connected (@your_bot_name)
   Gateway started
   ```

7. Open Telegram, find your bot, send `/start` ✅

---

#### Option B: Render

1. Go to https://render.com → **New → Web Service**
2. Connect your GitHub repo → set **Runtime**: Docker
3. Add environment variables (same as above)
4. Click **Create Web Service** → deploy ✅

---

#### Option C: Any VPS with Docker

```bash
git clone https://github.com/YOUR_NAME/yt-openclaw
cd yt-openclaw

docker build -t yt-openclaw .

docker run -d \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  -e GEMINI_API_KEY="your_key" \
  --name yt-bot \
  --restart unless-stopped \
  yt-openclaw

docker logs -f yt-bot
```

---

#### Option D: Replit (Browser-Based, No Setup)

1. Create a new **Bash** Repl on https://replit.com
2. Upload all files keeping folder structure intact
3. In **Secrets** tab (🔒): add `TELEGRAM_BOT_TOKEN` and `GEMINI_API_KEY`
4. In the Shell tab, run:
   ```bash
   # Install Node 22
   nvm install 22 && nvm use 22

   # Install Python deps
   pip3 install youtube-transcript-api google-generativeai --break-system-packages -q

   # Install OpenClaw
   npm install -g openclaw@latest

   # Copy configs to OpenClaw workspace
   mkdir -p ~/.openclaw/workspace/skills
   cp config/openclaw.json ~/.openclaw/openclaw.json
   cp config/SOUL.md ~/.openclaw/workspace/SOUL.md
   cp -r skills/youtube-summarizer ~/.openclaw/workspace/skills/

   # Start!
   openclaw gateway
   ```
5. Enable **Always On** (paid) or use UptimeRobot to ping the Repl URL every 5 minutes

---

## Usage

### Basic Flow

```
You:  https://youtube.com/watch?v=dQw4w9WgXcQ

Bot:  ✅ Transcript loaded! Generating summary...

      🎥 Rick Astley — Commitment and Loyalty Theme Analysis

      📌 5 Key Points:
      1. The song emphasizes unwavering commitment...
      2. ...

      ⏱ Important Timestamps:
      • 00:18 — Opening instrumental
      • 00:43 — First verse begins
      ...

      🧠 Core Takeaway:
      ...

      💬 Ask me anything about this video!
```

### Q&A

```
You:  What does he promise never to do?
Bot:  According to the video, he promises never to give you up, let you down, run around, or desert you...

You:  What instruments are used?
Bot:  ⚠️ This topic is not covered in the video.
```

### Commands

| Command | Action |
|---|---|
| `/summary` | Regenerate summary for current video |
| `/deepdive` | Core arguments, evidence, hidden insights |
| `/actionpoints` | Concrete actions to take after watching |
| `/language hindi` | Set response language |
| `/clear` | Clear session, start fresh |

### Language Switching

```
You:  /language hindi
Bot:  ✅ Language set to Hindi! Use /summary to regenerate in Hindi.

You:  Summarize in Tamil
Bot:  [Full summary in Tamil]

You:  हिंदी में समझाओ
Bot:  [Explanation in Hindi]
```

---

## Supported Languages

| Language | Command | Natural Trigger |
|---|---|---|
| English (default) | `/language english` | "in english" |
| Hindi | `/language hindi` | "in hindi", "हिंदी में" |
| Tamil | `/language tamil` | "in tamil", "தமிழில்" |
| Kannada | `/language kannada` | "in kannada", "ಕನ್ನಡದಲ್ಲಿ" |
| Telugu | `/language telugu` | "in telugu", "తెలుగులో" |
| Marathi | `/language marathi` | "in marathi", "मराठीत" |

---

## Error Handling

| Situation | Response |
|---|---|
| Invalid YouTube URL | Clear error + format examples |
| Transcripts disabled by creator | Explains why, suggests different video |
| No transcript/captions | Explains, suggests another video |
| Private/deleted video | Notifies user |
| Non-English video | Auto-translates transcript to English |
| Video >45k chars (very long) | Graceful truncation + note |
| Answer not in transcript | "⚠️ This topic is not covered in the video." |
| Question asked before URL | Prompts user to send a YouTube link |
| Gemini rate limit | Retries 3× with backoff |

---

## Cost Optimization

- **Gemini 2.0 Flash** — cheapest model that's still multilingual and capable
- **Transcript truncation** at 45k chars — prevents runaway token bills on long videos
- **Q&A uses only 8k chars** of transcript — reduces per-question cost
- **Temperature 0.3** — deterministic, less rambling = fewer output tokens
- **references/ loaded on-demand** — error/language docs only loaded when needed

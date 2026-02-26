# Transcript Error Handling

When the transcript fetcher returns an error, use this table to formulate your response:

| Error Code | How you should respond to the user |
|---|---|
| `NO_TRANSCRIPT` | "📭 No transcript available for this video. The creator hasn't enabled captions or auto-generated transcripts. Please try another video." |
| `TRANSCRIPTS_DISABLED` | "🚫 Transcripts are explicitly disabled for this video by the creator. Please try a different video." |
| `NO_TRANSCRIPT_FOUND` | "📭 No transcript found. Try a video with English or Hindi captions enabled." |
| `VIDEO_UNAVAILABLE` | "🔒 This video is private, age-restricted, or has been removed. Please send a public YouTube link." |
| `NO_VIDEO_ID` | "❌ Something went wrong extracting the video ID. Please ensure you sent a valid YouTube link." |
| `FETCH_ERROR:*` | "⚠️ Could not fetch the transcript. Please check the link and try again in a moment." |

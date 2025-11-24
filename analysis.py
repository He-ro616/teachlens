# backend/analysis.py
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
FILLER_WORDS = {"um","uh","like","you know","so","actually","right","okay","ok"}

def sentiment_scores(text):
    return analyzer.polarity_scores(text)

def wpm_from_transcript(text, audio_path=None):
    # approximate words per minute from transcript length and optional audio duration (ffprobe)
    words = len(text.split())
    if audio_path:
        try:
            # get audio duration via ffprobe
            import subprocess, json, shlex
            cmd = f'ffprobe -v quiet -print_format json -show_format "{audio_path}"'
            proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            data = json.loads(proc.stdout)
            dur = float(data["format"]["duration"])
            if dur > 0:
                return round(words / (dur / 60), 1)
        except Exception:
            pass
    # fallback assume 3 minutes if unknown
    return round(words / 3.0, 1)

def filler_count(text):
    lower = text.lower()
    count = 0
    for w in FILLER_WORDS:
        count += lower.count(w)
    return count

def lexical_diversity(text):
    words = re.findall(r"\w+", text.lower())
    if not words:
        return 0.0
    unique = len(set(words))
    return round(unique / len(words), 3)

def analyze_text(text):
    s = sentiment_scores(text)
    # compute scores (1-10)
    clarity_score = round(((s["compound"] + 1) / 2) * 10, 1)  # compound -1..1 -> 0..1 -> 0..10
    engagement_score = round((s["pos"] - s["neg"] + 0.5) * 10 / 1.5, 1)  # heuristic scaled
    # clamp
    clarity_score = max(1, min(10, clarity_score))
    engagement_score = max(1, min(10, engagement_score))

    strengths = []
    weaknesses = []
    suggestions = []

    if s["pos"] > 0.3:
        strengths.append("Generally positive / encouraging language")
    if s["neg"] < 0.2:
        strengths.append("Low negative phrasing")

    if s["neu"] > 0.6:
        weaknesses.append("High neutral content — may lack emotional engagement")
        suggestions.append("Add more interactive questions and expressive cues to increase engagement.")
    if filler_count(text) > 5:
        weaknesses.append(f"Filler words detected ({filler_count(text)}) — reduces clarity")
        suggestions.append("Reduce fillers by pausing intentionally between ideas.")

    if lexical_diversity(text) < 0.3:
        weaknesses.append("Limited lexical variety")
        suggestions.append("Use varied examples and vocabulary to explain concepts.")

    if not strengths:
        strengths.append("Clear wording in parts of the lesson")

    if not suggestions:
        suggestions.append("Encourage student interaction; add concrete examples; slow down for clarity if needed.")

    summary = ("This evaluation provides clarity and engagement scores based on transcript sentiment and speech patterns. "
               "Use the suggestions to improve interaction and explanation clarity.")

    return {
        "clarity_score": clarity_score,
        "engagement_score": engagement_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "summary": summary,
        "sentiment": s
    }

def compute_extra_metrics(text, audio_path):
    return {
        "wpm": wpm_from_transcript(text, audio_path),
        "filler_count": filler_count(text),
        "lexical_diversity": lexical_diversity(text)
    }

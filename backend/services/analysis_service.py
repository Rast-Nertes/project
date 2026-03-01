"""
Insight IS — AI Analysis Service
Sentiment analysis and impact scoring using Google Gemini AI.
"""

import json
from typing import Optional
from loguru import logger
import google.generativeai as genai

from settings.settings import settings

# Configure Gemini if key is provided
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    # Using gemini-1.5-flash as it's the fast, cost-effective model for this kind of task
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Fallback basic heuristic if API fails or key is missing
_POSITIVE = ["рост", "прибыль", "рекорд", "превысил", "позитивный", "growth", "profit", "bullish"]
_NEGATIVE = ["падение", "убыток", "снижение", "кризис", "drop", "loss", "decline", "bearish"]
_HIGH_IMPACT = ["ФРС", "ЦБ", "fed", "war", "война", "санкции", "запрет"]


def _fallback_analysis(text: str) -> dict:
    """Basic keyword analysis if AI fails."""
    text_lower = text.lower()
    
    pos_hits = sum(1 for kw in _POSITIVE if kw in text_lower)
    neg_hits = sum(1 for kw in _NEGATIVE if kw in text_lower)
    total = pos_hits + neg_hits
    
    sentiment = "neutral"
    raw_score = 0.0
    if total > 0:
        if pos_hits > neg_hits:
            sentiment = "positive"
            raw_score = pos_hits / total
        elif neg_hits > pos_hits:
            sentiment = "negative"
            raw_score = -(neg_hits / total)
            
    high_hits = sum(1 for kw in _HIGH_IMPACT if kw in text_lower)
    impact = "high" if high_hits >= 1 or total >= 5 else ("medium" if total >= 2 else "low")
    impact_score = 0.8 if impact == "high" else (0.4 + total * 0.05 if impact == "medium" else 0.1)
    
    return {
        "sentiment": sentiment,
        "sentiment_score": round(raw_score, 3),
        "impact": impact,
        "impact_score": min(round(impact_score, 3), 1.0),
        "confidence": min(0.5 + total * 0.05, 0.95),
        "summary": text[:200].strip(),
    }


def analyze_article(title: str, content: Optional[str] = None) -> dict:
    """
    Analyse an article using Google Gemini AI.
    Returns: {sentiment, impact, confidence, summary, sentiment_score, impact_score}
    """
    text = f"Title: {title}\n\nContent: {content or ''}"
    
    if not model:
        logger.warning("Gemini API key not found. Using fallback analysis.")
        return _fallback_analysis(text)

    prompt = f"""
    Analyze the following financial/economic news article. 
    You must respond ONLY with a valid JSON object matching this exact structure:
    {{
      "sentiment": "positive" | "negative" | "neutral",
      "sentiment_score": float between -1.0 (most negative) and 1.0 (most positive),
      "impact": "high" | "medium" | "low",
      "impact_score": float between 0.0 (no impact) and 1.0 (massive global impact),
      "confidence": float between 0.0 and 1.0 (how confident are you in this assessment),
      "summary": "String containing a concise 1-2 sentence summary of the news IN RUSSIAN LANGUAGE"
    }}

    Article Text:
    {text}
    """

    try:
        response = model.generate_content(prompt)
        # Extract JSON from the response (sometimes Gemini wraps it in markdown backticks)
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        ai_data = json.loads(result_text)
        
        # Ensure values are rounded properly
        return {
            "sentiment": ai_data.get("sentiment", "neutral"),
            "sentiment_score": round(float(ai_data.get("sentiment_score", 0.0)), 3),
            "impact": ai_data.get("impact", "low"),
            "impact_score": round(float(ai_data.get("impact_score", 0.1)), 3),
            "confidence": round(float(ai_data.get("confidence", 0.8)), 3),
            "summary": ai_data.get("summary", text[:200].strip()),
        }

    except Exception as e:
        logger.error(f"Gemini API analysis failed: {e}. Falling back to heuristics.")
        return _fallback_analysis(text)


analysis_service = type("AnalysisService", (), {"analyze": staticmethod(analyze_article)})()

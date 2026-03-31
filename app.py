# app.py — COMPLETE WORKING FILE
# Run with: python app.py

import os
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
# Load API key from .env file
if os.environ.get("RENDER") is None:
    load_dotenv()

# Create Claude client
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("❌ ANTHROPIC_API_KEY not found. Set it in environment variables.")

client = anthropic.Anthropic(api_key=api_key)
# ── PART 1: Prompt Builder (must be defined FIRST) ──────────────────────────
def build_prompt(reviews, platform):
    base = f"""
You are an expert digital marketing copywriter with 10+ years of experience.

Analyze these customer reviews and extract:
- Key emotions (joy, relief, frustration solved, surprise)
- Main pain points that were solved
- Specific benefits mentioned
- Trust signals (e.g., fast delivery, great quality)

Customer Reviews:
---
{reviews}
---
"""
    if platform == "all" or platform == "facebook":
        base += """
FACEBOOK AD (max 125 words):
Write an emotional, story-driven ad with a strong hook.
End with a clear call-to-action. Use emojis sparingly.
"""

    if platform == "all" or platform == "google":
        base += """
GOOGLE AD:
- Headline 1 (max 30 chars): [benefit-focused]
- Headline 2 (max 30 chars): [urgency or social proof]
- Description (max 90 chars): [clear value proposition]
"""

    if platform == "all" or platform == "email":
        base += """
EMAIL SUBJECT LINES (give 3 options):
- Option A: Curiosity-based
- Option B: Benefit-based
- Option C: Urgency-based
"""

    base += "\nFormat each section clearly with headers."
    return base


# ── PART 2: Claude API Call ──────────────────────────────────────────────────
def generate_ads_from_reviews(reviews_text, platform="all"):
    """
    Takes customer review text and generates ad copies.
    platform can be: "all", "facebook", "google", or "email"
    """
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": build_prompt(reviews_text, platform)
            }
        ]
    )
    return message.content[0].text


# ── PART 3: Flask Web Server ─────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow browser requests from any origin


# Route 1: Serve the HTML page
@app.route("/")
def home():
    # ✅ FIXED — forces UTF-8 so emojis load correctly
    return open("index.html", encoding="utf-8").read()


# Route 2: Generate ads from reviews
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    reviews  = data.get("reviews", "")
    platform = data.get("platform", "all")

    # Validation
    if not reviews or len(reviews.strip()) < 20:
        return jsonify({"error": "Please paste at least one full review."}), 400

    # Call Claude
    result = generate_ads_from_reviews(reviews, platform)
    return jsonify({"ads": result})


# ── START SERVER ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
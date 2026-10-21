
import os
import json
import re
import time
from urllib.parse import quote

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

from knowledge_base import STUDIO


# ==================================================
# 1. CONFIGURATION
# ==================================================

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.8-flash"
WHATSAPP_NUMBER = "918056644023"

client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)


# ==================================================
# 2. HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# 3. LOCAL KNOWLEDGE BASE ANSWERS
# These common questions do not call Gemini.
# ==================================================

def local_answer(message):
    msg = message.lower().strip()


    # Travel-related questions
    msg = message.lower()

    travel_keywords = [
        "travel", "travelling", "transport"
    ]

    extra_keywords = [
        "extra", "additional", "separate",
        "charge", "cost", "price", "pay",
        "included", "package"
    ]

    if any(word in msg for word in travel_keywords):
        if any(word in msg for word in extra_keywords):
            return (
                "Yes, travel charges are extra and are not included "
                "in the photography package. Travel, food, and stay "
                "expenses are charged separately, where applicable. "
                "Please contact the studio owner on WhatsApp to "
                "confirm the exact charges."
            )

        return (
            "Travel charges are separate from the photography package. "
            "Please contact the studio owner on WhatsApp for details."
        )

    # ----------------------------------------------
    # SERVICES
    # ----------------------------------------------

    if any(word in msg for word in [
        "service",
        "services",
        "what do you do",
        "what photography",
        "what do you offer",
        "list of services"
    ]):
        return (
            "📸 THI PHOTOGRAPHY SERVICES\n\n"
            "WEDDING & EVENTS\n"
            "• Wedding Photography\n"
            "• Reception Photography\n"
            "• Engagement Photography\n"
            "• Destination Wedding Photography\n"
            "• House Warming Photography\n"
            "• Birthday Party Photography\n\n"
            "COUPLE PHOTOGRAPHY\n"
            "• Pre-Wedding Shoot\n"
            "• Post-Wedding Shoot\n"
            "• Candid Photography\n"
            "• Outdoor Photography\n\n"
            "BABY & FAMILY PHOTOGRAPHY\n"
            "• Maternity Shoot\n"
            "• Baby and Children Photoshoots\n"
            "• Family Portraits\n"
            "• Baby Shower Photography\n"
            "• Naming Ceremony Photography\n"
            "• Ear Piercing Ceremony Photography\n"
            "• Head Tonsure Ceremony Photography\n"
            "• Puberty Ceremony Photography\n\n"
            "PHOTOGRAPHY & VIDEOGRAPHY\n"
            "• Traditional Photography\n"
            "• 4K Videography\n"
            "• Candid Videography\n"
            "• Model Shoot\n\n"
            "Customized service combinations are also possible.\n"
            "Which service are you interested in?"
        )

    # ----------------------------------------------
    # PRICE QUESTIONS
    # Check price before individual package answers.
    # ----------------------------------------------

    if any(word in msg for word in [
        "price",
        "prices",
        "pricing",
        "cost",
        "rate",
        "how much",
        "quotation",
        "quote",
        "budget"
    ]):
        return (
            "💰 PHOTOGRAPHY PRICING\n\n"
            "Package prices depend on your event, location, "
            "duration and selected services.\n\n"
            "• Basic Package\n"
            "• Premium Package\n"
            "• Customized Package\n\n"
            "The studio owner confirms the actual price. "
            "Please use the enquiry form to request a quotation."
        )

    # ----------------------------------------------
    # BASIC + PREMIUM COMPARISON
    # MUST COME BEFORE INDIVIDUAL PACKAGE CONDITIONS
    # ----------------------------------------------

    compare_packages = (
        ("basic" in msg and "premium" in msg)
        or "compare package" in msg
        or "compare packages" in msg
        or "all packages" in msg
        or "package inclusions" in msg
        or "basic and premium" in msg
        or "basic & premium" in msg
    )

    if compare_packages:
        return (
            "📦 OUR PHOTOGRAPHY PACKAGES\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "BASIC PACKAGE\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "• Traditional Photography\n"
            "• Unlimited Soft Copies\n"
            "• Traditional 4K Videography\n"
            "• Premium Album\n"
            "• 2 Frames\n"
            "• 1 Calendar\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "PREMIUM PACKAGE\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "• Traditional Photography with unlimited soft copies\n"
            "• Traditional 4K Videography\n"
            "• Candid Photography with unlimited soft copies\n"
            "• Candid Videography: teaser cut and highlights\n"
            "• Drone, subject to confirmation\n"
            "• Premium Album\n"
            "• 2 Frames\n"
            "• 1 Pendrive\n"
            "• Premium Album Bag\n"
            "• 1 Calendar\n"
            "• Complimentary Post-Wedding Shoot\n\n"
            "Both packages include soft copies according to "
            "the package terms. Extra copies beyond the included "
            "package may be chargeable.\n\n"
            "The owner confirms prices and final package details."
        )

    # ----------------------------------------------
    # CUSTOMIZED PACKAGE
    # ----------------------------------------------

    if "customized" in msg or "customised" in msg:
        return (
            "✨ CUSTOMIZED PACKAGE\n\n"
            "• Choose the photography services you need.\n"
            "• Combine photography and videography.\n"
            "• Request additional albums or frames at extra cost.\n"
            "• Discuss additional photographers or drone options.\n"
            "• Request a package based on your budget.\n"
            "• Short-duration coverage may be requested.\n\n"
            "The owner will confirm availability, final inclusions "
            "and the price."
        )

    # ----------------------------------------------
    # BASIC PACKAGE ONLY
    # ----------------------------------------------

    if "basic" in msg:
        return (
            "📦 BASIC PACKAGE\n\n"
            "• Traditional Photography\n"
            "• Unlimited Soft Copies\n"
            "• Traditional 4K Videography\n"
            "• Premium Album\n"
            "• 2 Frames\n"
            "• 1 Calendar\n\n"
            "Included soft copies are free according to package terms.\n"
            "The owner confirms the package price and final details."
        )

    # ----------------------------------------------
    # PREMIUM PACKAGE ONLY
    # ----------------------------------------------

    if "premium" in msg:
        return (
            "✨ PREMIUM PACKAGE\n\n"
            "• Traditional Photography with unlimited soft copies\n"
            "• Traditional 4K Videography\n"
            "• Candid Photography with unlimited soft copies\n"
            "• Candid Videography: teaser cut and highlights\n"
            "• Drone, subject to confirmation\n"
            "• Premium Album\n"
            "• 2 Frames\n"
            "• 1 Pendrive\n"
            "• Premium Album Bag\n"
            "• 1 Calendar\n"
            "• Complimentary Post-Wedding Shoot\n\n"
            "The owner confirms the package price and final terms."
        )

    # ----------------------------------------------
    # GENERAL PACKAGE QUESTION
    # ----------------------------------------------

    if "package" in msg or "packages" in msg:
        return (
            "📦 OUR PHOTOGRAPHY PACKAGES\n\n"
            "• Basic Package: traditional photography, 4K "
            "videography, premium album, 2 frames and 1 calendar.\n\n"
            "• Premium Package: traditional and candid photography, "
            "videography, album, frames and additional inclusions.\n\n"
            "• Customized Package: choose services according to "
            "your event and requirements.\n\n"
            "Ask about a specific package to see its inclusions. "
            "The owner confirms the actual price."
        )

    # ----------------------------------------------
    # BOOKING QUESTIONS
    # ----------------------------------------------

    if any(word in msg for word in [
        "booking",
        "book",
        "availability",
        "available date",
        "reserve",
        "appointment"
    ]):
        return (
            "🗓️ BOOKING ENQUIRY\n\n"
            "Please complete the Photography Enquiry Form.\n\n"
            "Details required:\n"
            "• Your name\n"
            "• Phone number\n"
            "• Event type and date\n"
            "• Event location\n"
            "• Preferred package\n\n"
            "The owner must confirm date availability, price "
            "and booking. Your booking is not confirmed until "
            "the owner approves it."
        )

    # ----------------------------------------------
    # LOCATION AND TRAVEL
    # ----------------------------------------------

    if any(word in msg for word in [
        "location",
        "where are you",
        "travel",
        "destination",
        "travel charges"
    ]):
        return (
            "📍 LOCATION & TRAVEL\n\n"
            "• Based in Aruppukottai, Tamil Nadu.\n"
            "• Photography services are available across India.\n"
            "• International travel can be requested.\n"
            "• For outdoor and destination shoots, customers arrange "
            "travel, food and accommodation.\n"
            "• Travel charges are not included.\n\n"
            "Please share your event location in the enquiry form."
        )

    # ----------------------------------------------
    # INSTAGRAM PORTFOLIO
    # ----------------------------------------------

    if any(word in msg for word in [
        "instagram",
        "portfolio",
        "sample photos",
        "sample pictures"
    ]):
        return (
            "📸 THI PHOTOGRAPHY PORTFOLIO\n\n"
            "View our work on Instagram:\n"
            "https://www.instagram.com/thi_clicks/\n\n"
            "You can contact us through the enquiry form "
            "to discuss your event."
        )

    # No local answer found
    return None


# ==================================================
# 4. CLEAN GEMINI FORMATTING
# ==================================================

def clean_reply(text):
    if not text:
        return ""

    # Remove Markdown headings
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)

    # Remove bold and italic markers
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)

    # Remove inline code markers
    text = text.replace("`", "")

    return text.strip()


# ==================================================
# 5. CHATBOT API
# ==================================================

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({
            "reply": "Please enter a valid text message."
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "reply": "Please enter your question."
        }), 400

    if len(message) > 1000:
        return jsonify({
            "reply": "Please keep your message under 1000 characters."
        }), 400

    # Answer known questions immediately
    answer = local_answer(message)

    if answer:
        return jsonify({
            "reply": answer,
            "source": "knowledge_base"
        }), 200

    # Fallback if Gemini is not configured
    if client is None:
        return jsonify({
            "reply": (
                "I can help with photography services, packages, "
                "soft copies and booking enquiries. Please try one "
                "of the quick questions or use the enquiry form."
            )
        }), 200

    prompt = f"""
You are SnapAssist, the customer enquiry assistant for Thi Photography.

VERIFIED STUDIO INFORMATION:
{json.dumps(STUDIO, ensure_ascii=False, indent=2)}

RULES:
1. Answer the customer's exact question first.
2. Use only verified studio information.
3. Use simple, friendly and professional English.
4. Put each list item on its own line.
5. Use short headings for services and package inclusions.
6. Do not output Markdown symbols such as **, ## or backticks.
7. Keep ordinary answers to 2–5 short sentences.
8. Never invent prices, discounts, availability or inclusions.
9. Basic and Premium packages include soft copies at no extra
   charge according to package terms.
10. Extra copies beyond package inclusions may be chargeable.
11. Only customer-selected photos are edited for the album.
12. The owner confirms prices and date availability.
13. Never claim a booking is confirmed without owner approval.
14. For booking enquiries, guide the customer to the enquiry form.
15. Do not send every question to the owner when verified information
    already answers it.
16. If information is unknown, say the owner must confirm it.
17. For unrelated questions, politely guide the customer back to
    photography services and enquiries.

CUSTOMER QUESTION:
{message}
"""

    try:
        response = None

        # Retry temporary service-unavailable errors
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config={"max_output_tokens": 700}
                )
                break

            except Exception as error:
                error_text = str(error).upper()

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                ):
                    if attempt < 2:
                        time.sleep(1 + attempt)
                        continue

                raise

        reply = clean_reply(response.text if response else "")

        if reply:
            return jsonify({
                "reply": reply,
                "source": "gemini"
            }), 200

        return jsonify({
            "reply": "I couldn't generate an answer. Please try again."
        }), 200

    except Exception:
        app.logger.exception("Gemini API request failed")

        return jsonify({
            "reply": (
                "I'm unable to answer that question right now. "
                "You can still ask about services, packages or soft copies."
            )
        }), 200


# ==================================================
# 6. WHATSAPP ENQUIRY FORM
# ==================================================

@app.route("/submit-enquiry", methods=["POST"])
def submit_enquiry():
    data = request.get_json(silent=True) or {}

    required_fields = {
        "name": "Name",
        "phone": "Phone number",
        "event_type": "Event type",
        "event_date": "Event date",
        "location": "Event location",
        "package": "Preferred package"
    }

    details = {}

    for key, label in required_fields.items():
        value = data.get(key, "")

        if not isinstance(value, str):
            value = ""

        value = value.strip()

        if not value:
            return jsonify({
                "error": f"Please enter {label.lower()}."
            }), 400

        if len(value) > 200:
            return jsonify({
                "error": f"{label} is too long."
            }), 400

        details[key] = value

    # Validate phone number
    phone_digits = re.sub(r"\D", "", details["phone"])

    if not 10 <= len(phone_digits) <= 15:
        return jsonify({
            "error": "Please enter a valid phone number."
        }), 400

    requirements = data.get("requirements", "")

    if not isinstance(requirements, str):
        requirements = ""

    requirements = requirements.strip()[:500]

    whatsapp_message = (
        "Hello Thi Photography! I would like to enquire about a booking.\n\n"
        f"Name: {details['name']}\n"
        f"Phone: {details['phone']}\n"
        f"Event: {details['event_type']}\n"
        f"Date: {details['event_date']}\n"
        f"Location: {details['location']}\n"
        f"Preferred package: {details['package']}\n"
        f"Additional requirements: {requirements or 'Not specified'}\n\n"
        "Please confirm availability, pricing and package details."
    )

    whatsapp_url = (
        f"https://wa.me/{WHATSAPP_NUMBER}"
        f"?text={quote(whatsapp_message)}"
    )

    return jsonify({
        "whatsapp_url": whatsapp_url
    }), 200


# ==================================================
# 7. RUN FLASK
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)

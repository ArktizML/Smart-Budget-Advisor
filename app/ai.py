from flask import Blueprint, request, jsonify, session, render_template
from groq import Groq
from .storage import load_data
import os
from dotenv import load_dotenv

load_dotenv()

airoute = Blueprint("airoute", __name__)
api_key=os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

@airoute.route("/ai_chat", methods=["POST"])
def ai_chat():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # load expenses
    all_expenses = load_data()

    user_id = session["user_id"]
    user_expenses = [e for e in all_expenses if e["user_id"] == user_id]

    # convert to readable summary
    expense_summary = "\n".join(
        f"- {e['date']} | {e['category']} | {e['amount']} zł | {e['description']}"
        for e in user_expenses
    ) or "User has no expenses."

    system_prompt = f"""
You are a financial advisor AI.
You analyze the user's expenses and give practical, actionable advice.

User's expenses:
{expense_summary}

Rules:
- Be concise but concrete.
- Provide insights, not generic fluff.
- Use numbers from the user’s data.
- Identify trends, risks, overspending, opportunities.
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    reply = completion.choices[0].message.content
    return jsonify({"reply": reply})

@airoute.route("/ai_chat", methods=["GET"])
def ai_chat_page():
    return render_template("ai_chat.html")
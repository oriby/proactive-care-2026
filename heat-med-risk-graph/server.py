"""
Optional local server for the Heat-Medication Risk Graph demo.

Not required to run the app — index.html works fine on its own by double-clicking it
(the "Generate explanation" button will just show the constructed prompt instead of a
real model response).

Run this only if you want the "Generate explanation" button to call a real LLM:

    pip install -r requirements.txt
    cp .env.example .env        # then paste your API key into .env
    python server.py
    open http://localhost:5050

Swap in whichever provider you have a key for — Anthropic is wired by default below.
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, static_folder=".")
CORS(app)  # allow the page to call this from file:// or http://localhost

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/summarize", methods=["POST"])
def summarize():
    body = request.get_json(force=True) or {}
    prompt = body.get("prompt", "")
    context = body.get("context", "")

    if not prompt:
        return jsonify({"error": "missing prompt"}), 400

    # The UI shows only the bare prompt; the retrieved patient facts arrive separately as `context`.
    prompt = f"{prompt}\n\n{context}" if context else prompt

    if not ANTHROPIC_API_KEY:
        return jsonify({
            "explanation": "No ANTHROPIC_API_KEY configured on the server. "
                            "Add one to .env and restart server.py to get a real generated explanation. "
                            "Meanwhile, here is the prompt you can paste into any assistant:\n\n" + prompt
        })

    try:
        import urllib.request

        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "content-type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        explanation = "\n".join(text_blocks) if text_blocks else "(model returned no text)"
        return jsonify({"explanation": explanation})

    except Exception as e:
        return jsonify({"explanation": f"LLM call failed ({e}). Here is the prompt to paste manually:\n\n{prompt}"})


if __name__ == "__main__":
    app.run(port=5050, debug=True)

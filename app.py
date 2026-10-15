import re, joblib
from flask import Flask, request, jsonify, send_from_directory
from features import extract, reasons

app = Flask(__name__, static_folder="static")
model = joblib.load("model.joblib")

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return r

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/check", methods=["POST", "OPTIONS"])
def check():
    if request.method == "OPTIONS": return "", 204
    text = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not text:
        return jsonify(error="No link provided"), 400
    # QR codes may hold plain text; find the first link-looking part
    m = re.search(r"(https?://\S+|(?:[\w-]+\.)+[a-z]{2,}\S*)", text, re.I)
    if not m:
        return jsonify(error="This does not look like a link", raw=text[:200]), 422
    url = m.group(1)
    p = float(model.predict_proba([extract(url)])[0][1])
    verdict = "phishing" if p >= 0.7 else "suspicious" if p >= 0.4 else "safe"
    return jsonify(url=url, verdict=verdict, risk=round(p * 100),
                   reasons=[{"level": l, "text": t} for l, t in reasons(url)])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    text = data.get("text", "")

    result = {
        "prediction": "Fake" if len(text) % 2 == 0 else "Real",
        "confidence": "0.85"
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)


import sys
import os

# Add the project root to Python path so it can find 'models' and 'utils'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, render_template, request, jsonify
from models.fake_news_model import FakeNewsModel
from models.deepfake_model import DeepfakeModel
from utils.credibility import compute_credibility

# Configure Flask to use the frontend folder
app = Flask(__name__, 
            template_folder=os.path.join(project_root, 'frontend'),
            static_folder=os.path.join(project_root, 'frontend'),
            static_url_path='')

# Initialize models
fake_news_model = FakeNewsModel()
deepfake_model = DeepfakeModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get text and file from frontend
    text = request.form.get('text', '')
    file = request.files.get('file', None)
    
    print(f"Received text: {text[:50]}...")  # Debug
    print(f"Received file: {file}")  # Debug

    # 1️⃣ Text analysis
    text_score, suspicious_phrases = fake_news_model.predict(text)

    # 2️⃣ Media analysis
    media_score, manipulated_regions = None, None
    if file and file.filename:
        print(f"Analyzing file: {file.filename}")
        media_score, manipulated_regions = deepfake_model.predict(file)
    else:
        print("No file uploaded")

    # 3️⃣ Compute final credibility
    final_score = compute_credibility(text_score, media_score)

    # 4️⃣ Return JSON response
    response = {
        'credibility_score': final_score,
        'text_score': text_score,
        'suspicious_phrases': suspicious_phrases,
        'media_score': media_score,
        'manipulated_regions': manipulated_regions
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
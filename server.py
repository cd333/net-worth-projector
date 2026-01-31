from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Get API key from environment variable (for security in production)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBnBeq-SU03tBwFM_hPDWPNiFHa_uVwURo')
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/parse-event', methods=['POST'])
def parse_event():
    try:
        data = request.json
        event_text = data.get('eventText', '')
        
        if not event_text:
            return jsonify({'error': 'No event text provided'}), 400
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Extract the following information from this financial event description:
"{event_text}"

Return ONLY a JSON object with these fields:
- year: the year number (integer)
- amount: the dollar amount (negative for expenses, positive for income)
- description: brief description

Example output: {{"year": 3, "amount": -80000, "description": "car purchase"}}

Return only the JSON, no other text."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return jsonify({'result': response_text})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
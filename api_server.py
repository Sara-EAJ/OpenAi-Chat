from flask import Flask, request, jsonify
import json
from start import get_chatbot_answer, load_data

app = Flask(__name__)

# تحميل البيانات عند بداية السيرفر
ARABIC_DATA_PATH = r'C:\Users\sarae\OneDrive\Pictures\Camera Roll\Documents\COOP Project\OpenAi\places_data.json'
ENGLISH_DATA_PATH = r'C:\Users\sarae\OneDrive\Pictures\Camera Roll\Documents\COOP Project\OpenAi\Englishplaces_data.json'
arabic_data, english_data = load_data(ARABIC_DATA_PATH, ENGLISH_DATA_PATH)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_question = data.get("question", "")
        if not user_question:
            return jsonify({"error": "No question provided"}), 400

        answer = get_chatbot_answer(user_question, arabic_data, english_data)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
        app.run(debug=True)

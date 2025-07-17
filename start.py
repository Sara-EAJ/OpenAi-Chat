import openai
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def detect_language(text):
    return 'ar' if re.search(r'[\u0600-\u06FF]', text) else 'en'

def load_data(arabic_path, english_path):
    with open(arabic_path, 'r', encoding='utf-8') as f:
        arabic_data = json.load(f)
    with open(english_path, 'r', encoding='utf-8') as f:
        english_data = json.load(f)
    return {'ar': arabic_data, 'en': english_data}

def filter_relevant_place(question, data):
    q_lower = question.lower()
    for place in data:
        for key in ['Place', 'City', 'Story', 'Summary']:
            if key in place and place[key].lower() in q_lower:
                return [place]
    return []

def is_prohibited_topic(question):
    prohibited_keywords = [
        'القرآن', 'آية', 'سورة', 'أحاديث', 'حديث', 'البخاري', 'مسلم',
        'حديث شريف', 'ما صحة', 'تفسير', 'إسناد', 'راوي',
        'quran', 'hadith', 'prophet said', 'sahih', 'bukhari', 'muslim', 'verse'
    ]
    q_lower = question.lower()
    for kw in prohibited_keywords:
        if kw in q_lower:
            return True
    return False

def build_prompt(question, data, lang):
    data_str = json.dumps(data, ensure_ascii=False)
    
    if lang == 'ar':
        return f"""
أنت مساعد ذكي مخصص فقط للإجابة عن الأسئلة المتعلقة بالأماكن النبوية والتاريخية داخل المملكة العربية السعودية، باستخدام المعلومات الموجودة في بيانات JSON التالية فقط:

التعليمات:
- لا ترد على أسئلة عن القرآن أو الأحاديث أو أي موضوع ديني خارج الأماكن.
- لا تخرج عن المعلومات المتوفرة.
- أجب بالفصحى فقط.

---

البيانات:
{data_str}

---

سؤال المستخدم:
{question}

أجب فقط بناءً على المعلومات أعلاه.
"""
    else:
        return f"""
You are a smart assistant designed to answer **only** questions about historical and prophetic places in Saudi Arabia based on the following JSON data.

Instructions:
- Do NOT answer anything related to Quran, Hadith, or religious interpretation.
- Only respond based on the provided data.
- Answer in formal English.

---

DATA:
{data_str}

---

User Question:
{question}

Respond only based on the data above.
"""

def get_chatbot_answer(user_question, all_data, model="gpt-4o-mini"):
    lang = detect_language(user_question)
    
    if is_prohibited_topic(user_question):
        return "عذرًا، لا أستطيع الإجابة عن هذا السؤال لأنه خارج نطاق المعلومات المسموح بها." if lang == 'ar' \
            else "Sorry, I cannot answer this question as it's outside the allowed topics."

    data = all_data.get(lang, [])

    matched = filter_relevant_place(user_question, data)
    if not matched:
        return "عذرًا، لا أستطيع الإجابة عن هذا السؤال لأنه خارج نطاق المعلومات المتوفرة لدي." if lang == 'ar' \
            else "Sorry, I can't answer that question because it's outside the scope of my data."

    prompt = build_prompt(user_question, matched, lang)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Assistant for prophetic and historical locations only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=700
    )

    return response['choices'][0]['message']['content'].strip()

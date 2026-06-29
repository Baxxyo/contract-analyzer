from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
import os
import json
import re

app = Flask(__name__, static_folder='static')
CORS(app)

# تهيئة عميل جوجل (سيقوم تلقائياً بجلب المفتاح من متغير البيئة GEMINI_API_KEY)
client = genai.Client()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    contract_text = data.get('text', '')
    options = data.get('options', [])

    if not contract_text.strip():
        return jsonify({'error': 'لم يتم إرسال نص العقد'}), 400

    prompt = f"""أنت محلل قانوني متخصص في لوائح البنك المركزي السعودي (ساما) وعقود البنوك السعودية.

قم بتحليل العقد التالي وإرجاع النتائج بصيغة JSON فقط بدون أي نص إضافي أو backticks.

نطاق التحليل: {', '.join(options)}

العقد:
\"\"\"
{contract_text[:8000]}
\"\"\"

أرجع JSON بهذا الشكل بالضبط:
{{
  "score": <رقم 0-100 يمثل نسبة الامتثال>,
  "scoreLabel": "<وصف: ممتاز/جيد/يحتاج مراجعة/خطر>",
  "scoreColor": "<gold أو green أو yellow أو red>",
  "contractTitle": "<نوع العقد>",
  "issues": [
    {{
      "level": "<high أو medium أو low>",
      "title": "<عنوان المشكلة>",
      "description": "<شرح سبب الخطورة>",
      "samaRef": "<رقم أو اسم لائحة ساما>"
    }}
  ]
}}

قواعد: high=مخالفة صريحة للوائح ساما، medium=غموض أو خطر محتمل، low=توصية للتحسين.
أعطِ على الأقل 5 نتائج من مستويات مختلفة."""

    try:
       #  الكود الصحيح
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
        
        # استخراج النص المسترجع من النموذج
        raw = response.text
        clean = re.sub(r'```json|```', '', raw).strip()
        result = json.loads(clean)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

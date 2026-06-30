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
        # استدعاء نموذج جيميناي فلاش بالمسافات الصحيحة للداخل
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


# ---- أكواد نظام الحسابات الجديد ----
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/login.html')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/signup.html')
def signup_page():
    return send_from_directory('static', 'signup.html')

# المسار الاحتياطي لحل مشكلة التوجيه لمنع ظهور خطأ Not Found 404
@app.route('/index.html')
def index_backup():
    return send_from_directory('static', 'index.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'error': 'جميع الحقول مطلوبة'}), 400
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO site_users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'تم إنشاء الحساب بنجاح!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'اسم المستخدم مسجّل مسبقاً'}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM site_users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'message': 'تم تسجيل الدخول بنجاح!', 'user': username}), 200
    return jsonify({'error': 'البيانات غير صحيحة'}), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
# محلل العقود الذكي - بنك الإنماء

## هيكل المشروع
```
project/
├── app.py
├── requirements.txt
└── static/
    └── index.html
```

## طريقة التشغيل

### 1. ثبّتي المكتبات
```bash
pip install -r requirements.txt
```

### 2. ضعي الـ API Key
**Windows:**
```cmd
set ANTHROPIC_API_KEY=sk-ant-xxxxxx
```
**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxx
```

### 3. شغّلي السيرفر
```bash
python app.py
```

### 4. افتحي المتصفح
```
http://localhost:5000
```

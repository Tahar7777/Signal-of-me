# Bybit Signal Scanner

أداة تداول تحليلية تعرض إشارات صفقات قصيرة (15 دقيقة) لعقود Bybit USDT عبر واجهة ويب.

## الملفات المطلوبة

- main.py
- requirements.txt
- Procfile
- templates/signals.html

## طريقة التشغيل على Render

- ارفع كل الملفات كما هي في المستودع.
- تأكد أن مجلد `templates` بجانب ملف `main.py` ويحتوي على ملف `signals.html`.
- اختر "Web Service" عند الإنشاء.
- أمر التشغيل سيكون تلقائياً `web: gunicorn main:app --bind 0.0.0.0:$PORT` بفضل الـ Procfile.
- زر "تحديث الإشارات" في الصفحة يعيد التحليل ويعرض أحدث النتائج.

---

## المميزات
- تحليل فوري لكل الأزواج
- يعتمد على مؤشرات فنية قوية
- واجهة Bootstrap أنيقة

# Byte Buddy

เกมทายคำศัพท์คอมพิวเตอร์ภาษาอังกฤษจากคำถามและคำใบ้ภาษาไทย ผู้เล่นเริ่มด้วยการใส่ชื่อ เลือกด่าน และเลือกระดับความยาก 3 ระดับ ผ่านด่านเพื่อปลดล็อกเส้นทางถัดไป

คำถามสุ่มจากคลังที่แยกตามความยาก แต่ละคลังมี 5 ข้อและจะไม่วนซ้ำจนกว่าจะใช้ครบ ตอบแต่ละข้อด้วยตัวเลือก A–D ซึ่งสุ่มตัวลวงจากคลังระดับเดียวกัน กติกาและ API ใช้ Python/Flask ส่วนหน้าเว็บแยกเป็น HTML, CSS และ JavaScript

## เริ่มเล่น

ต้องมี Python 3.9 ขึ้นไป

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

เปิด `http://127.0.0.1:5000` ในเบราว์เซอร์

## ทดสอบ

```powershell
py -m unittest discover -s tests -v
```

## ไฟล์หลัก

- `app.py` เว็บเซิร์ฟเวอร์และ API
- `game.py` คลังคำถามตามระดับ กติกาคะแนน และความคืบหน้าด่าน
- `index.html` โครงหน้าเกม
- `static/arcade.css` รูปแบบและการจัดวาง
- `static/arcade.js` การโต้ตอบและเปลี่ยนหน้าจอในเบราว์เซอร์
- `tests/test_game.py` การทดสอบกติกาและคลังคำถาม
- `tests/test_app.py` การทดสอบ API และการปลดล็อกด่าน

## เริ่มใช้ Git

```powershell
git init
git add .
git commit -m "Build Byte Buddy word guessing game"
```
# Byte Buddy

เกมทายคำศัพท์คอมพิวเตอร์ภาษาอังกฤษจากคำถามและคำใบ้ภาษาไทย ผู้เล่นเริ่มด้วยการใส่ชื่อ เลือกด่าน และเลือกระดับความยาก 3 ระดับ ผ่านด่านเพื่อปลดล็อกเส้นทางถัดไป เว็บเล่นบน GitHub Pages ได้โดยใช้ JavaScript และบันทึกความคืบหน้าไว้ในเบราว์เซอร์

คำถามสุ่มจากคลังที่แยกตามความยากใน `static/questions.json` แต่ละคลังมี 5 ข้อและจะไม่วนซ้ำจนกว่าจะใช้ครบ ตอบแต่ละข้อด้วยตัวเลือก A–D ซึ่งสุ่มตัวลวงจากคลังระดับเดียวกัน เลือกความยากครั้งเดียวต่อด่าน ระบบจะจำค่าเดิมเมื่อกลับมาเล่นด่านนั้นอีก

## Preview ในเครื่อง

ต้องมี Python 3.9 ขึ้นไป เปิด PowerShell ที่โฟลเดอร์โปรเจกต์แล้วรัน:

```powershell
py -m http.server 8000
```

เปิด `http://127.0.0.1:8000` ในเบราว์เซอร์ ไม่ต้องติดตั้ง package สำหรับหน้าเกม static

## เผยแพร่ด้วย GitHub Pages

1. Push repository นี้ขึ้น GitHub
2. เปิดหน้า repository แล้วไปที่ **Settings > Pages**
3. ใน **Build and deployment** เลือก **Deploy from a branch**
4. เลือก branch ที่ push ไว้ (เช่น `main` หรือ `master`) และ folder `/(root)` แล้วกด **Save**
5. รอ GitHub แสดง URL ของเว็บไซต์ในหน้า Pages

หน้า GitHub Pages ใช้ไฟล์ static เท่านั้น; ส่วนเว็บไม่เรียก Flask API และเก็บชื่อ คะแนน และด่านไว้ใน `localStorage` ของเบราว์เซอร์ ผู้เล่นจะเห็นคำตอบใน source ของเว็บได้ เพราะ GitHub Pages ไม่มี backend สำหรับซ่อนเฉลย

## Python API และ Tests

GitHub Pages ไม่ได้ใช้ Flask แต่ยังเปิด API สำหรับทดสอบในเครื่องได้:

```powershell
py -m pip install -r requirements.txt
py app.py
```

รันทดสอบ logic/API:

```powershell
py -m unittest discover -s tests -v
```

## ไฟล์หลัก

- `app.py` เว็บเซิร์ฟเวอร์และ API
- `game.py` คลังคำถามตามระดับ กติกาคะแนน และความคืบหน้าด่าน
- `index.html` โครงหน้าเกม
- `static/questions.json` คลังคำถามสำหรับ GitHub Pages
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
import os
import sys
import time
import traceback
from flask import Flask, request, jsonify

# បង្ខំ Server ឱ្យដើរម៉ោងស្រុកខ្មែរ
os.environ['TZ'] = 'Asia/Phnom_Penh'
time.tzset()

path = '/home/dramaflix/mysite'
if path not in sys.path:
    sys.path.insert(0, path)

# ហៅ Package ផ្លូវការមកប្រើ (លែងគាំងទៀតហើយ)
from bakong_khqr import KHQR

app = Flask(__name__)
app.config["DEBUG"] = True

# Token បាកងរបស់មេ
MY_TOKEN = "rbkGgBjB2q5EmMkSXSmMrlpi0n1vF3HYjx30GKZ4DC5yGA"
khqr = KHQR(MY_TOKEN)

@app.route('/')
def index():
    return "<h1>✅ DramaFlix API (Official SDK) is Running!</h1>"

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        data = request.json or {}
        raw_uid = data.get('uid', 'UNKNOWN')
        short_uid = raw_uid[:8] if len(raw_uid) > 8 else raw_uid
        bill_num = f"VIP{short_uid}" 

        # ----------------------------------------------------
        # ប្រើតាមស្តង់ដារ Document ថ្មី (v0.5.7) 
        # (🔴 កុំភ្លេចដូរ Bakong ID ដាក់របស់មេពិតប្រាកដ)
        # ----------------------------------------------------
        qr_string = khqr.create_qr(
            bank_account="monsela@aclb",      # 🔴 ដូរជា Bakong ID មេ
            merchant_name="MON SELA",         # 🔴 ឈ្មោះមេ (អក្សរធំ)
            merchant_city="PHNOM PENH",      
            amount=1.0,                       # លុយ ១ ដុល្លារ
            currency="USD",                   # (បើកុងលុយរៀល ដូរដាក់ KHR ហើយ amount ដាក់ 4000)
            store_label="DRAMAFLIX",         
            phone_number="85512345678",       # លេខទូរស័ព្ទត្រូវតែមាន 855 ពីមុខ
            bill_number=bill_num,            
            terminal_label="APP",            
            static=False,
            expiration=10                     # 🔴 មុខងារថ្មី៖ កំណត់ឱ្យ QR មានសុពលភាព ១០ នាទី
        )
        
        md5_hash = khqr.generate_md5(qr_string)
        
        return jsonify({
            "status": "success", 
            "qr_string": qr_string, 
            "md5": md5_hash
        })
        
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"QR Error: {error_msg}") 
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/check_status', methods=['POST'])
def check_status():
    try:
        data = request.json or {}
        md5 = data.get('md5')
        
        if not md5: 
            return jsonify({"status": "error", "message": "បាត់ MD5"}), 400
        
        status = khqr.check_payment(md5) 
        return jsonify({"status": status})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/test_api')
def test_api():
    try:
        # តេស្តឆែកមើលលុយដោយប្រើ MD5 ក្លែងក្លាយ
        status = khqr.check_payment("1234567890abcdef")
        return f"<h1>✅ ជោគជ័យ! Server អាចឆ្លងដែនទៅសួរ Bakong API បានហើយ! (លទ្ធផល: {status})</h1>"
    except Exception as e:
        return f"<h1>❌ Error ភ្ជាប់ទៅធនាគារ៖ {e}</h1>"

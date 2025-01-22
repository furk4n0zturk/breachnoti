from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# API Anahtarları ve izin verilen domainler
AUTHORIZED_KEYS = {
    "apikey123456": [""],  # Bu anahtar sadece mu.edu.tr ve example.com domainleri için sorgu atabilir
    "apikeyabcdef": ["anotherdomain.com"]          # Bu anahtar sadece anotherdomain.com için sorgu atabilir
}

# Veritabanı bağlantı bilgileri
DB_HOST = "localhost"
DB_USER = "db_user"
DB_PASS = "12345678**"
DB_NAME = "breached_db"

# Veritabanına bağlanma
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Yetkilendirme kontrolü
def check_api_key(api_key):
    return api_key in AUTHORIZED_KEYS

# Domain izni kontrolü
def check_domain_permission(api_key, domain):
    allowed_domains = AUTHORIZED_KEYS.get(api_key, [])
    return domain in allowed_domains

# API endpoint: Veri çekme
@app.route('/get-data', methods=['POST'])
def get_data():
    # API anahtarını kontrol et
    api_key = request.headers.get('Authorization')
    if not api_key or not check_api_key(api_key):
        return jsonify({"error": "Unauthorized"}), 401

    # Domain bilgisini al
    data = request.get_json()
    domain = data.get("domain")
    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    # Domain izni kontrol et
    if not check_domain_permission(api_key, domain):
        return jsonify({"error": f"Access to domain '{domain}' is not allowed for this API key"}), 403

    # Veritabanından veri çek
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email LIKE %s"
            cursor.execute(sql, ('%' + domain,))
            result = cursor.fetchall()
        return jsonify({"data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()

# API çalıştırma
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

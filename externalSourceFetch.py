import os
import requests
import pymysql
from dotenv import load_dotenv

# .env dosyasını yükleme
load_dotenv()

# Dehashed API bilgileri
EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN")
DEHASHED_URL = f"{os.getenv('DEHASHED_URL')}\'{EMAIL_DOMAIN}\'"
DEHASHED_USER = os.getenv("DEHASHED_USER")
DEHASHED_PASS = os.getenv("DEHASHED_PASS")

# Veritabanı bağlantı bilgileri
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Dehashed API'den veri çekme
def fetch_data():
    response = requests.get(
        DEHASHED_URL,
        auth=(DEHASHED_USER, DEHASHED_PASS),
        headers={"Accept": "application/json"}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Veriyi veritabanına yazma
def update_database(entries):
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            for entry in entries:
                email = entry.get("email", "")
                username = entry.get("username", "")
                database_name = entry.get("database_name", "")
                id_value = entry.get("id", "")

                # Veriyi ekleme veya güncelleme sorgusu
                sql = """
                INSERT INTO users (id, email, username, database_name)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    email = VALUES(email),
                    username = VALUES(username),
                    database_name = VALUES(database_name);
                """
                cursor.execute(sql, (id_value, email, username, database_name))
            
            # Değişiklikleri kaydet
            connection.commit()

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

# Main iş akışı
def main():
    data = fetch_data()
    if data and "entries" in data:
        update_database(data["entries"])
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()

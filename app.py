from flask import Flask, Response, request
import pymysql
import json
import os

app = Flask(__name__)

# TOKEN
TOKEN = "profe123"

# 🔌 Conexión a Railway MySQL
def get_connection():
    try:
        connection = pymysql.connect(
            host="caboose.proxy.rlwy.net",
            port=48033,
            user="root",
            password="WCgIxNYZwDigbFRCaOsXANJOTHyBVAUl",
            database="railway",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        return connection
    except Exception as e:
        print("❌ ERROR CONECTANDO A MYSQL:", e)
        raise

@app.route("/")
def index():
    token = request.args.get("token")

    if token != TOKEN:
        return {"error": "No autorizado"}, 401

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM universidades LIMIT 5;")
        data = cursor.fetchall()
        conn.close()

        return data

    except Exception as e:
        return {"error": str(e)}, 500

# 🚀 Render usa esto automáticamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
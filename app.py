from flask import Flask, Response, request
import pymysql
import json
import os
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = "clave_super_segura_123"

# conexión a railway
def get_connection():
    connection = pymysql.connect(
        host="caboose.proxy.rlwy.net",
        port=48033,
        user="root",
        password="WCgIxNYZwDigbFRCaOsXANJOTHyBVAUl",
        database="railway",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


# generar token
@app.route("/login")
def login():

    payload = {
        "user": "cristal",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "token": token
    }


# endpoint principal
@app.route("/")
def index():

    token = request.args.get("token")

    if not token:
        return {"error": "Token requerido"}, 401

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return {"error": "Token inválido o expirado"}, 401

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        u.id as universidad_id,
        u.nombre as universidad,
        u.tipo_institucion,
        u.modalidad,
        c.nombre as ciudad,
        e.nombre as estado,
        ca.nombre as carrera
    FROM universidades u
    JOIN ciudades c ON u.ciudad_id = c.id
    JOIN estados e ON c.estado_id = e.id
    LEFT JOIN universidad_carreras uc ON u.id = uc.universidad_id
    LEFT JOIN carreras ca ON uc.carrera_id = ca.id
    WHERE u.publicado = TRUE
    ORDER BY u.id DESC
    """

    cursor.execute(query)
    resultados = cursor.fetchall()

    conn.close()

    universidades = {}

    for fila in resultados:

        uid = fila["universidad_id"]

        if uid not in universidades:
            universidades[uid] = {
                "nombre": fila["universidad"],
                "ciudad": fila["ciudad"],
                "estado": fila["estado"],
                "tipo": fila["tipo_institucion"],
                "modalidad": fila["modalidad"],
                "carreras": []
            }

        if fila["carrera"]:
            universidades[uid]["carreras"].append(fila["carrera"])

    return Response(
        json.dumps(list(universidades.values()), indent=4, ensure_ascii=False),
        mimetype="application/json"
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
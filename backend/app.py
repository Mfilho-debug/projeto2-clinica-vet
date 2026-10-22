import os
import datetime
import pymysql
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)


def get_conn():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "clinica"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=5,
    )


def clean(row):
    return {k: (v.isoformat() if isinstance(v, (datetime.date, datetime.datetime)) else v)
            for k, v in row.items()}


def query(sql, params=(), one=False, write=False):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if write:
                return cur.lastrowid, cur.rowcount
            rows = [clean(r) for r in cur.fetchall()]
            if one:
                return rows[0] if rows else None
            return rows
    finally:
        conn.close()


def err(msg, code):
    return jsonify({"erro": msg}), code


@app.errorhandler(pymysql.err.IntegrityError)
def integrity(e):
    return err("Violação de integridade (e-mail duplicado ou tutor inexistente)", 409)


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/health")
def health():
    query("SELECT 1")
    return jsonify({"status": "ok", "db": "ok"})


# ---------- TUTORES ----------
@app.get("/api/tutores")
def list_tutores():
    return jsonify(query("SELECT * FROM tutores ORDER BY id"))


@app.get("/api/tutores/<int:id>")
def get_tutor(id):
    t = query("SELECT * FROM tutores WHERE id=%s", (id,), one=True)
    return jsonify(t) if t else err("Tutor não encontrado", 404)


@app.post("/api/tutores")
def create_tutor():
    d = request.get_json(silent=True) or {}
    if not d.get("nome") or not d.get("email"):
        return err("nome e email são obrigatórios", 400)
    new_id, _ = query("INSERT INTO tutores (nome,email,telefone) VALUES (%s,%s,%s)",
                      (d["nome"], d["email"], d.get("telefone")), write=True)
    return jsonify(query("SELECT * FROM tutores WHERE id=%s", (new_id,), one=True)), 201


@app.put("/api/tutores/<int:id>")
def update_tutor(id):
    d = request.get_json(silent=True) or {}
    if not d.get("nome") or not d.get("email"):
        return err("nome e email são obrigatórios", 400)
    query("UPDATE tutores SET nome=%s,email=%s,telefone=%s WHERE id=%s",
          (d["nome"], d["email"], d.get("telefone"), id), write=True)
    t = query("SELECT * FROM tutores WHERE id=%s", (id,), one=True)
    return jsonify(t) if t else err("Tutor não encontrado", 404)


@app.delete("/api/tutores/<int:id>")
def delete_tutor(id):
    _, n = query("DELETE FROM tutores WHERE id=%s", (id,), write=True)
    return ("", 204) if n else err("Tutor não encontrado", 404)


# ---------- PETS ----------
PET_SELECT = ("SELECT p.*, t.nome AS tutor_nome FROM pets p "
              "JOIN tutores t ON t.id = p.tutor_id")


@app.get("/api/pets")
def list_pets():
    tutor_id = request.args.get("tutor_id")
    if tutor_id:
        return jsonify(query(PET_SELECT + " WHERE p.tutor_id=%s ORDER BY p.id", (tutor_id,)))
    return jsonify(query(PET_SELECT + " ORDER BY p.id"))


@app.get("/api/pets/<int:id>")
def get_pet(id):
    p = query(PET_SELECT + " WHERE p.id=%s", (id,), one=True)
    return jsonify(p) if p else err("Pet não encontrado", 404)


@app.post("/api/pets")
def create_pet():
    d = request.get_json(silent=True) or {}
    if not d.get("nome") or not d.get("especie") or not d.get("tutor_id"):
        return err("nome, especie e tutor_id são obrigatórios", 400)
    new_id, _ = query(
        "INSERT INTO pets (tutor_id,nome,especie,raca,data_nascimento) VALUES (%s,%s,%s,%s,%s)",
        (d["tutor_id"], d["nome"], d["especie"], d.get("raca"), d.get("data_nascimento") or None),
        write=True)
    return jsonify(query(PET_SELECT + " WHERE p.id=%s", (new_id,), one=True)), 201


@app.put("/api/pets/<int:id>")
def update_pet(id):
    d = request.get_json(silent=True) or {}
    if not d.get("nome") or not d.get("especie") or not d.get("tutor_id"):
        return err("nome, especie e tutor_id são obrigatórios", 400)
    query("UPDATE pets SET tutor_id=%s,nome=%s,especie=%s,raca=%s,data_nascimento=%s WHERE id=%s",
          (d["tutor_id"], d["nome"], d["especie"], d.get("raca"),
           d.get("data_nascimento") or None, id), write=True)
    p = query(PET_SELECT + " WHERE p.id=%s", (id,), one=True)
    return jsonify(p) if p else err("Pet não encontrado", 404)


@app.delete("/api/pets/<int:id>")
def delete_pet(id):
    _, n = query("DELETE FROM pets WHERE id=%s", (id,), write=True)
    return ("", 204) if n else err("Pet não encontrado", 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))

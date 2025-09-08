from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "chave_super_secreta"

# ======================
# CONFIGURAÇÕES DO LOGIN
# ======================
USUARIO_ADMIN = "heurooscria@gamil.com"
SENHA_ADMIN = "heuro"

# ======================
# CONFIGURAÇÕES DE UPLOAD
# ======================
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ======================
# BANCO DE DADOS
# ======================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        descricao TEXT,
        moeda TEXT DEFAULT 'USD',
        imagem TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ======================
# ROTAS DE LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
            session["logado"] = True
            return redirect(url_for("painel"))
        else:
            return render_template("login.html", erro="Usuário ou senha incorretos!")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ======================
# ROTAS DO PAINEL
# ======================
@app.route("/painel", methods=["GET", "POST"])
def painel():
    if not session.get("logado"):
        return redirect(url_for("login"))

    if request.method == "POST":
        nome = request.form["nome"]
        preco = request.form["preco"]
        descricao = request.form["descricao"]
        moeda = request.form["moeda"]

        imagem = None
        if "imagem" in request.files:
            file = request.files["imagem"]
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                imagem = filename

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO produtos (nome, preco, descricao, moeda, imagem) VALUES (?, ?, ?, ?, ?)",
                    (nome, preco, descricao, moeda, imagem))
        conn.commit()
        conn.close()

    # Listar produtos cadastrados
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco, descricao, moeda, imagem FROM produtos")
    produtos = cur.fetchall()
    conn.close()

    return render_template("painel.html", produtos=produtos)

# ======================
# ROTAS DA API (JSON)
# ======================
@app.route("/api/produtos")
def api_produtos():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, nome, preco, descricao, moeda, imagem FROM produtos")
    
    produtos = []
    for r in cur.fetchall():
        # 🔑 Monta URL completa da imagem se existir
        if r[5]:
            img_url = f"https://painel-ly5m.onrender.com/static/uploads/{r[5]}"
        else:
            img_url = None

        produtos.append({
            "id": r[0],
            "nome": r[1],
            "preco": r[2],
            "descricao": r[3],
            "moeda": r[4],
            "imagem": img_url
        })

    conn.close()
    return jsonify(produtos)

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render define a porta na variável de ambiente
    app.run(host="0.0.0.0", port=port, debug=False)

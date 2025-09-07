from flask import Flask, render_template, request
import os, json, csv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# RUTAS EXISTENTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'


# PERSISTENCIA DE DATOS
DATA_DIR = "datos"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

TXT_FILE = os.path.join(DATA_DIR, "datos.txt")
JSON_FILE = os.path.join(DATA_DIR, "datos.json")
CSV_FILE = os.path.join(DATA_DIR, "datos.csv")

# Formulario
@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

# Guardar datos en archivos
@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form['nombre']
    edad = request.form['edad']

    # Guardar en TXT
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{edad}\n")

    # Guardar en JSON
    datos_json = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                datos_json = json.load(f)
            except:
                datos_json = []
    datos_json.append({"nombre": nombre, "edad": edad})
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(datos_json, f, indent=4)

    # Guardar en CSV
    escribir_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if escribir_header:
            writer.writerow(["nombre", "edad"])
        writer.writerow([nombre, edad])

    return render_template('resultado.html', nombre=nombre, edad=edad)

# Ver datos
@app.route('/ver/txt')
def ver_txt():
    with open(TXT_FILE, "r", encoding="utf-8") as f:
        datos = f.readlines()
    return "<br>".join(datos)

@app.route('/ver/json')
def ver_json():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return {"usuarios": datos}

@app.route('/ver/csv')
def ver_csv():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        datos = list(reader)
    return {"usuarios": datos}

# PERSISTENCIA CON SQLITE

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "database", "usuarios.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    edad = db.Column(db.Integer)

with app.app_context():
    db.create_all()

@app.route('/guardar_db', methods=['POST'])
def guardar_db():
    nombre = request.form['nombre']
    edad = int(request.form['edad'])

    usuario = Usuario(nombre=nombre, edad=edad)
    db.session.add(usuario)
    db.session.commit()

    return f"Usuario {nombre} guardado en SQLite."

@app.route('/ver/db')
def ver_db():
    usuarios = Usuario.query.all()
    return {"usuarios": [{"id": u.id, "nombre": u.nombre, "edad": u.edad} for u in usuarios]}

# EJECUTAR APP
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Mantener para Render
    app.run(host='0.0.0.0', port=port, debug=True)
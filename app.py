from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
import json
import os


# Configuración de Flask y MySQL con SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:12345@localhost:3307/desarrollo_web"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)


# Modelo de Usuario en MySQL

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # nombre exacto de la tabla en MySQL
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=True)

# Crear tablas si no existen (no pasa nada si ya existen)
with app.app_context():
    db.create_all()

# Rutas principales


@app.route('/')
def index():
    return render_template('index.html')


# PRODUCTOS (CSV)

@app.route('/productos')
def productos():
    productos_list = []
    basedir = os.path.abspath(os.path.dirname(__file__))
    productos_file = os.path.join(basedir, 'datos', 'productos.csv')
    if os.path.exists(productos_file):
        with open(productos_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                productos_list.append(row)
    return render_template('productos.html', productos=productos_list)

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    basedir = os.path.abspath(os.path.dirname(__file__))
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        if nombre and precio:
            productos_file = os.path.join(basedir, 'datos', 'productos.csv')
            file_exists = os.path.exists(productos_file)
            with open(productos_file, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['nombre', 'precio']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({'nombre': nombre, 'precio': precio})
            return redirect(url_for('productos'))
    return render_template('agregar_producto.html')


# VENTAS (JSON)

@app.route('/ventas')
def ventas():
    ventas_list = []
    basedir = os.path.abspath(os.path.dirname(__file__))
    ventas_file = os.path.join(basedir, 'datos', 'ventas.json')
    if os.path.exists(ventas_file):
        with open(ventas_file, 'r', encoding='utf-8') as f:
            try:
                ventas_list = json.load(f)
            except json.JSONDecodeError:
                ventas_list = []
    return render_template('ventas.html', ventas=ventas_list)

@app.route('/agregar_venta', methods=['GET', 'POST'])
def agregar_venta():
    basedir = os.path.abspath(os.path.dirname(__file__))
    ventas_file = os.path.join(basedir, 'datos', 'ventas.json')
    if request.method == 'POST':
        producto = request.form.get('producto')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')
        if producto and cantidad and precio:
            nueva_venta = {
                'producto': producto,
                'cantidad': int(cantidad),
                'precio': float(precio)
            }
            ventas_list = []
            if os.path.exists(ventas_file):
                with open(ventas_file, 'r', encoding='utf-8') as f:
                    try:
                        ventas_list = json.load(f)
                    except json.JSONDecodeError:
                        ventas_list = []
            ventas_list.append(nueva_venta)
            with open(ventas_file, 'w', encoding='utf-8') as f:
                json.dump(ventas_list, f, indent=4)
            return redirect(url_for('ventas'))
    return render_template('agregar_venta.html')


# FORMULARIO USUARIOS (MySQL)

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        email = request.form.get('email')
        if nombre and edad:
            nuevo_usuario = Usuario(nombre=nombre, edad=int(edad), email=email)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('resultado', nombre=nombre, edad=edad))
    return render_template('formulario.html')

@app.route('/resultado')
def resultado():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    return render_template('resultado.html', nombre=nombre, edad=edad)

# LISTAR USUARIOS MYSQL
@app.route('/usuarios_mysql')
def usuarios_mysql():
    usuarios = Usuario.query.all()
    return render_template('usuarios_mysql.html', usuarios=usuarios)

# RUTA DE PRUEBA DE CONEXIÓN A MYSQL
@app.route('/test_db')
def test_db():
    try:
        # Crear sesión temporal de SQLAlchemy
        conn = db.session()
        conn.close()
        return "Conexión a MySQL exitosa"
    except Exception as e:
        return f"Error al conectar: {e}"
    
# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

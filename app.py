from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import json
import os

# Configuración de Flask y MySQL con SQLAlchemy
app = Flask(__name__)
app.secret_key = "clave_secreta_segura"  # Necesario para sesiones y Flask-Login

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:12345@localhost:3307/desarrollo_web"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Modelo de Usuario en MySQL
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id_usuario)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# -------------------- RUTAS --------------------

@app.route('/')
def index():
    return render_template('index.html')

# -------- PRODUCTOS (CSV) --------
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

# -------- VENTAS (JSON) --------
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

# -------- FORMULARIO USUARIOS (MySQL) --------
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        email = request.form.get('email')
        password = request.form.get('password')
        if nombre and edad and password:
            password_hash = generate_password_hash(password)
            nuevo_usuario = Usuario(nombre=nombre, edad=int(edad), email=email, password=password_hash)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('resultado', nombre=nombre, edad=edad))
    return render_template('formulario.html')

@app.route('/resultado')
def resultado():
    nombre = request.args.get('nombre')
    edad = request.args.get('edad')
    return render_template('resultado.html', nombre=nombre, edad=edad)

# -------- LISTAR USUARIOS MYSQL --------
@app.route('/usuarios_mysql')
def usuarios_mysql():
    usuarios = Usuario.query.all()
    return render_template('usuarios_mysql.html', usuarios=usuarios)

# -------- LOGIN / REGISTER / LOGOUT / DASHBOARD --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        edad = request.form['edad']

        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado", "danger")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        nuevo_usuario = Usuario(nombre=nombre, email=email, edad=int(edad), password=password_hash)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario registrado con éxito", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', usuario=current_user)

# -------- PRUEBA CONEXIÓN MYSQL --------
@app.route('/test_db')
def test_db():
    try:
        conn = db.session()
        conn.close()
        return "Conexión a MySQL exitosa"
    except Exception as e:
        return f"Error al conectar: {e}"

# -------------------- EJECUTAR APP --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


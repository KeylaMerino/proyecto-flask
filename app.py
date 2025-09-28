from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

# -------------------- CONFIGURACIÓN --------------------
app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:12345@localhost:3307/desarrollo_web"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------- MODELOS --------------------
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id_usuario)

class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# -------------------- LOGIN MANAGER --------------------
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

# -------- CRUD PRODUCTOS --------
@app.route('/productos')
@login_required
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/crear_producto', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        if nombre and precio and stock:
            nuevo = Producto(nombre=nombre, precio=precio, stock=stock)
            db.session.add(nuevo)
            db.session.commit()
            flash("Producto agregado exitosamente", "success")
            return redirect(url_for('productos'))
    return render_template('agregar_producto.html')

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.precio = request.form['precio']
        producto.stock = request.form['stock']
        db.session.commit()
        flash("Producto actualizado correctamente", "success")
        return redirect(url_for('productos'))
    return render_template('editar_producto.html', producto=producto)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado", "success")
    return redirect(url_for('productos'))

# -------- VENTAS (JSON) --------
@app.route('/ventas')
@login_required
def ventas():
    basedir = os.path.abspath(os.path.dirname(__file__))
    ventas_file = os.path.join(basedir, 'datos', 'ventas.json')
    ventas_list = []
    if os.path.exists(ventas_file):
        with open(ventas_file, 'r', encoding='utf-8') as f:
            try:
                ventas_list = json.load(f)
            except json.JSONDecodeError:
                ventas_list = []
    return render_template('ventas.html', ventas=ventas_list)

@app.route('/agregar_venta', methods=['GET', 'POST'])
@login_required
def agregar_venta():
    basedir = os.path.abspath(os.path.dirname(__file__))
    ventas_file = os.path.join(basedir, 'datos', 'ventas.json')
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        nueva_venta = {
            "producto": producto,
            "cantidad": int(cantidad),
            "precio": float(precio)
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
        flash("Venta agregada correctamente", "success")
        return redirect(url_for('ventas'))
    return render_template('agregar_venta.html')

# -------- LOGIN / REGISTER / LOGOUT --------
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
            flash("Login exitoso", "success")
            return redirect(url_for('dashboard'))  # <--- Aquí usamos dashboard
        else:
            flash("Correo o contraseña incorrectos", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión", "success")
    return redirect(url_for('login'))

# -------- DASHBOARD --------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', usuario=current_user)

# -------------------- EJECUTAR APP --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


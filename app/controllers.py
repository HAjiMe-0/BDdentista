from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models import db, Doctor, Paciente

main_bp = Blueprint('main', __name__)

# Decorador para proteger rutas que requieren autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta de inicio
@main_bp.route('/')
def home():
    if 'doctor_id' in session:
        return redirect(url_for('main.index'))
    return redirect(url_for('main.login'))

# Ruta principal después de login
@main_bp.route('/index')
@login_required
def index():
    doctores = Doctor.query.all()
    pacientes = Paciente.query.all()
    return render_template('index.html', doctores=doctores, pacientes=pacientes)

# Ruta de login
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and doctor.contraseña == contraseña:  # Recuerda encriptar contraseñas en producción
            session['doctor_id'] = doctor.doctor_id
            session['doctor_name'] = doctor.nombre
            return redirect(url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
    return render_template('login.html')

# Ruta de logout
@main_bp.route('/logout')
def logout():
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    return redirect(url_for('main.login'))

# Ruta para crear un doctor
@main_bp.route('/doctor/create', methods=['GET', 'POST'])
@login_required
def create_doctor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form.get('especialidad')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')  # Agregar campo de contraseña
        doctor = Doctor(nombre=nombre, especialidad=especialidad, telefono=telefono, email=email, contraseña=contraseña)
        db.session.add(doctor)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_doctor.html')

# Ruta para crear un paciente
@main_bp.route('/paciente/create', methods=['GET', 'POST'])
@login_required
def create_paciente():
    doctores = Doctor.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        doctor_id = request.form['doctor_id']
        paciente = Paciente(
            nombre=nombre, fecha_nacimiento=fecha_nacimiento,
            direccion=direccion, telefono=telefono, doctor_id=doctor_id
        )
        db.session.add(paciente)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_paciente.html', doctores=doctores)

# Ruta para eliminar un doctor o paciente
@main_bp.route('/delete/<string:entity>/<int:id>', methods=['POST'])
@login_required
def delete_entity(entity, id):
    if entity == "doctor":
        Doctor.query.filter_by(doctor_id=id).delete()
    elif entity == "paciente":
        Paciente.query.filter_by(paciente_id=id).delete()
    db.session.commit()
    return redirect(url_for('main.index'))

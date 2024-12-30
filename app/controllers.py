from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models import db, Doctor, Paciente
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app import mail  # Importar mail desde app

main_bp = Blueprint('main', __name__)

# Configuración de URLSafeTimedSerializer
s = URLSafeTimedSerializer('Thisisasecret!')

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
    # Obtén el doctor_id desde la sesión
    doctor_id = session.get('doctor_id')
    
    # Filtra los pacientes que pertenecen al doctor que inició sesión
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()
    
    # Opcional: También puedes incluir los datos del doctor logueado si lo necesitas
    doctor = Doctor.query.get(doctor_id)
    
    return render_template('index.html', doctor=doctor, pacientes=pacientes)

# Ruta de login
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        doctor = Doctor.query.filter_by(email=email).first()

        # Verifica si la contraseña ingresada coincide con la almacenada
        if doctor and check_password_hash(doctor.contraseña, contraseña):
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
        paterno = request.form.get('paterno')
        materno = request.form.get('materno')
        especialidad = request.form.get('especialidad')
        telefono = request.form.get('telefono')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')
        hashed_password = generate_password_hash(contraseña)  # Encriptar la contraseña
        doctor = Doctor(nombre=nombre, especialidad=especialidad, telefono=telefono, email=email, contraseña=hashed_password)
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor creado exitosamente.', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_doctor.html')

# Ruta para crear un paciente
@main_bp.route('/paciente/create', methods=['GET', 'POST'])
@login_required
def create_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        paterno = request.form.get('paterno')
        materno = request.form.get('materno')
        ci = request.form.get('ci')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        celular = request.form.get('celular')
        estado_civil = request.form.get('estado_civil')
        ocupacion = request.form.get('ocupacion')
        doctor_id = session.get('doctor_id')

        paciente = Paciente(
            nombre=nombre,
            paterno=paterno,
            materno=materno,
            ci=ci,
            fecha_nacimiento=fecha_nacimiento,
            direccion=direccion,
            telefono=telefono,
            celular=celular,
            estado_civil=estado_civil,
            ocupacion=ocupacion,
            doctor_id=doctor_id
        )
        db.session.add(paciente)
        db.session.commit()
        flash('Paciente creado exitosamente.', 'success')
        return redirect(url_for('main.create_paciente'))

    return render_template('create_paciente.html')

# Ver detalle del paciente
@main_bp.route('/paciente/<int:paciente_id>', methods=['GET'])
@login_required
def paciente_detail(paciente_id):
    # Buscar el paciente por ID
    paciente = Paciente.query.get_or_404(paciente_id)
    
    # Verificar que el paciente pertenezca al doctor logueado
    if paciente.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver este paciente.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('paciente_detail.html', paciente=paciente)

# Ver detalle del Doctor 
@main_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
@login_required
def doctor_detail(doctor_id):
    # Obtener el doctor por ID
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Verificar que el doctor sea el mismo que está logueado
    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver este perfil.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('doctor_detail.html', doctor=doctor)

# Editar Doctor
@main_bp.route('/doctor/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para editar este perfil.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if 'nombre' in request.form:
            doctor.nombre = request.form['nombre']
        if 'paterno' in request.form:
            doctor.paterno = request.form['paterno']
        if 'materno' in request.form:
            doctor.materno = request.form['materno']
        if 'especialidad' in request.form:
            doctor.especialidad = request.form['especialidad']
        if 'telefono' in request.form:
            doctor.telefono = request.form['telefono']
        if 'fecha_nacimiento' in request.form:
            doctor.fecha_nacimiento = request.form['fecha_nacimiento']
        if 'email' in request.form:
            doctor.email = request.form['email']
            
        # Actualiza el nombre en la sesión después de guardar los cambios
        session['doctor_name'] = doctor.nombre

        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('main.edit_doctor', doctor_id=doctor_id))

    return render_template('edit_doctor.html', doctor=doctor)

# Editar Paciente
@main_bp.route('/paciente/edit/<int:paciente_id>', methods=['GET', 'POST'])
@login_required
def edit_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)

    if paciente.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para editar este paciente.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        if 'nombre' in request.form:
            paciente.nombre = request.form['nombre']
        if 'paterno' in request.form:
            paciente.paterno = request.form['paterno']
        if 'materno' in request.form:
            paciente.materno = request.form['materno']
        if 'ci' in request.form:
            paciente.ci = request.form['ci']
        if 'fecha_nacimiento' in request.form:
            paciente.fecha_nacimiento = request.form['fecha_nacimiento']
        if 'direccion' in request.form:
            paciente.direccion = request.form['direccion']
        if 'telefono' in request.form:
            paciente.telefono = request.form['telefono']
        if 'celular' in request.form:
            paciente.celular = request.form['celular']
        if 'estado_civil' in request.form:
            paciente.estado_civil = request.form['estado_civil']
        if 'ocupacion' in request.form:
            paciente.ocupacion = request.form['ocupacion']

        db.session.commit()
        flash('Paciente actualizado exitosamente.', 'success')
        return redirect(url_for('main.pacientes_list'))

    return render_template('edit_paciente.html', paciente=paciente)

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

# Ruta de registro 
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ci = request.form['ci']
        nombre = request.form['nombre']
        paterno = request.form.get('paterno')
        materno = request.form.get('materno')
        especialidad = request.form.get('especialidad')
        telefono = request.form.get('telefono')
        fecha_nacimiento = request.form.get('fecha_nacimiento')
        email = request.form['email']
        contraseña = request.form['contraseña']

        # Verifica si el email ya está registrado
        if Doctor.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado. Intente con otro.', 'error')
            return redirect(url_for('main.register'))

        # Encriptar la contraseña antes de guardarla
        hashed_password = generate_password_hash(contraseña)

        # Verificar que la fecha de nacimiento esté presente
        if not fecha_nacimiento:
            flash('La fecha de nacimiento es requerida.', 'error')
            return redirect(url_for('main.register'))

        # Convertir la fecha de nacimiento a un formato adecuado para la base de datos
        from datetime import datetime
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()

        # Crear un nuevo doctor
        nuevo_doctor = Doctor(
            ci=ci,
            nombre=nombre,
            paterno=paterno,
            materno=materno,
            especialidad=especialidad,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            contraseña=hashed_password
        )
        db.session.add(nuevo_doctor)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')
#Lista de pacientes
@main_bp.route('/pacientes', methods=['GET'])
@login_required
def pacientes_list():
    doctor_id = session.get('doctor_id')
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()
    return render_template('pacientes_list.html', pacientes=pacientes)

# Ruta para restablecer contraseña
@main_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor:
            token = s.dumps(email, salt='email-confirm')
            msg = Message('Restablecer contraseña', sender='noreply@domain.com', recipients=[email])
            link = url_for('main.reset_with_token', token=token, _external=True)
            msg.body = f'Su enlace para restablecer su contraseña es {link}'
            mail.send(msg)
            flash('Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña.', 'info')
        else:
            flash('El correo electrónico no está registrado.', 'error')
    return render_template('reset_password.html')

@main_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado.', 'error')
        return redirect(url_for('main.reset_password'))

    if request.method == 'POST':
        contraseña = request.form['contraseña']
        hashed_password = generate_password_hash(contraseña)
        doctor = Doctor.query.filter_by(email=email).first()
        doctor.contraseña = hashed_password
        db.session.commit()
        flash('Su contraseña ha sido actualizada.', 'success')
        return redirect(url_for('main.login'))

    return render_template('reset_with_token.html')

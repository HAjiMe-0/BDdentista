from flask import Blueprint, render_template, request, redirect, url_for, session, flash ,jsonify, Response, send_file
from functools import wraps
from app.models import db, Doctor, Paciente , Cita
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app import mail  # Importar mail desde app
from app import db
from .models import Paciente, FormularioMedico
from app.models import Paciente, FichaDental, FormularioMedico
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from datetime import datetime

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
# Ruta para listar a los pacientes
@main_bp.route('/list_paciente')
@login_required
def list_paciente():
    doctor_id = session.get('doctor_id')
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()
    doctor = Doctor.query.get(doctor_id)
    return render_template('paciente/list_paciente.html', doctor=doctor, pacientes=pacientes)

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

    return render_template('paciente/create_paciente.html')

# Ver detalle del paciente
@main_bp.route('/paciente/<int:paciente_id>', methods=['GET'])
@login_required
def detail_paciente(paciente_id):
    # Buscar el paciente por ID
    paciente = Paciente.query.get_or_404(paciente_id)
    
    # Verificar que el paciente pertenezca al doctor logueado
    if paciente.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver este paciente.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('paciente/detail_paciente.html', paciente=paciente)

# Ver detalle del Doctor 
@main_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
@login_required
def detail_doctor(doctor_id):
    # Obtener el doctor por ID
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Verificar que el doctor sea el mismo que está logueado
    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver este perfil.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('doctor/detail_doctor.html', doctor=doctor)

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

    return render_template('doctor/edit_doctor.html', doctor=doctor)

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
        return redirect(url_for('main.edit_paciente', paciente_id=paciente_id))

    return render_template('paciente/edit_paciente.html', paciente=paciente)

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

    #rutas para las fichas dentales

# Ruta para listar fichas de un paciente
@main_bp.route('/paciente/<int:paciente_id>/fichas', methods=['GET'])
@login_required
def listar_fichas(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    fichas = FichaDental.query.filter_by(paciente_id=paciente_id).all()
    return render_template('paciente/listar_fichas.html', paciente=paciente, fichas=fichas)

# Ruta para crear una ficha dental para un paciente
@main_bp.route('/paciente/<int:paciente_id>/fichas/crear', methods=['GET', 'POST'])
@login_required
def crear_ficha(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)

    if request.method == 'POST':
        fecha = request.form.get('fecha')
        pieza_dental = request.form.get('pieza_dental')
        diagnostico = request.form.get('diagnostico')
        tratamiento = request.form.get('tratamiento')
        costo = float(request.form.get('costo'))
        al_contado = float(request.form.get('al_contado'))
        saldo = float(request.form.get('saldo', 0))
        observaciones = request.form.get('observaciones')

        # Crear y guardar la nueva ficha
        nueva_ficha = FichaDental(
            fecha=fecha,
            pieza_dental=pieza_dental,
            diagnostico=diagnostico,
            tratamiento=tratamiento,
            costo=costo,
            al_contado=al_contado,
            saldo=saldo,
            observaciones=observaciones,
            paciente_id=paciente_id
        )
        db.session.add(nueva_ficha)
        db.session.commit()

        flash('Ficha creada exitosamente.', 'success')
        return redirect(url_for('main.listar_fichas', paciente_id=paciente_id))

    return render_template('paciente/crear_ficha.html', paciente=paciente)

# Ruta para editar una ficha dental existente
@main_bp.route('/ficha/<int:ficha_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_ficha(ficha_id):
    ficha = FichaDental.query.get_or_404(ficha_id)

    if request.method == 'POST':
        # Asignar los valores del formulario a los campos de la ficha dental
        ficha.fecha = request.form.get('fecha', ficha.fecha)  # Mantener fecha original si no se proporciona nueva
        ficha.pieza_dental = request.form.get('pieza_dental', ficha.pieza_dental)
        ficha.diagnostico = request.form.get('diagnostico', ficha.diagnostico)
        ficha.tratamiento = request.form.get('tratamiento', ficha.tratamiento)
        
        # Convertir los valores de costo, al_contado, y saldo a decimal
        ficha.costo = request.form.get('costo', ficha.costo)
        ficha.al_contado = request.form.get('al_contado', ficha.al_contado)
        ficha.saldo = request.form.get('saldo', ficha.saldo)
        
        ficha.observaciones = request.form.get('observaciones', ficha.observaciones)

        # Commit de los cambios
        db.session.commit()
        flash('Ficha Dental actualizada con éxito.', 'success')
        return redirect(url_for('main.listar_fichas', paciente_id=ficha.paciente_id))

    # Si el método es GET, simplemente renderiza el formulario con los datos actuales de la ficha
    return render_template('paciente/editar_ficha.html', ficha=ficha)


# Ruta para eliminar una ficha dental
@main_bp.route('/ficha/<int:ficha_id>/eliminar', methods=['POST'])
@login_required
def eliminar_ficha(ficha_id):
    ficha = FichaDental.query.get_or_404(ficha_id)
    paciente_id = ficha.paciente_id
    db.session.delete(ficha)
    db.session.commit()
    flash('Ficha Dental eliminada con éxito.', 'success')
    return redirect(url_for('main.listar_fichas', paciente_id=paciente_id))



# Ruta para crear una cita
@main_bp.route('/cita/create', methods=['GET', 'POST'])
@login_required
def create_cita():
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        doctor_id = session.get('doctor_id')
        fecha = request.form['fecha']
        motivo = request.form['motivo']
        
        # Crear la cita
        nueva_cita = Cita(
            paciente_id=paciente_id,
            doctor_id=doctor_id,
            fecha=fecha,
            motivo=motivo
        )
        
        db.session.add(nueva_cita)
        db.session.commit()
        flash('Cita creada con éxito.', 'success')
        return redirect(url_for('main.list_cita'))
    
    # Obtener lista de pacientes
    doctor_id = session.get('doctor_id')
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()
    
    return render_template('cita/create_cita.html', pacientes=pacientes)

#Ruta para ver detalles
@main_bp.route('/cita/<int:cita_id>', methods=['GET'])
@login_required
def detail_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    if cita.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver esta cita.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('cita/detail_cita.html', cita=cita)

#Ruta para editar cita
@main_bp.route('/cita/edit/<int:cita_id>', methods=['GET', 'POST'])
@login_required
def edit_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    
    if cita.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para editar esta cita.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nueva_fecha = request.form['fecha']
        nuevo_motivo = request.form['motivo']
        nuevo_estado = request.form['estado']
        
        cita.fecha = nueva_fecha
        cita.motivo = nuevo_motivo
        cita.estado = nuevo_estado
        
        db.session.commit()
        flash('Cita actualizada con éxito.', 'success')
        return redirect(url_for('main.list_cita'))
    
    return render_template('cita/edit_cita.html', cita=cita)

# Ruta para listar las citas
@main_bp.route('/citas', methods=['GET'])
@login_required
def list_cita():
    doctor_id = session.get('doctor_id')
    citas = Cita.query.filter_by(doctor_id=doctor_id).all()
    return render_template('cita/list_cita.html', citas=citas)

# Ruta para eliminar una cita
@main_bp.route('/delete_cita/<int:cita_id>', methods=['POST'])
@login_required
def delete_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    
    if cita.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para eliminar esta cita.', 'error')
        return redirect(url_for('main.index'))
    
    db.session.delete(cita)
    db.session.commit()
    flash('Cita eliminada con éxito.', 'success')
    return redirect(url_for('main.list_cita'))


# Ruta para obtener las citas de un doctor
@main_bp.route('/citas/<int:year>/<int:month>', methods=['GET'])
def get_citas_for_month(year, month):
    # Obtener las citas del mes desde la base de datos
    citas = Cita.query.filter(db.extract('year', Cita.fecha) == year,
                              db.extract('month', Cita.fecha) == month).all()

    # Formatear las citas para enviarlas al frontend
    citas_data = [{
        'id': cita.cita_id,
        'fecha': cita.fecha.strftime('%Y-%m-%d'),
        'motivo': cita.motivo,
        'paciente': cita.paciente.nombre,  # Asegúrate de acceder correctamente al nombre del paciente
    } for cita in citas]

    return jsonify(citas_data)


# Ruta para mostrar el formulario con datos del paciente
@main_bp.route('/formulario/<int:paciente_id>', methods=['GET'])
def mostrar_formulario(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    return render_template('formulario.html', paciente=paciente)

@main_bp.route('/guardar_historial', methods=['POST'])
def guardar_historial():
    try:
        data = request.get_json()
        paciente_id = data.get('paciente_id')
        pregunta_respuesta = data.get('pregunta_respuesta')

        # Validaciones
        if not paciente_id:
            return jsonify({"message": "ID de paciente no recibido"}), 400
        if not pregunta_respuesta:
            return jsonify({"message": "No se recibieron respuestas"}), 400

        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            return jsonify({"message": "Paciente no encontrado"}), 404

        # Crear el historial médico
        nuevo_historial = FormularioMedico(
            paciente_id=paciente_id,
            pregunta_respuesta=pregunta_respuesta
        )
        db.session.add(nuevo_historial)
        db.session.commit()
        print("Datos recibidos:", data)
        print("Paciente ID:", paciente_id)
        print("Pregunta Respuesta:", pregunta_respuesta)
        return jsonify({"message": "Historial clínico guardado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al guardar: {str(e)}"}), 500
    
# ruta para geneerar el pdf del formulario
@main_bp.route('/generar_pdf/<int:paciente_id>', methods=['GET'])
def generar_pdf(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    formulario = FormularioMedico.query.filter_by(paciente_id=paciente_id).first()

    if not formulario:
        return jsonify({"message": "No se encontró el formulario médico para este paciente"}), 404

    # Crear el archivo PDF en memoria
    pdf_output = BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)

    # Agregar título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Formulario Médico")

    # Datos del paciente
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Nombre completo: {paciente.nombre} {paciente.paterno} {paciente.materno}")
    c.drawString(50, 705, f"Cédula de Identidad: {paciente.ci}")
    c.drawString(50, 690, f"Fecha de nacimiento: {paciente.fecha_nacimiento}")
    c.drawString(50, 675, f"Estado Civil: {paciente.estado_civil}")
    c.drawString(50, 660, f"Ocupación: {paciente.ocupacion}")
    c.drawString(50, 645, f"Teléfono: {paciente.telefono}")
    c.drawString(50, 630, f"Celular: {paciente.celular}")

    # Antecedentes médicos
    y_position = 600
    for pregunta, respuesta in formulario.pregunta_respuesta.items():
        c.drawString(50, y_position, f"{pregunta}: {respuesta}")
        y_position -= 15  # Espacio entre cada línea

    # Finalizar el PDF
    c.showPage()
    c.save()

    # Retornar el PDF como archivo descargable
    pdf_output.seek(0)
    return send_file(pdf_output, as_attachment=True, download_name=f"formulario_paciente_{paciente_id}.pdf", mimetype="application/pdf")
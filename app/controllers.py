from flask import (Blueprint, render_template, request, redirect, url_for, session,
                   flash, jsonify, make_response, send_file)
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from app.models import db, Doctor, Paciente, Cita, Tratamiento, FormularioMedico
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app import mail
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
from decimal import Decimal

main_bp = Blueprint('main', __name__)
s = URLSafeTimedSerializer('clave_secreta')

# Decorador para rutas que requieren autenticación
def login_requerido(funcion):
    @wraps(funcion)
    def decorador(*args, **kwargs):
        if 'doctor_id' not in session:
            return redirect(url_for('main.  '))
        return funcion(*args, **kwargs)
    return decorador

# Ruta de inicio
@main_bp.route('/')
def inicio():
    if 'doctor_id' in session:
        return redirect(url_for('main.iniciar_sesion'))
    return redirect(url_for('main.dashboard'))

# Pantalla de inicio de sesión
@main_bp.route('/iniciar-sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        doctor = Doctor.query.filter_by(email=email).first()

        if doctor and check_password_hash(doctor.contraseña, contraseña):
            session['doctor_id'] = doctor.doctor_id
            session['doctor_nombre'] = doctor.nombre
            return redirect(url_for('main.dashboard'))
        else:
            flash('Correo o contraseña incorrectos.', 'error')
    return render_template('autenticacion/iniciar_sesion.html')

# Ruta de registro
@main_bp.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        datos = {
            'ci': request.form['ci'],
            'nombre': request.form['nombre'],
            'paterno': request.form.get('paterno'),
            'materno': request.form.get('materno'),
            'especialidad': request.form.get('especialidad'),
            'telefono': request.form.get('telefono'),
            'fecha_nacimiento': request.form.get('fecha_nacimiento'),
            'email': request.form['email'],
            'contraseña': generate_password_hash(request.form['contraseña'])
        }

        if Doctor.query.filter_by(email=datos['email']).first():
            flash('El correo electrónico ya está registrado.', 'error')
            return redirect(url_for('main.registrarse'))

        try:
            nuevo_doctor = Doctor(**datos)
            db.session.add(nuevo_doctor)
            db.session.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('main.iniciar_sesion'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error al registrarse: {str(e)}', 'error')
    return render_template('autenticacion/registrarse.html')

# Ruta para cerrar sesión
@main_bp.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('main.iniciar_sesion'))

# Dashboard principal
@main_bp.route('/dashboard')
@login_requerido
def dashboard():
    doctor_id = session['doctor_id']
    doctor = Doctor.query.get(doctor_id)
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()
    citas_pendientes = Cita.query.filter_by(doctor_id=doctor_id, estado='Pendiente').all()
    tratamientos_activos = Tratamiento.query.filter_by(paciente_id=doctor_id, estado='En Progreso').all()

    return render_template('dashboard.html', doctor=doctor, pacientes=pacientes, citas=citas_pendientes, tratamientos=tratamientos_activos)
# Gestión de doctor
@main_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
@login_requerido
def detalle_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para ver este perfil.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('doctor/detalle_doctor.html', doctor=doctor)
    
@main_bp.route('/doctor/<int:doctor_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para editar este perfil.', 'error')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        doctor.nombre = request.form['nombre']
        doctor.paterno = request.form.get('paterno')
        doctor.materno = request.form.get('materno')
        doctor.ci = request.form.get('ci')
        doctor.fecha_nacimiento = request.form.get('fecha_nacimiento')
        doctor.especialidad = request.form.get('especialidad')
        doctor.telefono = request.form.get('telefono')
        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('main.detalle_doctor', doctor_id=doctor_id))
    
    return render_template('doctor/editar_doctor.html', doctor=doctor)


# Gestión de pacientes
@main_bp.route('/pacientes')
@login_requerido
def listar_pacientes():
    doctor_id = session.get('doctor_id')  # Usar `get` para evitar errores si no existe la clave
    if not doctor_id:
        # Manejo del caso en que `doctor_id` no está en la sesión
        return redirect('/login')  # O la página que corresponda
    
    # Obtener al doctor desde la base de datos
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        # Manejo del caso en que el doctor no existe
        return "Doctor no encontrado", 404

    # Obtener los pacientes asociados al doctor
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()

    # Pasar el doctor y los pacientes al template
    return render_template(
        'pacientes/listar_pacientes.html', 
        pacientes=pacientes, 
        doctor=doctor
    )


@main_bp.route('/paciente/crear', methods=['GET', 'POST'])
@login_requerido
def crear_paciente():
    if request.method == 'POST':
        datos = {
            'nombre': request.form['nombre'],
            'paterno': request.form.get('paterno'),
            'materno': request.form.get('materno'),
            'ci': request.form.get('ci'),
            'fecha_nacimiento': request.form.get('fecha_nacimiento'),
            'direccion': request.form.get('direccion'),
            'telefono': request.form.get('telefono'),
            'celular': request.form.get('celular'),
            'estado_civil': request.form.get('estado_civil'),
            'ocupacion': request.form.get('ocupacion'),
            'doctor_id': session['doctor_id']
        }
        nuevo_paciente = Paciente(**datos)
        db.session.add(nuevo_paciente)
        db.session.commit()
        flash('Paciente creado exitosamente.', 'success')
        return redirect(url_for('main.listar_pacientes'))
    return render_template('pacientes/crear_paciente.html')

@main_bp.route('/paciente/<int:paciente_id>')
@login_requerido
def detalle_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver este paciente.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    tratamientos = Tratamiento.query.filter_by(paciente_id=paciente_id).all()
    citas = Cita.query.filter_by(paciente_id=paciente_id).all()
    formulario_medico = FormularioMedico.query.filter_by(paciente_id=paciente_id).order_by(FormularioMedico.fecha.desc()).first()
    return render_template('pacientes/detalle_paciente.html', paciente=paciente, tratamientos=tratamientos, citas=citas, formulario_medico=formulario_medico)

@main_bp.route('/paciente/<int:paciente_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para editar este paciente.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    if request.method == 'POST':
        paciente.nombre = request.form['nombre']
        paciente.paterno = request.form.get('paterno')
        paciente.materno = request.form.get('materno')
        paciente.ci = request.form.get('ci')
        paciente.fecha_nacimiento = request.form.get('fecha_nacimiento')
        paciente.direccion = request.form.get('direccion')
        paciente.telefono = request.form.get('telefono')
        paciente.celular = request.form.get('celular')
        paciente.estado_civil = request.form.get('estado_civil')
        paciente.ocupacion = request.form.get('ocupacion')
        db.session.commit()
        flash('Paciente actualizado exitosamente.', 'success')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    return render_template('pacientes/editar_paciente.html', paciente=paciente)

@main_bp.route('/paciente/<int:paciente_id>/eliminar', methods=['POST'])
@login_requerido
def eliminar_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para eliminar este paciente.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    db.session.delete(paciente)
    db.session.commit()
    flash('Paciente eliminado exitosamente.', 'success')
    return redirect(url_for('main.listar_pacientes'))

# Gestión de citas
@main_bp.route('/citas')
@login_requerido
def listar_citas():
    doctor_id = session['doctor_id']
    citas = Cita.query.filter_by(doctor_id=doctor_id).order_by(Cita.fecha.asc()).all()
    return render_template('citas/listar_citas.html', citas=citas)

@main_bp.route('/cita/crear', methods=['GET', 'POST'])
@login_requerido
def crear_cita():
    if request.method == 'POST':
        datos = {
            'paciente_id': request.form['paciente_id'],
            'doctor_id': session['doctor_id'],
            'fecha': datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M'),
            'motivo': request.form['motivo'],
            'estado': 'Pendiente'
        }
        nueva_cita = Cita(**datos)
        db.session.add(nueva_cita)
        db.session.commit()
        flash('Cita creada exitosamente.', 'success')
        return redirect(url_for('main.listar_citas'))

    pacientes = Paciente.query.filter_by(doctor_id=session['doctor_id']).all()
    return render_template('citas/crear_cita.html', pacientes=pacientes)

@main_bp.route('/cita/<int:cita_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    if cita.doctor_id != session['doctor_id']:
        flash('No tienes permiso para editar esta cita.', 'error')
        return redirect(url_for('main.listar_citas'))

    if request.method == 'POST':
        cita.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M')
        cita.motivo = request.form['motivo']
        cita.estado = request.form['estado']
        db.session.commit()
        flash('Cita actualizada exitosamente.', 'success')
        return redirect(url_for('main.listar_citas'))

    return render_template('citas/editar_cita.html', cita=cita)

@main_bp.route('/cita/<int:cita_id>/eliminar', methods=['POST'])
@login_requerido
def eliminar_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    if cita.doctor_id != session['doctor_id']:
        flash('No tienes permiso para eliminar esta cita.', 'error')
        return redirect(url_for('main.listar_citas'))

    db.session.delete(cita)
    db.session.commit()
    flash('Cita eliminada exitosamente.', 'success')
    return redirect(url_for('main.listar_citas'))

# Ruta para obtener citas de un mes específico
@main_bp.route('/citas/<int:year>/<int:month>', methods=['GET'])
@login_requerido
def obtener_citas(year, month):
    try:
        doctor_id = session.get('doctor_id')
        if not doctor_id:
            return jsonify({"error": "No autorizado"}), 401

        citas = Cita.query.filter(
            Cita.doctor_id == doctor_id,
            Cita.fecha >= datetime(year, month, 1),
            Cita.fecha < datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        ).all()

        citas_serializadas = [
            {
                "id": cita.cita_id,
                "fecha": cita.fecha.strftime('%Y-%m-%d'),
                "paciente": f"{cita.paciente.nombre} {cita.paciente.paterno}",
                "motivo": cita.motivo
            } for cita in citas
        ]
        return jsonify(citas_serializadas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para crear una cita (formularios de la pantalla Crear Cita)
@main_bp.route('/citas/crear', methods=['GET', 'POST'])
@login_requerido
def crear_citaPC():
    if request.method == 'POST':
        try:
            datos = {
                'paciente_id': request.form['paciente_id'],
                'doctor_id': session['doctor_id'],
                'fecha': datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M'),
                'motivo': request.form['motivo'],
                'estado': 'Pendiente'
            }
            nueva_cita = Cita(**datos)
            db.session.add(nueva_cita)
            db.session.commit()
            return jsonify({"message": "Cita creada exitosamente."}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    pacientes = Paciente.query.filter_by(doctor_id=session['doctor_id']).all()
    return render_template('citas/crear_cita.html', pacientes=pacientes)

# Ruta para eliminar una cita
@main_bp.route('/delete_cita/<int:cita_id>', methods=['POST'])
@login_requerido
def eliminar_citaPC(cita_id):
    try:
        cita = Cita.query.get_or_404(cita_id)
        if cita.doctor_id != session['doctor_id']:
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(cita)
        db.session.commit()
        flash('Cita eliminada exitosamente.', 'success')
        return redirect(url_for('main.listar_citas'))
    except Exception as e:
        flash(f'Error al eliminar la cita: {str(e)}', 'error')
        return redirect(url_for('main.listar_citas'))

# Gestión de tratamientos
# Crear tratamiento
@main_bp.route('/tratamiento/<int:paciente_id>/crear', methods=['GET', 'POST'])
@login_requerido
def crear_tratamiento(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para agregar tratamientos a este paciente.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    if request.method == 'POST':
        datos = {
            'paciente_id': paciente_id,
            'nombre': request.form['nombre'],
            'costo_total': float(request.form['costo_total']),
            'monto_pagado': 0,
            'saldo': float(request.form['costo_total']),
            'fecha_inicio': datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d'),
            'estado': 'En Progreso',
            'pieza_dental': request.form.get('pieza_dental'),
            'diagnostico': request.form.get('diagnostico'),
            'tratamiento_descripcion': request.form.get('tratamiento_descripcion'),
            'observaciones': request.form.get('observaciones')
        }
        nuevo_tratamiento = Tratamiento(**datos)
        db.session.add(nuevo_tratamiento)
        db.session.commit()
        flash('Tratamiento creado exitosamente.', 'success')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    return render_template('tratamientos/crear_tratamiento.html', paciente=paciente)

# Editar tratamiento
@main_bp.route('/tratamiento/<int:tratamiento_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para editar este tratamiento.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    if request.method == 'POST':
        tratamiento.nombre = request.form['nombre']
        tratamiento.costo_total = float(request.form['costo_total'])
        tratamiento.monto_pagado = float(request.form.get('monto_pagado', tratamiento.monto_pagado))
        tratamiento.saldo = tratamiento.costo_total - tratamiento.monto_pagado
        tratamiento.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d')
        tratamiento.fecha_fin = request.form.get('fecha_fin')
        if tratamiento.fecha_fin:
            tratamiento.fecha_fin = datetime.strptime(tratamiento.fecha_fin, '%Y-%m-%d')
        tratamiento.estado = request.form['estado']
        tratamiento.pieza_dental = request.form.get('pieza_dental')
        tratamiento.diagnostico = request.form.get('diagnostico')
        tratamiento.tratamiento_descripcion = request.form.get('tratamiento_descripcion')
        tratamiento.observaciones = request.form.get('observaciones')
        db.session.commit()
        flash('Tratamiento actualizado exitosamente.', 'success')
        return redirect(url_for('main.detalle_paciente', paciente_id=tratamiento.paciente_id))

    return render_template('tratamientos/editar_tratamiento.html', tratamiento=tratamiento)

# Eliminar tratamiento
@main_bp.route('/tratamiento/<int:tratamiento_id>/eliminar', methods=['POST'])
@login_requerido
def eliminar_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para eliminar este tratamiento.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    db.session.delete(tratamiento)
    db.session.commit()
    flash('Tratamiento eliminado exitosamente.', 'success')
    return redirect(url_for('main.detalle_paciente', paciente_id=tratamiento.paciente_id))

# Agregar pago al tratamiento (actualizar saldo)
@main_bp.route('/tratamiento/<int:tratamiento_id>/pago', methods=['POST'])
@login_requerido
def agregar_pago_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para agregar pagos a este tratamiento.', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=tratamiento.paciente_id))

    

    monto_pago = Decimal(request.form['monto_pago'])
    tratamiento.monto_pagado += monto_pago
    tratamiento.saldo = tratamiento.costo_total - tratamiento.monto_pagado
    db.session.commit()
    flash('Pago agregado exitosamente.', 'success')
    return redirect(url_for('main.detalle_paciente', paciente_id=tratamiento.paciente_id))

#
@main_bp.route('/tratamiento/<int:tratamiento_id>', methods=['GET'])
@login_requerido
def ver_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver este tratamiento.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    return render_template('tratamientos/ver_tratamiento.html', tratamiento=tratamiento)

# Crear formulario médico
@main_bp.route('/paciente/<int:paciente_id>/formulario/crear', methods=['GET', 'POST'])
@login_requerido
def crear_formulario_medico(paciente_id):
                paciente = Paciente.query.get_or_404(paciente_id)
                if paciente.doctor_id != session['doctor_id']:
                    flash('No tienes permiso para crear un formulario médico para este paciente.', 'error')
                    return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

                if request.method == 'POST':
                    pregunta_respuesta = {key: value for key, value in request.form.items() if key.startswith('pregunta_')}
                    pregunta_respuesta_json = json.dumps(pregunta_respuesta)
                    nuevo_formulario = FormularioMedico(paciente_id=paciente_id, pregunta_respuesta=pregunta_respuesta_json, fecha=datetime.now())
                    db.session.add(nuevo_formulario)
                    db.session.commit()
                    flash('Formulario médico creado exitosamente.', 'success')
                    return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

                return render_template('formularios/crear_formulario.html', paciente=paciente)

@main_bp.route('/guardar_historial', methods=['POST'])
@login_requerido
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
            return jsonify({"message": "Historial clínico guardado exitosamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error al guardar: {str(e)}"}), 500

# Exportar formulario médico a PDF
@main_bp.route('/paciente/<int:paciente_id>/formulario/pdf', methods=['GET'])
@login_requerido
def exportar_formulario_pdf(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    formulario = FormularioMedico.query.filter_by(paciente_id=paciente_id).order_by(FormularioMedico.fecha.desc()).first()

    if not formulario:
        flash('No se encontró un formulario médico para este paciente.', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle('Formulario Médico')

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(200, 750, 'Formulario Médico')

    pdf.setFont('Helvetica', 12)
    pdf.drawString(50, 720, f'Paciente: {paciente.nombre} {paciente.paterno or ""} {paciente.materno or ""}')
    pdf.drawString(50, 700, f'Cédula: {paciente.ci}')
    pdf.drawString(50, 680, f'Fecha de Nacimiento: {paciente.fecha_nacimiento}')

    y = 660
    for pregunta, respuesta in formulario.pregunta_respuesta.items():
        pdf.drawString(50, y, f'{pregunta}: {respuesta}')
        y -= 20
        if y < 50:
            pdf.showPage()
            pdf.setFont('Helvetica', 12)
            y = 750

    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f'Formulario_Paciente_{paciente_id}.pdf', mimetype='application/pdf')
from flask import (Blueprint, render_template, request, redirect, url_for, session,
                   flash, jsonify, make_response, send_file)
from sqlalchemy import cast, String
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
from datetime import date
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet ,ParagraphStyle
from reportlab.lib.enums import TA_CENTER

main_bp = Blueprint('main', __name__)
s = URLSafeTimedSerializer('clave_secreta')


# Decorador para rutas que requieren autenticación
def login_requerido(funcion):
    @wraps(funcion)
    def decorador(*args, **kwargs):
        if 'doctor_id' not in session:
            return redirect(url_for('main.iniciar_sesion'))
        return funcion(*args, **kwargs)
    return decorador

# Ruta de inicio
@main_bp.route('/')
def inicio():
    if 'doctor_id' not in session:
        flash('Por favor, inicia sesión para continuar.', 'info')
        
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
            'paterno': request.form.get('paterno'),
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


# Editar Doctor
@main_bp.route('/doctor/<int:doctor_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.doctor_id != session.get('doctor_id'):
        flash('No tienes permiso para editar este perfil.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Actualización de datos
        doctor.nombre = request.form.get('nombre')
        doctor.paterno = request.form.get('paterno')
        doctor.materno = request.form.get('materno')
        doctor.ci = request.form.get('ci')
        doctor.fecha_nacimiento = request.form.get('fecha_nacimiento')
        doctor.especialidad = request.form.get('especialidad')
        doctor.telefono = request.form.get('telefono')
        doctor.email = request.form.get('email')
        
        # Manejo de contraseña opcional con encriptación
        nueva_contraseña = request.form.get('contraseña')
        if nueva_contraseña:
            doctor.contraseña = generate_password_hash(nueva_contraseña)
        
        try:
            db.session.commit()
            flash('Perfil actualizado exitosamente.', 'success')
            return redirect(url_for('main.detalle_doctor', doctor_id=doctor_id))
        except Exception as e:
            db.session.rollback()
            flash('Hubo un error al actualizar los datos. Inténtalo de nuevo.', 'error')
    
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

    # Obtener los pacientes asociados al doctor con paginación
    page = request.args.get('page', 1, type=int)
    pacientes_paginados = Paciente.query.filter_by(doctor_id=doctor_id).paginate(page=page, per_page=10)

    # Pasar el doctor y los pacientes paginados al template
    return render_template(
        'pacientes/listar_pacientes.html', 
        pacientes=pacientes_paginados.items, 
        doctor=doctor,
        pagination=pacientes_paginados
    )

#Buscar Paciente

@main_bp.route('/pacientes/buscar', methods=['GET', 'POST'])
@login_requerido
def buscar_pacientes():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('main.iniciar_sesion'))

    query = Paciente.query.filter_by(doctor_id=doctor_id)
    
    if request.method == 'POST':
        ci = request.form.get('ci')

        if ci:
            # Usar cast para convertir `ci` a texto y luego usar ILIKE para la comparación
            query = query.filter(cast(Paciente.ci, String).ilike(f'%{ci}%'))

    page = request.args.get('page', 1, type=int)
    pacientes_paginados = query.paginate(page=page, per_page=3)

    return render_template(
        'pacientes/listar_pacientes.html', 
        pacientes=pacientes_paginados.items, 
        pagination=pacientes_paginados
    )



#Crear Paciente
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
            'paterno': request.form.get('paterno'),
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
#Detalle del Paciente

@main_bp.route('/paciente/<int:paciente_id>')
@login_requerido
def detalle_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver este paciente.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    tratamientos_activos = Tratamiento.query.filter_by(paciente_id=paciente_id, estado='En Progreso').all()
    tratamientos_finalizados = Tratamiento.query.filter_by(paciente_id=paciente_id, estado='Finalizado').all()
    citas = Cita.query.filter_by(paciente_id=paciente_id, estado='Pendiente').order_by(Cita.fecha.desc()).all()
    formulario_medico = FormularioMedico.query.filter_by(paciente_id=paciente_id).order_by(FormularioMedico.fecha.desc()).first()
    return render_template('pacientes/detalle_paciente.html', paciente=paciente, tratamientos_activos=tratamientos_activos, tratamientos_finalizados=tratamientos_finalizados, citas=citas, formulario_medico=formulario_medico)

#Editar Paciente
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
        paciente.paterno = request.form.get('paterno')
        paciente.celular = request.form.get('celular')
        paciente.estado_civil = request.form.get('estado_civil')
        paciente.ocupacion = request.form.get('ocupacion')
        db.session.commit()
        flash('Paciente actualizado exitosamente.', 'success')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    return render_template('pacientes/editar_paciente.html', paciente=paciente)
#Eliminar Paciente
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
#Listar Citas
@main_bp.route('/citas')
@login_requerido
def listar_citas():
    doctor_id = session['doctor_id']
    citas = Cita.query.filter_by(doctor_id=doctor_id).order_by(Cita.fecha.asc()).all()
    return render_template('citas/listar_citas.html', citas=citas)

# Detalle de cita
@main_bp.route('/cita/<int:cita_id>')
@login_requerido
def detalle_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    if cita.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver esta cita.', 'error')
        return redirect(url_for('main.listar_citas'))

    return render_template('citas/detalle_cita.html', cita=cita)
#Crear Citas
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
#Editar citas
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
#Eliminar Citas
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
            flash('No tienes permiso para ver estas citas.', 'error')
            return redirect(url_for('main.dashboard'))

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
                "motivo": cita.motivo,
                "estado": cita.estado
            } for cita in citas
        ]
        return jsonify(citas_serializadas)
    except Exception as e:
        flash(f'Error al obtener las citas: {str(e)}', 'error')

    
# Ruta para crear una cita (Para paciente espacifoco)
@main_bp.route('/paciente/<int:paciente_id>/cita/crear', methods=['GET', 'POST'])
@login_requerido
def crear_cita_para_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para crear una cita para este paciente.', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    if request.method == 'POST':
        try:
            datos = {
                'paciente_id': paciente_id,
                'doctor_id': session['doctor_id'],
                'fecha': datetime.strptime(request.form['fecha'], '%Y-%m-%dT%H:%M'),
                'motivo': request.form['motivo'],
                'estado': 'Pendiente'
            }
            nueva_cita = Cita(**datos)
            db.session.add(nueva_cita)
            db.session.commit()
            flash('Cita creada exitosamente.', 'success')
            return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cita: {str(e)}', 'error')

    return render_template('citas/crear_cita_paciente.html', paciente=paciente)

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
            flash('Cita creada exitosamente.', 'success')
            return redirect(url_for('main.listar_citas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cita: {str(e)}', 'error')
            return redirect(url_for('main.crear_citaPC'))
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
    
# Ruta para editar el estado de una cita (Pendiente, Cancelada, Realizada)
@main_bp.route('/cita/<int:cita_id>/editar_estado', methods=['POST'])
@login_requerido
def editar_estado_cita(cita_id):
    try:
        cita = Cita.query.get_or_404(cita_id)
        if cita.doctor_id != session['doctor_id']:
            flash('No tienes permiso para editar el estado de esta cita.', 'error')
            return redirect(url_for('main.listar_citas'))

        nuevo_estado = request.form['estado']
        cita.estado = nuevo_estado
        db.session.commit()
        flash('Estado de la cita actualizado exitosamente.', 'success')
        return redirect(url_for('main.detalle_cita', cita_id=cita_id))
    except Exception as e:
        flash(f'Error al actualizar el estado de la cita: {str(e)}', 'error')
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
    
    # Verificar permisos del doctor
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para editar este tratamiento.', 'error')
        return redirect(url_for('main.ver_tratamiento'))
    
    if request.method == 'POST':
        try:
            # Actualizar campos básicos
            tratamiento.nombre = request.form['nombre'].strip()
            tratamiento.costo_total = float(request.form['costo_total'])
            tratamiento.monto_pagado = float(request.form.get('monto_pagado', tratamiento.monto_pagado))
            tratamiento.saldo = tratamiento.costo_total - tratamiento.monto_pagado
            
            # Validar y actualizar fechas
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            
            if fecha_inicio:
                tratamiento.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            else:
                tratamiento.fecha_inicio = None
            
            if fecha_fin:
                tratamiento.fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            else:
                tratamiento.fecha_fin = None
            
            # Actualizar otros campos
            tratamiento.estado = request.form['estado'].strip()
            tratamiento.pieza_dental = request.form.get('pieza_dental', '').strip()
            tratamiento.diagnostico = request.form.get('diagnostico', '').strip()
            tratamiento.tratamiento_descripcion = request.form.get('tratamiento_descripcion', '').strip()
            tratamiento.observaciones = request.form.get('observaciones', '').strip()
            
            # Guardar cambios en la base de datos
            db.session.commit()
            flash('Tratamiento actualizado exitosamente.', 'success')
            return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento_id))
        
        except ValueError as e:
            # Manejar errores en las conversiones de datos
            db.session.rollback()
            flash(f'Error en los datos ingresados: {str(e)}', 'error')
        except Exception as e:
            # Manejar otros errores
            db.session.rollback()
            flash(f'Ocurrió un error al actualizar el tratamiento: {str(e)}', 'error')
    
    # Renderizar la plantilla con los datos del tratamiento
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
        return redirect(url_for('main.ver_tratamiento',  tratamiento_id=tratamiento_id))

    

    monto_pago = Decimal(request.form['monto_pago'])
    tratamiento.monto_pagado += monto_pago
    tratamiento.saldo = tratamiento.costo_total - tratamiento.monto_pagado
    db.session.commit()
    flash('Pago agregado exitosamente.', 'success')
    return redirect(url_for('main.ver_tratamiento',  tratamiento_id=tratamiento_id))

# Ver Tratamiento
@main_bp.route('/tratamiento/<int:tratamiento_id>', methods=['GET'])
@login_requerido
def ver_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver este tratamiento.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    return render_template('tratamientos/ver_tratamiento.html', tratamiento=tratamiento)

# Finalizar Tratamiento
@main_bp.route('/tratamiento/<int:tratamiento_id>/finalizar', methods=['POST'])
@login_requerido
def finalizar_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)

    # Verificar permisos del doctor
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para finalizar este tratamiento.', 'error')
        return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento_id))

    # Verificar si ya está finalizado
    if tratamiento.estado == 'Finalizado':
        flash('Este tratamiento ya está finalizado.', 'info')
        return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento_id))

    # Actualizar estado y fecha de finalización
    tratamiento.estado = 'Finalizado'
    tratamiento.fecha_fin = date.today()
    db.session.commit()

    flash('El tratamiento ha sido finalizado correctamente.', 'success')
    return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento_id))

# Cancelar Tratamiento
@main_bp.route('/tratamiento/<int:tratamiento_id>/cancelar', methods=['POST'])
@login_requerido
def cancelar_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para cancelar este tratamiento.', 'error')
        return redirect(url_for('main.listar_pacientes'))

    # Verificar si el tratamiento ya está cancelado
    if tratamiento.estado == "Cancelado":
        flash('El tratamiento ya ha sido cancelado.', 'info')
        return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento.tratamiento_id))

    # Cambiar el estado a "Cancelado" y registrar la fecha de fin
    tratamiento.estado = "Cancelado"
    tratamiento.fecha_fin = datetime.today().date()

    db.session.commit()
    flash('El tratamiento ha sido cancelado exitosamente.', 'success')
    return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento.tratamiento_id))
# Exportar tratamiento a PDF
@main_bp.route('/tratamiento/<int:tratamiento_id>/pdf', methods=['GET'])
@login_requerido
def generar_pdf_tratamiento(tratamiento_id):
    tratamiento = Tratamiento.query.get_or_404(tratamiento_id)
    if tratamiento.paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para generar un PDF de este tratamiento.', 'error')
        return redirect(url_for('main.ver_tratamiento', tratamiento_id=tratamiento_id))

    # Configurar buffer y documento
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del documento
    title = Paragraph("Detalle del Tratamiento", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Información del tratamiento
    tratamiento_info = [
        ["Tratamiento:", tratamiento.nombre],
        ["Paciente:", f"{tratamiento.paciente.nombre} {tratamiento.paciente.paterno or ''} {tratamiento.paciente.materno or ''}"],
        ["Costo Total:", f"{tratamiento.costo_total:.2f}"],
        ["Monto Pagado:", f"{tratamiento.monto_pagado:.2f}"],
        ["Saldo:", f"{tratamiento.saldo:.2f}"],
        ["Fecha de Inicio:", tratamiento.fecha_inicio.strftime('%Y-%m-%d')],
        ["Fecha de Fin:", tratamiento.fecha_fin.strftime('%Y-%m-%d') if tratamiento.fecha_fin else "En Progreso"],
        ["Estado:", tratamiento.estado],
        ["Pieza Dental:", tratamiento.pieza_dental or "No especificado"],
        ["Diagnóstico:", tratamiento.diagnostico or "No especificado"],
        ["Descripción del Tratamiento:", tratamiento.tratamiento_descripcion or "No especificado"],
        ["Observaciones:", tratamiento.observaciones or "No especificado"]
    ]

    # Crear tabla con la información del tratamiento
    table = Table(tratamiento_info, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)
    fecha_actual = datetime.now().strftime('%Y_%m_%d')

    return send_file(buffer, as_attachment=True, download_name=f'{tratamiento.paciente.paterno}_{tratamiento.nombre}_{fecha_actual}.pdf', mimetype='application/pdf')



#Gestion de Formularios Medicos

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

                return render_template('formularios/crear_formulario.html', paciente=paciente, paciente_id=paciente_id)

#Guardar historial medico
@main_bp.route('/guardar_historial', methods=['POST'])
@login_requerido
def guardar_historial():
    try:
        data = request.get_json()
        paciente_id = data.get('paciente_id')
        pregunta_respuesta = data.get('pregunta_respuesta')

        # Validaciones
        if not paciente_id:
            flash('ID de paciente no recibido', 'error')
            return redirect(url_for('main.listar_formulario', paciente_id=paciente_id))
        if not pregunta_respuesta:
            flash('No se recibieron respuestas', 'error')
            return redirect(url_for('main.listar_formulario', paciente_id=paciente_id))

        paciente = Paciente.query.get(paciente_id)
        if not paciente:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('main.listar_formulario', paciente_id=paciente_id))

        # Crear el historial médico
        nuevo_historial = FormularioMedico(
            paciente_id=paciente_id,
            pregunta_respuesta=pregunta_respuesta
        )
        db.session.add(nuevo_historial)
        db.session.commit()
        flash('Historial clínico guardado exitosamente', 'success')
        return redirect(url_for('main.listar_formulario', paciente_id=paciente_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar: {str(e)}', 'error')
        return redirect(url_for('main.listar_formulario', paciente_id=paciente_id))

# Exportar formulario médico a PDF
@main_bp.route('/paciente/<int:paciente_id>/formulario/pdf', methods=['GET'])
@login_requerido
def exportar_formulario_pdf(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    formulario = FormularioMedico.query.filter_by(paciente_id=paciente_id).order_by(FormularioMedico.fecha.desc()).first()

    if not formulario:
        flash('No se encontró un formulario médico para este paciente.', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    try:
        # Configurar buffer y documento
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título del documento
        title = Paragraph("Formulario Médico", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Información del paciente
        paciente_info = f"""
        <b>Paciente:</b> {paciente.nombre} {paciente.paterno or ""} {paciente.materno or ""}<br/>
        <b>Cédula:</b> {paciente.ci}<br/>
        <b>Fecha de Nacimiento:</b> {paciente.fecha_nacimiento}
        """
        elements.append(Paragraph(paciente_info, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Ordenar y estructurar datos del formulario
        orden_preguntas = [
            ("¿Ha tenido alguna operación o enfermedad grave?", "operaciones"),
            ("¿Ha tenido alguna de las siguientes enfermedades?", "enfermedades[]"),
            ("¿A qué es alérgico?", "alergias"),
            ("¿Siente dolor en el tórax después de hacer ejercicio?", "dolor_torax"),
            ("¿Le falta aire después del ejercicio?", "falta_aire"),
            ("¿Ha sangrado de forma anormal después de una extracción?", "sangrado_anormal"),
            ("¿Ha tenido algún problema grave asociado con algún tratamiento odontológico?", "problema_odontologico"),
            ("¿Ha tenido alguna enfermedad, proceso o problema no relacionado con la odontología?", "problema_no_odontologico"),
            ("¿Está tomando algún tipo de medicamento o fármaco?", "medicamento"),
            ("¿Ha tenido reacciones adversas a medicamentos?", "reacciones_medicamentos"),
            ("¿Cuál?", "detalle_reacciones_medicamentos"),
            ("Acostumbra:", "costumbres[]"),
            ("¿Tiene algún problema con:", "problemas[]"),
            ("¿Ud. ha tenido en los últimos 14 días:", "ultimos_14[]"),
            ("Exclusivo para mujeres: ¿Está usted embarazada?", "embarazo"),
            ("¿Cuántas semanas?", "semanas_embarazo"),
            ("Observaciones:", "observaciones"),
            ("Detalle Cardiopatía (opcional):", "detalle_cardiopatia"),
            ("Detalle Enfermedades Respiratorias (opcional):", "detalle_respiratorias"),
        ]

        # Tabla de preguntas y respuestas
        data = [[Paragraph("<b>Pregunta</b>", styles['Normal']), Paragraph("<b>Respuesta</b>", styles['Normal'])]]
        for pregunta, key in orden_preguntas:
            respuesta = formulario.pregunta_respuesta.get(key, "No especificado")
            # Manejar listas
            if isinstance(respuesta, list):
                respuesta = "<br/>".join(respuesta)
            data.append([Paragraph(pregunta, styles['Normal']), Paragraph(str(respuesta), styles['Normal'])])

        table = Table(data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        # Construir el PDF
        doc.build(elements)
        buffer.seek(0)

        flash('Formulario médico exportado exitosamente.', 'success')
        return send_file(buffer, as_attachment=True, download_name=f'Formulario_Paciente_{paciente_id}.pdf', mimetype='application/pdf')
    except Exception as e:
        flash(f'Error al generar el PDF: {str(e)}', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

@main_bp.route('/doctor/<int:doctor_id>/informe', methods=['GET', 'POST'])
@login_requerido
def generar_informe_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if doctor.doctor_id != session['doctor_id']:
        flash('No tienes permiso para generar informes para este doctor.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Parámetros del informe
    periodo = request.form.get('periodo', 'mensual')  # "mensual" o "anual"
    mes = int(request.form.get('mes', datetime.now().month))
    año = int(request.form.get('año', datetime.now().year))

    # Filtrar datos según el periodo
    inicio = datetime(año, mes, 1) if periodo == 'mensual' else datetime(año, 1, 1)
    fin = (datetime(año, mes + 1, 1) if mes < 12 else datetime(año + 1, 1, 1)) if periodo == 'mensual' else datetime(año + 1, 1, 1)

    # Consultas a la base de datos
    citas = Cita.query.filter(Cita.doctor_id == doctor_id, Cita.fecha >= inicio, Cita.fecha < fin).all()
    tratamientos = Tratamiento.query.filter(Tratamiento.paciente_id.in_(
        [p.paciente_id for p in Paciente.query.filter_by(doctor_id=doctor_id).all()]
    )).all()
    pacientes = Paciente.query.filter_by(doctor_id=doctor_id).all()

    # Datos del informe
    nro_pacientes = len(set(cita.paciente_id for cita in citas))
    nro_citas_pendientes = len([c for c in citas if c.estado == 'Pendiente'])
    nro_citas_completadas = len([c for c in citas if c.estado == 'Realizada'])
    nro_citas_canceladas = len([c for c in citas if c.estado == 'Cancelada'])
    nro_tratamientos = len(tratamientos)
    tratamientos_en_progreso = len([t for t in tratamientos if t.estado == 'En Progreso'])
    tratamientos_finalizados = len([t for t in tratamientos if t.estado == 'Finalizado'])
    tratamientos_cancelados = len([t for t in tratamientos if t.estado == 'Cancelado'])
    ingresos_facturados = sum(t.costo_total for t in tratamientos)
    ingresos_pagados = sum(t.monto_pagado for t in tratamientos)
    saldo_pendiente = sum(t.saldo for t in tratamientos)

    # Generar PDF
    if request.method == 'POST':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = styles['Title']
        title_style.fontSize = 20
        title_style.leading = 24
        title_style.textColor = colors.black
        
        heading_style = styles['Heading2']
        heading_style.textColor = colors.black
        heading_style.fontSize = 14
        heading_style.leading = 18

        normal_style = styles['BodyText']
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ])
        
        # Encabezado
        title = Paragraph(f"Reporte General - Dr. {doctor.nombre} {doctor.paterno or ''} {doctor.materno or ''}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<hr/>", styles['BodyText']))

        # Información del doctor
        doctor_info = [
            ["Datos:"],
            ["Nombre:", f"{doctor.nombre} {doctor.paterno or ''} {doctor.materno or ''}"],
            ["Especialidad:", doctor.especialidad or "No especificada"],
            ["CI:", doctor.ci],
            ["Teléfono:", doctor.telefono or "No especificado"],
            ["Email:", doctor.email],
            ["Total de pacientes asignados:", len(pacientes)],
            ["Ingresos totales generados:", f"${ingresos_facturados:.2f}"]
        ]
        doctor_info_table = Table(doctor_info, colWidths=[150, 350])
        doctor_info_table.setStyle(table_style)
        elements.append(doctor_info_table)
        elements.append(Spacer(1, 12))

        # Lista de pacientes
        elements.append(Paragraph("Lista de Pacientes", heading_style))
        pacientes_data = [[
            "Nombre Completo", "CI", "Fecha de Nacimiento", "Teléfono/Celular"
        ]] + [
            [
                f"{p.nombre} {p.paterno or ''} {p.materno or ''}",
                p.ci,
                p.fecha_nacimiento.strftime('%Y-%m-%d'),
                p.telefono or p.celular or "No especificado"
            ] for p in pacientes
        ]
        pacientes_table = Table(pacientes_data, colWidths=[200, 100, 150, 150])
        pacientes_table.setStyle(table_style)
        elements.append(pacientes_table)
        elements.append(Spacer(1, 12))

        # Resumen de tratamientos
        elements.append(Paragraph("Resumen de Tratamientos", heading_style))
        tratamientos_info = [
            ["Total Tratamientos:", nro_tratamientos],
            ["En Progreso:", tratamientos_en_progreso],
            ["Finalizados:", tratamientos_finalizados],
            ["Cancelados:", tratamientos_cancelados],
            ["Monto Facturado:", f"${ingresos_facturados:.2f}"],
            ["Monto Pagado:", f"${ingresos_pagados:.2f}"],
            ["Saldo Pendiente:", f"${saldo_pendiente:.2f}"]
        ]
        tratamientos_table = Table(tratamientos_info, colWidths=[200, 150])
        tratamientos_table.setStyle(table_style)
        elements.append(tratamientos_table)
        elements.append(Spacer(1, 12))

        # Resumen de citas
        elements.append(Paragraph("Resumen de Citas Médicas", heading_style))
        citas_info = [
            ["Total de Citas:", len(citas)],
            ["Pendientes:", nro_citas_pendientes],
            ["Completadas:", nro_citas_completadas],
            ["Canceladas:", nro_citas_canceladas],
        ]
        citas_table = Table(citas_info, colWidths=[200, 150])
        citas_table.setStyle(table_style)
        elements.append(citas_table)
        elements.append(Spacer(1, 12))

        # Estadísticas generales
        elements.append(Paragraph("Estadísticas Generales", heading_style))
        estadisticas_info = [
            ["Promedio de pacientes atendidos/mes:", f"{nro_pacientes:.2f}"],
            ["Ingresos promedio por tratamiento:", f"${ingresos_facturados / nro_tratamientos:.2f}" if nro_tratamientos else "$0.00"]
        ]
        estadisticas_table = Table(estadisticas_info, colWidths=[250, 200])
        estadisticas_table.setStyle(table_style)
        elements.append(estadisticas_table)
        elements.append(Spacer(1, 12))

        # Construcción del PDF
        doc.build(elements)
        buffer.seek(0)
        flash('Informe generado exitosamente.', 'success')
        return send_file(buffer, as_attachment=True, download_name=f'Informe_Dr_{doctor.nombre}_{año}_{mes}.pdf', mimetype='application/pdf')

    return render_template(
        'reportes/generar_informe.html',
        doctor=doctor,
        datetime=datetime  # Pasar datetime al contexto
    )
    

# Detalle formulario Medico
@main_bp.route('/formulario/<int:historial_id>', methods=['GET'])
@login_requerido
def detalle_formulario(historial_id):
    formulario = FormularioMedico.query.get_or_404(historial_id)
    paciente = Paciente.query.get_or_404(formulario.paciente_id)  # Obtener el paciente relacionado
    return render_template('formularios/detalle_formulario.html', formulario=formulario, paciente=paciente, paciente_id=paciente.paciente_id)



# Listar formularios médicos de un paciente
@main_bp.route('/paciente/<int:paciente_id>/formularios', methods=['GET'])
@login_requerido
def listar_formulario(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    if paciente.doctor_id != session['doctor_id']:
        flash('No tienes permiso para ver los formularios médicos de este paciente.', 'error')
        return redirect(url_for('main.dashboard'))

    formularios = FormularioMedico.query.filter_by(paciente_id=paciente_id).order_by(FormularioMedico.fecha.desc()).all()
    return render_template('formularios/listar_formulario.html', paciente=paciente, formularios=formularios,)

# Exportar formulario médico a PDF - Nueva versión
@main_bp.route('/paciente/<int:paciente_id>/formulario/<int:historial_id>/pdf', methods=['GET'])
@login_requerido
def exportar_formulario_pdf2(paciente_id, historial_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    formulario = FormularioMedico.query.filter_by(historial_id=historial_id, paciente_id=paciente_id).first()

    if not formulario:
        flash('No se encontró un formulario médico para este paciente.', 'error')
        return redirect(url_for('main.detalle_paciente', paciente_id=paciente_id))

    # Configurar buffer y documento
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título del documento
    title = Paragraph("Formulario Médico", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Información del paciente
    paciente_info = f"""
    <b>Paciente:</b> {paciente.nombre} {paciente.paterno or ""} {paciente.materno or ""}<br/>
    <b>Cédula:</b> {paciente.ci}<br/>
    <b>Fecha de Nacimiento:</b> {paciente.fecha_nacimiento}
    """
    elements.append(Paragraph(paciente_info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Ordenar y estructurar datos del formulario
    orden_preguntas = [
        ("¿Ha tenido alguna operación o enfermedad grave?", "operaciones"),
        ("¿Ha tenido alguna de las siguientes enfermedades?", "enfermedades[]"),
        ("¿A qué es alérgico?", "alergias"),
        ("¿Siente dolor en el tórax después de hacer ejercicio?", "dolor_torax"),
        ("¿Le falta aire después del ejercicio?", "falta_aire"),
        ("¿Ha sangrado de forma anormal después de una extracción?", "sangrado_anormal"),
        ("¿Ha tenido algún problema grave asociado con algún tratamiento odontológico?", "problema_odontologico"),
        ("¿Ha tenido alguna enfermedad, proceso o problema no relacionado con la odontología?", "problema_no_odontologico"),
        ("¿Está tomando algún tipo de medicamento o fármaco?", "medicamento"),
        ("¿Ha tenido reacciones adversas a medicamentos?", "reacciones_medicamentos"),
        ("¿Cuál?", "detalle_reacciones_medicamentos"),
        ("Acostumbra:", "costumbres[]"),
        ("¿Tiene algún problema con:", "problemas[]"),
        ("¿Ud. ha tenido en los últimos 14 días:", "ultimos_14[]"),
        ("Exclusivo para mujeres: ¿Está usted embarazada?", "embarazo"),
        ("¿Cuántas semanas?", "semanas_embarazo"),
        ("Observaciones:", "observaciones"),
        ("Detalle Cardiopatía (opcional):", "detalle_cardiopatia"),
        ("Detalle Enfermedades Respiratorias (opcional):", "detalle_respiratorias"),
    ]

    # Tabla de preguntas y respuestas
    data = [[Paragraph("<b>Pregunta</b>", styles['Normal']), Paragraph("<b>Respuesta</b>", styles['Normal'])]]
    for pregunta, key in orden_preguntas:
        respuesta = formulario.pregunta_respuesta.get(key, "No especificado")
        # Manejar listas
        if isinstance(respuesta, list):
            respuesta = "<br/>".join(respuesta)
        data.append([Paragraph(pregunta, styles['Normal']), Paragraph(str(respuesta), styles['Normal'])])

    table = Table(data, colWidths=[200, 300])
    table.setStyle(TableStyle([  
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Construir el PDF
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f'Formulario_Paciente_{paciente_id}_Historial_{historial_id}.pdf', mimetype='application/pdf')

# Controlador para eliminar el formulario médico
@main_bp.route('/formulario/<int:historial_id>/eliminar', methods=['POST'])
@login_requerido
def eliminar_formulario(historial_id):
    # Buscar el formulario médico con el historial_id proporcionado
    formulario = FormularioMedico.query.get_or_404(historial_id)
    
    # Eliminar el formulario médico
    try:
        db.session.delete(formulario)
        db.session.commit()
        flash('Formulario médico eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el formulario médico: {e}', 'error')
    
    # Redirigir a la lista de formularios
    return redirect(url_for('main.listar_formulario', paciente_id=formulario.paciente_id))


# Controlador para editar el formulario médico
@main_bp.route('/formulario/<int:historial_id>/editar', methods=['GET', 'POST'])
@login_requerido
def editar_formulario(historial_id):
    # Obtener el formulario médico
    formulario = FormularioMedico.query.get_or_404(historial_id)
    
    if request.method == 'POST':
        # Aquí procesamos los datos enviados desde el formulario
        formulario.pregunta_respuesta = request.form.to_dict()
        
        try:
            # Guardamos los cambios en la base de datos
            db.session.commit()
            flash('Formulario médico actualizado correctamente.', 'success')
            return redirect(url_for('main.detalle_formulario', historial_id=formulario.historial_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el formulario: {e}', 'error')

    # Renderizamos el formulario de edición
    return render_template('formularios/editar_formulario.html', formulario=formulario)





from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Doctor, Paciente

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    doctores = Doctor.query.all()
    pacientes = Paciente.query.all()
    return render_template('index.html', doctores=doctores, pacientes=pacientes)

@main_bp.route('/doctor/create', methods=['GET', 'POST'])
def create_doctor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        especialidad = request.form.get('especialidad')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        doctor = Doctor(nombre=nombre, especialidad=especialidad, telefono=telefono, email=email)
        db.session.add(doctor)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_doctor.html')

@main_bp.route('/paciente/create', methods=['GET', 'POST'])
def create_paciente():
    doctores = Doctor.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        doctor_id = request.form['doctor_id']
        paciente = Paciente(nombre=nombre, fecha_nacimiento=fecha_nacimiento, direccion=direccion, telefono=telefono, doctor_id=doctor_id)
        db.session.add(paciente)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_paciente.html', doctores=doctores)

@main_bp.route('/delete/<string:entity>/<int:id>', methods=['POST'])
def delete_entity(entity, id):
    if entity == "doctor":
        Doctor.query.filter_by(doctor_id=id).delete()
    elif entity == "paciente":
        Paciente.query.filter_by(paciente_id=id).delete()
    db.session.commit()
    return redirect(url_for('main.index'))

from app import db
from datetime import datetime
from sqlalchemy import String

class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    paterno = db.Column(db.String(100))
    materno = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    contraseña = db.Column(db.String(255), nullable=False)

    pacientes = db.relationship('Paciente', backref='doctor', lazy=True, cascade="all, delete-orphan")
    citas = db.relationship('Cita', backref='doctor', lazy=True, cascade="all, delete-orphan")


class Paciente(db.Model):
    paciente_id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(String, nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    paterno = db.Column(db.String(100))
    materno = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(15))
    celular = db.Column(db.String(15))
    estado_civil = db.Column(db.String(50))
    ocupacion = db.Column(db.String(100))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)

    tratamientos = db.relationship('Tratamiento', backref='paciente', lazy=True, cascade="all, delete-orphan")
    citas = db.relationship('Cita', backref='paciente', lazy=True, cascade="all, delete-orphan")
    formularios_medicos = db.relationship('FormularioMedico', backref='paciente', lazy=True, cascade="all, delete-orphan")


class Tratamiento(db.Model):
    tratamiento_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)
    monto_pagado = db.Column(db.Numeric(10, 2), default=0)
    saldo = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    estado = db.Column(db.String(50), default='En Progreso')
    pieza_dental = db.Column(db.String(10))
    diagnostico = db.Column(db.Text)
    tratamiento_descripcion = db.Column(db.Text)
    observaciones = db.Column(db.Text)

    citas = db.relationship('Cita', backref='tratamiento', lazy=True, cascade="all, delete-orphan")


class Cita(db.Model):
    cita_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    tratamiento_id = db.Column(db.Integer, db.ForeignKey('tratamiento.tratamiento_id'))
    fecha = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.Text)
    estado = db.Column(db.String(50), default='Pendiente')

    __table_args__ = (db.UniqueConstraint('paciente_id', 'doctor_id', 'fecha', name='uniq_cita_paciente_doctor'),)


class FormularioMedico(db.Model):
    historial_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id'), nullable=False)
    fecha = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    pregunta_respuesta = db.Column(db.JSON, nullable=False)
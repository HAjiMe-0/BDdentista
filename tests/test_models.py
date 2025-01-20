# tests/test_models.py

import pytest
from app.models import Doctor, Paciente, Tratamiento, Cita, FormularioMedico
from datetime import datetime, date
from app import db

def test_create_doctor(test_client):
    """
    Prueba para crear un doctor y verificar que se haya guardado correctamente.
    """
    new_doctor = Doctor(
        ci=12345678,
        nombre="Juan",
        paterno="Perez",
        materno="Gomez",
        fecha_nacimiento=date(1985, 5, 20),
        especialidad="Ortodoncia",
        telefono="123456789",
        email="juan.perez@example.com",
        contraseña="securepassword"
    )
    db.session.add(new_doctor)
    db.session.commit()

    doctor = Doctor.query.filter_by(email="juan.perez@example.com").first()
    assert doctor is not None
    assert doctor.nombre == "Juan"

def test_create_paciente(test_client):
    """
    Prueba para crear un paciente asociado a un doctor y verificar la relación.
    """
    doctor = Doctor.query.first()
    assert doctor is not None, "Se requiere al menos un doctor para esta prueba."

    new_paciente = Paciente(
        ci="98765432",
        nombre="Maria",
        paterno="Lopez",
        materno="Diaz",
        fecha_nacimiento=date(1990, 7, 15),
        direccion="Calle Falsa 123",
        telefono="987654321",
        celular="789456123",
        estado_civil="Soltera",
        ocupacion="Ingeniera",
        doctor_id=doctor.doctor_id
    )
    db.session.add(new_paciente)
    db.session.commit()

    paciente = Paciente.query.filter_by(ci="98765432").first()
    assert paciente is not None
    assert paciente.doctor.nombre == "Juan"

def test_create_tratamiento(test_client):
    """
    Prueba para crear un tratamiento y verificar sus atributos.
    """
    paciente = Paciente.query.first()
    assert paciente is not None, "Se requiere al menos un paciente para esta prueba."

    new_tratamiento = Tratamiento(
        paciente_id=paciente.paciente_id,
        nombre="Blanqueamiento dental",
        costo_total=200.00,
        monto_pagado=50.00,
        saldo=150.00,
        fecha_inicio=date.today(),
        estado="En Progreso",
        pieza_dental="D12",
        diagnostico="Dientes manchados",
        tratamiento_descripcion="Blanqueamiento dental intensivo.",
        observaciones="Paciencia requerida."
    )
    db.session.add(new_tratamiento)
    db.session.commit()

    tratamiento = Tratamiento.query.filter_by(nombre="Blanqueamiento dental").first()
    assert tratamiento is not None
    assert tratamiento.paciente.nombre == "Maria"

def test_create_cita(test_client):
    """
    Prueba para crear una cita y verificar las relaciones.
    """
    paciente = Paciente.query.first()
    doctor = Doctor.query.first()
    assert paciente is not None, "Se requiere al menos un paciente para esta prueba."
    assert doctor is not None, "Se requiere al menos un doctor para esta prueba."

    new_cita = Cita(
        paciente_id=paciente.paciente_id,
        doctor_id=doctor.doctor_id,
        fecha=datetime.now(),
        motivo="Chequeo general",
        estado="Pendiente"
    )
    db.session.add(new_cita)
    db.session.commit()

    cita = Cita.query.filter_by(motivo="Chequeo general").first()
    assert cita is not None
    assert cita.paciente.nombre == "Maria"
    assert cita.doctor.nombre == "Juan"

def test_create_formulario_medico(test_client):
    """
    Prueba para crear un formulario médico asociado a un paciente.
    """
    paciente = Paciente.query.first()
    assert paciente is not None, "Se requiere al menos un paciente para esta prueba."

    new_formulario = FormularioMedico(
        paciente_id=paciente.paciente_id,
        pregunta_respuesta={"¿Es alérgico?": "No", "¿Fuma?": "Sí"}
    )
    db.session.add(new_formulario)
    db.session.commit()

    formulario = FormularioMedico.query.filter_by(paciente_id=paciente.paciente_id).first()
    assert formulario is not None
    assert formulario.pregunta_respuesta["¿Es alérgico?"] == "No"

# tests/test_integration.py

from app.models import Doctor, Paciente, Tratamiento, Cita
from datetime import datetime

def test_create_doctor_and_paciente(test_client, db_session):
    """
    Prueba para verificar la integración al crear un doctor y un paciente asociado.
    """
    # Crear un doctor
    doctor_data = {
        "ci": 12345678,
        "nombre": "Carlos",
        "paterno": "Fernandez",
        "materno": "Lopez",
        "fecha_nacimiento": "1980-01-15",
        "especialidad": "Cirugía Dental",
        "telefono": "123456789",
        "email": "carlos.fernandez@example.com",
        "contraseña": "securepassword",
    }
    doctor = Doctor(**doctor_data)
    db_session.add(doctor)
    db_session.commit()

    # Verificar que el doctor se creó correctamente
    assert doctor.doctor_id is not None

    # Crear un paciente asociado al doctor
    paciente_data = {
        "ci": "87654321",
        "nombre": "Ana",
        "paterno": "Gonzalez",
        "materno": "Rojas",
        "fecha_nacimiento": "1995-03-10",
        "direccion": "Avenida Siempre Viva 742",
        "telefono": "123456789",
        "celular": "987654321",
        "estado_civil": "Casada",
        "ocupacion": "Abogada",
        "doctor_id": doctor.doctor_id,
    }
    paciente = Paciente(**paciente_data)
    db_session.add(paciente)
    db_session.commit()

    # Verificar que el paciente se creó correctamente y está asociado al doctor
    assert paciente.paciente_id is not None
    assert paciente.doctor_id == doctor.doctor_id

def test_create_tratamiento_and_cita(test_client, db_session):
    """
    Prueba para verificar la integración al crear un tratamiento y una cita asociada a un paciente y un doctor.
    """
    # Crear un doctor
    doctor = Doctor(
        ci=98765432,
        nombre="Laura",
        paterno="Mendoza",
        materno="Torres",
        fecha_nacimiento="1975-08-25",
        especialidad="Ortodoncia",
        telefono="987654321",
        email="laura.mendoza@example.com",
        contraseña="password123",
    )
    db_session.add(doctor)
    db_session.commit()

    # Crear un paciente
    paciente = Paciente(
        ci="12345678",
        nombre="Pedro",
        paterno="Ramirez",
        materno="Gutierrez",
        fecha_nacimiento="2000-04-22",
        direccion="Calle Falsa 123",
        telefono="1122334455",
        celular="5566778899",
        estado_civil="Soltero",
        ocupacion="Estudiante",
        doctor_id=doctor.doctor_id,
    )
    db_session.add(paciente)
    db_session.commit()

    # Crear un tratamiento asociado al paciente
    tratamiento = Tratamiento(
        paciente_id=paciente.paciente_id,
        nombre="Limpieza Dental",
        costo_total=100.00,
        monto_pagado=50.00,
        saldo=50.00,
        fecha_inicio=datetime.now().date(),
        estado="En Progreso",
        pieza_dental="32",
        diagnostico="Placa dental",
        tratamiento_descripcion="Limpieza de sarro",
        observaciones="Sin complicaciones",
    )
    db_session.add(tratamiento)
    db_session.commit()

    # Verificar que el tratamiento se creó correctamente
    assert tratamiento.tratamiento_id is not None
    assert tratamiento.paciente_id == paciente.paciente_id

    # Crear una cita asociada al tratamiento, paciente y doctor
    cita = Cita(
        paciente_id=paciente.paciente_id,
        doctor_id=doctor.doctor_id,
        tratamiento_id=tratamiento.tratamiento_id,
        fecha=datetime.now(),
        motivo="Primera consulta",
        estado="Pendiente",
    )
    db_session.add(cita)
    db_session.commit()

    # Verificar que la cita se creó correctamente
    assert cita.cita_id is not None
    assert cita.paciente_id == paciente.paciente_id
    assert cita.doctor_id == doctor.doctor_id
    assert cita.tratamiento_id == tratamiento.tratamiento_id

def test_delete_cascade(test_client, db_session):
    """
    Prueba para verificar el borrado en cascada.
    """
    # Crear un doctor y un paciente
    doctor = Doctor(
        ci=54321098,
        nombre="Luis",
        paterno="Vargas",
        materno="Luna",
        fecha_nacimiento="1982-11-05",
        especialidad="Endodoncia",
        telefono="333222111",
        email="luis.vargas@example.com",
        contraseña="securepass",
    )
    db_session.add(doctor)
    db_session.commit()

    paciente = Paciente(
        ci="11122233",
        nombre="Claudia",
        paterno="Martinez",
        materno="Hernandez",
        fecha_nacimiento="1998-12-30",
        direccion="Zona Central",
        telefono="5566778899",
        celular="7788996655",
        estado_civil="Soltera",
        ocupacion="Contadora",
        doctor_id=doctor.doctor_id,
    )
    db_session.add(paciente)
    db_session.commit()

    # Crear un tratamiento y una cita para el paciente
    tratamiento = Tratamiento(
        paciente_id=paciente.paciente_id,
        nombre="Blanqueamiento Dental",
        costo_total=200.00,
        monto_pagado=100.00,
        saldo=100.00,
        fecha_inicio=datetime.now().date(),
        estado="En Progreso",
    )
    db_session.add(tratamiento)
    db_session.commit()

    cita = Cita(
        paciente_id=paciente.paciente_id,
        doctor_id=doctor.doctor_id,
        tratamiento_id=tratamiento.tratamiento_id,
        fecha=datetime.now(),
        motivo="Seguimiento",
        estado="Pendiente",
    )
    db_session.add(cita)
    db_session.commit()

    # Eliminar el paciente y verificar que el tratamiento y la cita también se eliminen
    db_session.delete(paciente)
    db_session.commit()

    assert Tratamiento.query.get(tratamiento.tratamiento_id) is None
    assert Cita.query.get(cita.cita_id) is None

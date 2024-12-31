from app import db

class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)  # ID único del doctor
    ci = db.Column(db.Integer, nullable=False)           # Nombre del doctor
    nombre = db.Column(db.String(100), nullable=False)   # Nombre del doctor
    paterno = db.Column(db.String(100))                  # Apellido paterno
    materno = db.Column(db.String(100))                  # Apellido materno
    especialidad = db.Column(db.String(100))             # Especialidad
    telefono = db.Column(db.String(15))                  # Teléfono de contacto
    fecha_nacimiento = db.Column(db.Date, nullable=False) # Fecha de nacimiento
    email = db.Column(db.String(100), unique=True)       # Correo único
    contraseña = db.Column(db.String(255), nullable=False)  # Contraseña (encriptada)

    # Relación con pacientes
    pacientes = db.relationship('Paciente', backref='doctor', lazy=True)

class Paciente(db.Model):
    paciente_id = db.Column(db.Integer, primary_key=True)  # ID único del paciente
    ci = db.Column(db.Integer, nullable=False)            # Cédula de identidad
    nombre = db.Column(db.String(100), nullable=False)    # Nombre del paciente
    paterno = db.Column(db.String(100))                   # Apellido paterno
    materno = db.Column(db.String(100))                   # Apellido materno
    fecha_nacimiento = db.Column(db.Date, nullable=False) # Fecha de nacimiento
    direccion = db.Column(db.Text)                        # Dirección
    telefono = db.Column(db.String(15))                   # Teléfono fijo
    celular = db.Column(db.String(15))                    # Teléfono celular
    estado_civil = db.Column(db.String(50))               # Estado civil
    ocupacion = db.Column(db.String(100))                 # Ocupación
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)  # ID del doctor asignado


#Modelo para ficha dental
class FichaDental(db.Model):
    __tablename__ = 'ficha_dental'

    ficha_id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id', ondelete='CASCADE'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)  # Fecha manualmente ingresada
    pieza_dental = db.Column(db.String(10), nullable=True)
    diagnostico = db.Column(db.Text, nullable=True)
    tratamiento = db.Column(db.Text, nullable=True)
    costo = db.Column(db.Numeric(10, 2), nullable=True)
    al_contado = db.Column(db.Numeric(10, 2), nullable=True)
    saldo = db.Column(db.Numeric(10, 2), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)  # Asegúrate de que se llame 'observaciones'

    paciente = db.relationship('Paciente', backref=db.backref('fichas_dentales', cascade='all, delete-orphan'))



    
class Cita(db.Model):
    cita_id = db.Column(db.Integer, primary_key=True)     # ID único de la cita
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id'), nullable=False)  # ID del paciente
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)      # ID del doctor
    fecha = db.Column(db.DateTime, nullable=False)         # Fecha y hora de la cita
    motivo = db.Column(db.Text)                           # Motivo de la cita
    estado = db.Column(db.String(50), default='Pendiente') # Estado de la cita (Pendiente, Confirmada, etc.)

    # Relación con paciente y doctor
    paciente = db.relationship('Paciente', backref='citas', lazy=True)
    doctor = db.relationship('Doctor', backref='citas', lazy=True)

    # Restricción única para evitar citas duplicadas para un mismo paciente y doctor en la misma fecha
    __table_args__ = (
        db.UniqueConstraint('paciente_id', 'doctor_id', 'fecha', name='_unique_cita_paciente_doctor_fecha'),
    )
    

class FormularioMedico(db.Model):
    __tablename__ = 'formulario_medico'

    formulario_id = db.Column(db.Integer, primary_key=True)  # ID único del formulario
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.paciente_id', ondelete='CASCADE'), nullable=False)  # Relación con Paciente
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)  # Fecha de creación
    operacion_grave = db.Column(db.Boolean, default=False)  # Si tuvo una operación grave
    detalle_operacion_grave = db.Column(db.Text)            # Detalle de operación grave
    fiebre_reumatica = db.Column(db.Boolean, default=False)  # Fiebre reumática
    cardiopatia = db.Column(db.Boolean, default=False)      # Cardiopatía
    detalle_cardiopatia = db.Column(db.Text)                # Detalle de la cardiopatía
    enfermedades_respiratorias = db.Column(db.Boolean, default=False)  # Enfermedades respiratorias
    detalle_enfermedades_respiratorias = db.Column(db.Text) # Detalle de enfermedades respiratorias
    enfermedades_renales = db.Column(db.Boolean, default=False)  # Enfermedades renales
    asma = db.Column(db.Boolean, default=False)             # Asma
    mareos = db.Column(db.Boolean, default=False)           # Mareos
    diabetes = db.Column(db.Boolean, default=False)         # Diabetes
    artritis = db.Column(db.Boolean, default=False)         # Artritis
    ulcera_gastrica = db.Column(db.Boolean, default=False)  # Úlcera gástrica
    tuberculosis = db.Column(db.Boolean, default=False)     # Tuberculosis
    enfermedades_venereas = db.Column(db.Boolean, default=False)  # Enfermedades venéreas
    presion_alta = db.Column(db.Boolean, default=False)     # Presión alta
    presion_baja = db.Column(db.Boolean, default=False)     # Presión baja
    hepatitis = db.Column(db.Boolean, default=False)        # Hepatitis
    sinusitis = db.Column(db.Boolean, default=False)        # Sinusitis
    vih = db.Column(db.Boolean, default=False)              # VIH
    alergias = db.Column(db.Boolean, default=False)         # Alergias
    detalle_alergias = db.Column(db.Text)                   # Detalle de alergias
    dolor_torax = db.Column(db.Boolean, default=False)      # Dolor en el tórax tras ejercicio
    falta_aire = db.Column(db.Boolean, default=False)       # Falta de aire tras ejercicio
    sangrado_anormal = db.Column(db.Boolean, default=False) # Sangrado anormal tras extracción
    problema_odontologico = db.Column(db.Boolean, default=False)  # Problema odontológico grave
    problema_no_odontologico = db.Column(db.Boolean, default=False)  # Problema no odontológico grave
    medicamentos = db.Column(db.Boolean, default=False)     # Si toma medicamentos
    reaccion_medicamentos = db.Column(db.Boolean, default=False)  # Reacción adversa a medicamentos
    detalle_reaccion_medicamentos = db.Column(db.Text)      # Detalle de reacción a medicamentos
    observaciones = db.Column(db.Text)                      # Observaciones adicionales

    # Relación con el paciente
    paciente = db.relationship('Paciente', backref=db.backref('formularios_medicos', cascade='all, delete-orphan'))

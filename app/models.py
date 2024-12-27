from app import db

class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)  # ID único del doctor
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

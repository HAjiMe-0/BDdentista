from app import db

class Doctor(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    contraseña = db.Column(db.String(255), unique=True)


class Paciente(db.Model):
    paciente_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.Text)
    telefono = db.Column(db.String(15))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    contraseña = db.Column(db.String(255), unique=True)
    
    doctor = db.relationship('Doctor', backref=db.backref('pacientes', lazy=True))

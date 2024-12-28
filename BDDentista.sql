
-- Tabla Doctor con campo de contraseña
CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,  -- ID único del doctor
    ci INT NOT NULL, --ci del doctor
    nombre VARCHAR(100) NOT NULL,  -- Nombre del doctor
    paterno VARCHAR(100),           -- Apellido paterno
    materno VARCHAR(100),           -- Apellido materno
    fecha_nacimiento DATE NOT NULL, -- Fecha de nacimiento del paciente
    especialidad VARCHAR(100),     -- Especialidad del doctor
    telefono VARCHAR(15),          -- Teléfono de contacto
    email VARCHAR(100) UNIQUE,     -- Correo electrónico único
    contraseña VARCHAR(255) NOT NULL  -- Contraseña del doctor
);

-- Tabla Paciente con campo de contraseña
CREATE TABLE paciente (
    paciente_id SERIAL PRIMARY KEY, -- ID único del paciente
    ci INT NOT NULL,                -- Cédula de identidad
    nombre VARCHAR(100) NOT NULL,   -- Nombre del paciente
    paterno VARCHAR(100),           -- Apellido paterno
    materno VARCHAR(100),           -- Apellido materno
    fecha_nacimiento DATE NOT NULL, -- Fecha de nacimiento del paciente
    direccion TEXT,                 -- Dirección del paciente
    telefono VARCHAR(15),           -- Teléfono fijo
    celular VARCHAR(15),            -- Teléfono celular
    estado_civil VARCHAR(50),       -- Estado civil del paciente
    ocupacion VARCHAR(100),         -- Ocupación del paciente
    doctor_id INT NOT NULL,         -- ID del doctor asignado

    CONSTRAINT fk_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE -- Si se elimina un doctor, se eliminan sus pacientes
);

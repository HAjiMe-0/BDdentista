
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

-- Tabla Ficha Dental
CREATE TABLE ficha_dental (
    ficha_id SERIAL PRIMARY KEY,     -- ID único de la ficha dental
    paciente_id INT NOT NULL,        -- ID del paciente asociado
    fecha DATE NOT NULL,             -- Fecha de la ficha
    pieza_dental VARCHAR(10),        -- Pieza dental afectada
    diagnostico TEXT,                -- Diagnóstico realizado
    tratamiento TEXT,                -- Tratamiento sugerido
    costo DECIMAL(10, 2),            -- Costo del tratamiento
    al_contado DECIMAL(10, 2),       -- Monto pagado al contado
    saldo DECIMAL(10, 2),            -- Saldo restante
    observaciones TEXT,              -- Observaciones adicionales

    CONSTRAINT fk_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES paciente(paciente_id)
        ON DELETE CASCADE
);

-- Tabla Cita
CREATE TABLE cita (
    cita_id SERIAL PRIMARY KEY,          -- ID único de la cita
    paciente_id INT NOT NULL,            -- ID del paciente
    doctor_id INT NOT NULL,              -- ID del doctor
    fecha TIMESTAMP NOT NULL,            -- Fecha y hora de la cita
    motivo TEXT,                         -- Motivo de la cita
    estado VARCHAR(50) DEFAULT 'Pendiente', -- Estado de la cita (Pendiente, Confirmada, etc.)

    CONSTRAINT fk_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES paciente(paciente_id)
        ON DELETE CASCADE, -- Si se elimina un paciente, se eliminan sus citas

    CONSTRAINT fk_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE, -- Si se elimina un doctor, se eliminan sus citas

    CONSTRAINT uniq_cita_paciente_doctor
        UNIQUE (paciente_id, doctor_id, fecha) -- Evitar que un paciente tenga dos citas con el mismo doctor en la misma hora
);

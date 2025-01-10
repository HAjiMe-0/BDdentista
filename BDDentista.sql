-- Tabla Doctor
CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,         -- ID único del doctor
    ci INT NOT NULL,                      -- Cédula de identidad del doctor
    nombre VARCHAR(100) NOT NULL,         -- Nombre del doctor
    paterno VARCHAR(100),                 -- Apellido paterno
    materno VARCHAR(100),                 -- Apellido materno
    fecha_nacimiento DATE NOT NULL,       -- Fecha de nacimiento
    especialidad VARCHAR(100),            -- Especialidad del doctor
    telefono VARCHAR(15),                 -- Teléfono de contacto
    email VARCHAR(100) UNIQUE,            -- Correo electrónico único
    contraseña VARCHAR(255) NOT NULL      -- Contraseña del doctor
);

-- Tabla Paciente
CREATE TABLE paciente (
    paciente_id SERIAL PRIMARY KEY,       -- ID único del paciente
    ci INT NOT NULL,                      -- Cédula de identidad
    nombre VARCHAR(100) NOT NULL,         -- Nombre del paciente
    paterno VARCHAR(100),                 -- Apellido paterno
    materno VARCHAR(100),                 -- Apellido materno
    fecha_nacimiento DATE NOT NULL,       -- Fecha de nacimiento
    direccion TEXT,                       -- Dirección del paciente
    telefono VARCHAR(15),                 -- Teléfono fijo
    celular VARCHAR(15),                  -- Teléfono celular
    estado_civil VARCHAR(50),             -- Estado civil del paciente
    ocupacion VARCHAR(100),               -- Ocupación del paciente
    doctor_id INT NOT NULL,               -- ID del doctor asignado

    CONSTRAINT fk_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE                 -- Si se elimina un doctor, se eliminan sus pacientes
);


-- Tabla Tratamiento
CREATE TABLE tratamiento (
    tratamiento_id SERIAL PRIMARY KEY,    -- ID único del tratamiento
    paciente_id INT NOT NULL,             -- ID del paciente asociado
    nombre VARCHAR(255) NOT NULL,         -- Nombre o descripción del tratamiento
    costo_total DECIMAL(10, 2) NOT NULL,  -- Costo total del tratamiento
    monto_pagado DECIMAL(10, 2) DEFAULT 0,-- Monto pagado hasta el momento
    saldo DECIMAL(10, 2) NOT NULL,        -- Saldo restante del tratamiento
    fecha_inicio DATE NOT NULL,           -- Fecha de inicio del tratamiento
    fecha_fin DATE,                       -- Fecha de finalización (opcional)
    estado VARCHAR(50) DEFAULT 'En Progreso', -- Estado del tratamiento
    pieza_dental VARCHAR(10),             -- Pieza dental afectada (si aplica)
    diagnostico TEXT,                     -- Diagnóstico realizado
    tratamiento_descripcion TEXT,         -- Descripción específica del tratamiento
    observaciones TEXT,                   -- Observaciones adicionales

    CONSTRAINT fk_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES paciente(paciente_id)
        ON DELETE CASCADE
);

-- Tabla Cita
CREATE TABLE cita (
    cita_id SERIAL PRIMARY KEY,           -- ID único de la cita
    paciente_id INT NOT NULL,             -- ID del paciente
    doctor_id INT NOT NULL,               -- ID del doctor
    tratamiento_id INT,                   -- ID del tratamiento asociado (opcional)
    fecha TIMESTAMP NOT NULL,             -- Fecha y hora de la cita
    motivo TEXT,                          -- Motivo de la cita
    estado VARCHAR(50) DEFAULT 'Pendiente', -- Estado de la cita

    CONSTRAINT fk_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES paciente(paciente_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_tratamiento
        FOREIGN KEY (tratamiento_id)
        REFERENCES tratamiento(tratamiento_id)
        ON DELETE SET NULL,              -- Si se elimina un tratamiento, la cita queda sin tratamiento asociado

    CONSTRAINT uniq_cita_paciente_doctor
        UNIQUE (paciente_id, doctor_id, fecha) -- Evitar que un paciente tenga dos citas con el mismo doctor a la misma hora
);

-- Tabla Formulario Médico
CREATE TABLE formulario_medico (
    historial_id SERIAL PRIMARY KEY,      -- ID único del formulario médico
    paciente_id INT NOT NULL,             -- ID del paciente asociado
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de creación del formulario
    pregunta_respuesta JSONB NOT NULL,    -- Preguntas y respuestas en formato JSONB

    CONSTRAINT fk_paciente
        FOREIGN KEY (paciente_id)
        REFERENCES paciente(paciente_id)
        ON DELETE CASCADE
);

-- Si hacemos un cambio a la bd lo guardan en aca para que todos podamos ver plocs 

-- Tabla Doctor con campo de contraseña
CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,  -- ID único del doctor
    nombre VARCHAR(100) NOT NULL,  -- Nombre del doctor
    especialidad VARCHAR(100),     -- Especialidad del doctor
    telefono VARCHAR(15),          -- Teléfono de contacto
    email VARCHAR(100) UNIQUE,     -- Correo electrónico único
    contraseña VARCHAR(255) NOT NULL  -- Contraseña del doctor
);

-- Tabla Paciente con campo de contraseña
CREATE TABLE paciente (
    paciente_id SERIAL PRIMARY KEY, -- ID único del paciente
    nombre VARCHAR(100) NOT NULL,   -- Nombre del paciente
    fecha_nacimiento DATE NOT NULL, -- Fecha de nacimiento del paciente
    direccion TEXT,                 -- Dirección del paciente
    telefono VARCHAR(15),           -- Teléfono de contacto
    doctor_id INT NOT NULL,         -- ID del doctor asignado
-- Al paciente le quietare la contraseña hasta que hagamos el modulo de pacientes en la App 
--    contraseña VARCHAR(255) NOT NULL, -- Contraseña del paciente 
    CONSTRAINT fk_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctor(doctor_id)
        ON DELETE CASCADE -- Si se elimina un doctor, se eliminan sus pacientes
);

-- Insertar datos en la tablas
-- Insertar datos en la tabla doctor
INSERT INTO doctor (nombre, especialidad, telefono, email, contraseña)
VALUES 
('Dr. Juan Pérez', 'Cardiología', '555-1234', 'juan.perez@hospital.com', '12345'),
('Dra. Ana López', 'Pediatría', '555-5678', 'ana.lopez@hospital.com', '12345');

-- Insertar datos en la tabla paciente
INSERT INTO paciente (nombre, fecha_nacimiento, direccion, telefono, doctor_id)
VALUES
('Carlos Martínez', '1980-05-15', 'Av. Siempre Viva 123', '555-9876', 1),
('María González', '1992-08-25', 'Calle Falsa 456', '555-6543', 1),
('Lucía Rodríguez', '2015-11-10', 'Calle Larga 789', '555-1122', 2),
('Pedro Sánchez', '2010-03-20', 'Plaza Central 101', '555-3344', 2);

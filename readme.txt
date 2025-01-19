# BDdentista

BDdentista es una aplicación web diseñada para la gestión de una clínica dental. Permite a los doctores administrar pacientes, citas, tratamientos y formularios médicos de manera eficiente.

## Funcionalidades Generales

### Autenticación y Registro
- **Inicio de Sesión**: Los doctores pueden iniciar sesión con su correo electrónico y contraseña.
- **Registro**: Los nuevos doctores pueden registrarse proporcionando su información personal y profesional.

### Gestión de Doctores
- **Perfil del Doctor**: Los doctores pueden ver y editar su perfil, incluyendo su información personal y profesional.
- **Cerrar Sesión**: Los doctores pueden cerrar sesión de manera segura.

### Dashboard
- **Vista General**: El dashboard proporciona una vista general de las funcionalidades principales, incluyendo la gestión de pacientes, citas y reportes.

### Gestión de Pacientes
- **Listar Pacientes**: Los doctores pueden ver una lista de todos sus pacientes.
- **Buscar Pacientes**: Los doctores pueden buscar pacientes por su cédula de identidad.
- **Crear Paciente**: Los doctores pueden agregar nuevos pacientes proporcionando su información personal.
- **Editar Paciente**: Los doctores pueden actualizar la información de los pacientes existentes.
- **Eliminar Paciente**: Los doctores pueden eliminar pacientes de la base de datos.
- **Detalle del Paciente**: Los doctores pueden ver la información detallada de un paciente, incluyendo sus tratamientos y citas.

### Gestión de Citas
- **Listar Citas**: Los doctores pueden ver una lista de todas las citas programadas.
- **Crear Cita**: Los doctores pueden programar nuevas citas para sus pacientes.
- **Editar Cita**: Los doctores pueden actualizar la información de las citas existentes.
- **Eliminar Cita**: Los doctores pueden cancelar citas.
- **Detalle de Cita**: Los doctores pueden ver la información detallada de una cita específica.

### Gestión de Tratamientos
- **Crear Tratamiento**: Los doctores pueden agregar nuevos tratamientos para sus pacientes.
- **Editar Tratamiento**: Los doctores pueden actualizar la información de los tratamientos existentes.
- **Eliminar Tratamiento**: Los doctores pueden eliminar tratamientos de la base de datos.
- **Agregar Pago**: Los doctores pueden registrar pagos realizados por los pacientes para sus tratamientos.
- **Finalizar Tratamiento**: Los doctores pueden marcar tratamientos como finalizados.
- **Cancelar Tratamiento**: Los doctores pueden cancelar tratamientos.
- **Detalle de Tratamiento**: Los doctores pueden ver la información detallada de un tratamiento específico.
- **Exportar Tratamiento a PDF**: Los doctores pueden generar un PDF con la información detallada de un tratamiento.

### Gestión de Formularios Médicos
- **Crear Formulario Médico**: Los doctores pueden crear formularios médicos para sus pacientes.
- **Editar Formulario Médico**: Los doctores pueden actualizar la información de los formularios médicos existentes.
- **Eliminar Formulario Médico**: Los doctores pueden eliminar formularios médicos de la base de datos.
- **Detalle de Formulario Médico**: Los doctores pueden ver la información detallada de un formulario médico específico.
- **Listar Formularios Médicos**: Los doctores pueden ver una lista de todos los formularios médicos de un paciente.
- **Exportar Formulario Médico a PDF**: Los doctores pueden generar un PDF con la información detallada de un formulario médico.

### Generación de Reportes
- **Generar Informe del Doctor**: Los doctores pueden generar informes detallados sobre sus actividades, incluyendo citas, tratamientos y pacientes atendidos. Los informes pueden ser mensuales o anuales y se pueden exportar a PDF.

## Tecnologías Utilizadas
- **Flask**: Framework web utilizado para desarrollar la aplicación.
- **SQLAlchemy**: ORM utilizado para interactuar con la base de datos.
- **Jinja2**: Motor de plantillas utilizado para renderizar las vistas.
- **ReportLab**: Biblioteca utilizada para generar PDFs.
- **Bootstrap**: Framework CSS utilizado para el diseño y la interfaz de usuario.

## Instalación y Configuración
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/BDdentista.git
   cd BDdentista
   ```

2. Crea un entorno virtual y activa:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura la base de datos en `config.py`.

5. Realiza las migraciones de la base de datos:
   ```bash
   flask db upgrade
   ```

6. Ejecuta la aplicación:
   ```bash
   flask run
   ```

## Estructura del Proyecto

```plaintext
project/
├── app/
│   ├── __init__.py         # Configuración de la app Flask
│   ├── models.py           # Definición de las tablas (Doctor, Paciente, Cita, Tratamiento, FormularioMedico)
│   ├── controllers.py      # Controladores para el CRUD
│   ├── templates/          # Archivos HTML para la interfaz
│   │   ├── base.html       # Base para extender otras plantillas
│   │   ├── index.html      # Página principal
│   │   ├── autenticacion/  # Plantillas para autenticación (iniciar sesión, registrarse)
│   │   ├── doctor/         # Plantillas para gestión de doctores
│   │   ├── pacientes/      # Plantillas para gestión de pacientes
│   │   ├── citas/          # Plantillas para gestión de citas
│   │   ├── tratamientos/   # Plantillas para gestión de tratamientos
│   │   ├── formularios/    # Plantillas para gestión de formularios médicos
│   │   └── reportes/       # Plantillas para generación de reportes
│   ├── static/             # Archivos estáticos (CSS, JS)
│   │   ├── css/
│   │   │   └── styles.css  # Estilos personalizados
│   │   ├── js/
│   │   │   └── scripts.js  # Scripts personalizados
│   ├── utils/
│   │   └── decorator.py    # Decoradores personalizados (como manejo de permisos)
│   └── forms.py            # Formularios WTForms para validación
├── migrations/             # Directorio generado por Flask-Migrate
├── requirements.txt        # Lista de dependencias del proyecto
├── run.py                  # Punto de entrada principal para la app Flask
└── README.md               # Documentación del proyecto
```


## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que desees realizar.

## Licencia
Esta aplicación está licenciada bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.


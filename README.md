# BDdentista

![BDdentista][static/img/logogg.jpg]: static/img/logogg.jpg

**BDdentista** es una aplicación web diseñada para la gestión eficiente de clínicas dentales. Proporciona una plataforma centralizada para la administración de pacientes, citas, tratamientos y formularios médicos, optimizando el flujo de trabajo para los doctores.

---

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- Inicio de sesión seguro para doctores.
- Registro de nuevos usuarios con información profesional.
- Cierre de sesión y manejo de sesiones seguras.

### 🏥 Gestión de Doctores
- Creación y actualización del perfil profesional.
- Acceso a informes personalizados.

### 👩‍⚕️ Gestión de Pacientes
- Registro, edición y eliminación de pacientes.
- Búsqueda rápida de pacientes por cédula de identidad.
- Historial detallado con tratamientos y citas.

### 📆 Gestión de Citas
- Programación, edición y cancelación de citas.
- Visualización de citas programadas en un calendario.

### 💉 Gestión de Tratamientos
- Creación y actualización de tratamientos médicos.
- Registro de pagos y finalización de tratamientos.
- Generación de informes en PDF.

### 📋 Formularios Médicos
- Creación y almacenamiento de historiales médicos.
- Exportación de formularios a PDF.

### 📊 Generación de Reportes
- Informes detallados de actividades médicas.
- Exportación de datos en diferentes formatos.

---

## 🛠 Tecnologías Utilizadas

| Tecnología | Descripción |
|------------|-------------|
| Flask | Framework web para el backend |
| SQLAlchemy | ORM para la gestión de base de datos |
| Jinja2 | Motor de plantillas para las vistas |
| ReportLab | Generación de documentos PDF |
| Bootstrap | Diseño responsivo y UI moderna |

---

## 📌 Instalación y Configuración

### 🔧 Requisitos Previos
- Python 3.8+ instalado.
- PostgreSQL (o cualquier otro motor SQL compatible).
- Git instalado.

### 📥 Clonar el Proyecto
```bash
git clone https://github.com/tu_usuario/BDdentista.git
cd BDdentista
```

### 🏗 Configurar el Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 📦 Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 🗄 Configurar la Base de Datos
Edita `config.py` para establecer las credenciales correctas de la base de datos.


### 🚀 Ejecutar la Aplicación
```bash
py run.py
```
La aplicación estará disponible en `http://127.0.0.1:5000/`.

---

## 📂 Estructura del Proyecto
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
---

## 🤝 Contribuciones

Agradecemos a los siguientes contribuidores por su apoyo y colaboración en el desarrollo de este proyecto:

- <img src="https://github.com/cmrnda.png?size=60" alt="Carlos Miranda" style="border-radius: 50%;">[Carlos Miranda](https://github.com/cmrnda)
- <img src="https://github.com/rolandobryanmunozante.png?size=60" alt="Rolando Muñoz" style="border-radius: 50%;">[Rolando Muñoz](https://github.com/rolandobryanmunozante)
- <img src="https://github.com/dmiguel04.png?size=60" alt="David Machicado" style="border-radius: 50%;"> [David Machicado](https://github.com/dmiguel04)
- <img src="https://github.com/HAjiMe-0.png?size=60" alt="Harold Quispe" style="border-radius: 50%;">[Harold Quispe](https://github.com/HAjiMe-0)
---

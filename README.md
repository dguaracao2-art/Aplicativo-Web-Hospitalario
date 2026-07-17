Aplicativo Web para Registro y Gestión de Pacientes y Consultas Médicas

Integrantes


Robin Gabriel Leiton Cabrera
Anderson Alfredo Asencio Inga
Danny Ismael Guaraca Orozco
Bryan David Chimbo Pezo


Carrera y Semestre

Carrera: Ingeniería en Software
Semestre: Cuarto Semestre

Descripción del Proyecto

Aplicativo web para el registro y gestión de pacientes, médicos y citas médicas, desarrollado con metodología Scrum como proyecto MVP funcional. Permite administrar pacientes, agendar citas, generar facturas y llevar un control organizado de la información hospitalaria desde un panel centralizado.

Resumen de Actividades Realizadas


Se creó un repositorio público en GitHub para el desarrollo del proyecto.
Se configuró un entorno virtual de Python para administrar las dependencias.
Se instaló Django y se generó la estructura inicial del proyecto (arquitectura MVT).
Se configuró el archivo .env para gestionar las variables de entorno y la conexión a la base de datos.
Se estableció la conexión entre Django y MySQL para el almacenamiento de la información.
Se organizó el proyecto en distintas apps: core, security, catalog, customers, pacientes e invoicing.
Se instalaron las dependencias del proyecto y se generó el archivo requirements.txt.
Se ejecutaron las migraciones para crear las tablas de pacientes, médicos, citas y facturación en la base de datos.
Se implementó el sistema de autenticación y roles (administrador y médico) mediante mixins de permisos.
Se desarrolló el módulo de pacientes, con relación entre los modelos Cliente y Paciente.
Se construyó el dashboard con estadísticas, corrigiendo un problema de zona horaria en las consultas a MySQL.
Se implementó el módulo de facturación, con validaciones para evitar el registro de facturas duplicadas.
Se generaron reportes en PDF a partir de la información registrada.
Se verificó el funcionamiento de la aplicación ejecutando el servidor local con python manage.py runserver.
Se realizaron pruebas para validar la conexión con la base de datos y el correcto funcionamiento de cada módulo.
Finalmente, se registraron los cambios mediante commits y se publicaron en GitHub.


Tecnologías Utilizadas


Backend: Python, Django 6
Base de datos: MySQL
Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
Arquitectura: MVT (Model-View-Template)
Control de versiones: Git y GitHub
Herramientas: Visual Studio Code, StarUML
Captura de Ejecución
<img width="1882" height="970" alt="image" src="https://github.com/user-attachments/assets/a8222fe0-2375-4c8d-bbe5-69517fc0096b" />


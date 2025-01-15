# Proyecto Portafolio de titulo "Equivale"

## Descripción

El proyecto de nuestro portafolio es un software de e-commerce llamado **“Equivale”**, que busca ofrecer un servicio de compraventa online con despacho y encuestas de usuario, enfocado en la sustentabilidad. Este proyecto está construido utilizando **Django**, **Oracle Database**, **Python**, **HTML**, **CSS**, **JavaScript** y **Tailwind** como principales tecnologías. Además, se implementó el patrón **Modelo-Vista-Template (MVT)** propio de Django.

En este proyecto, pondremos en práctica las siguientes competencias del perfil de egreso:

- **Levantamiento y análisis de requerimientos**
- **Desarrollo de una aplicación web**
- **Aseguramiento de la calidad de software**

Utilizaremos una buena arquitectura para facilitar su desarrollo. Además, hemos trabajado colaborativamente mediante metodologías ágiles y herramientas como:

- Repositorios online de git (GitHub)
- Ofimática (Google Docs, Google Spreadsheet, Google Slides, Figma)

## Requisitos
- [Python](https://www.python.org/) (versión 3.8 o superior)
- [pip](https://pip.pypa.io/en_stable/) (incluido con Python)

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/AlexisVarela2811/Portafolio-De-Titulo.git
   cd Equivale
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de la Base de Datos
Asegúrate de configurar tu base de datos en el archivo de configuración correspondiente. Adapta el archivo de configuración para que incluya los detalles de tu base de datos.

## Claves API
Debes incluir las siguientes claves API en tu archivo de configuración:

### OAuth GitHub
```python
SOCIAL_AUTH_GITHUB_KEY = 'COLOCAR TU KEY AQUI'
SOCIAL_AUTH_GITHUB_SECRET = 'COLOCAR TU SECRET AQUI'
```

### OAuth Google
```python
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'COLOCAR TU KEY AQUI'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'COLOCAR TU SECRET AQUI'
```

### PayPal
```python
PAYPAL_CLIENT_ID = 'COLOCAR TU KEY AQUI'
PAYPAL_CLIENT_SECRET = 'COLOCAR TU SECRET AQUI'
PAYPAL_MODE = 'sandbox'
SITE_URL = 'COLOCAR TU URL AQUI POR DEFAULT ES http://127.0.0.1:8000'
```

## Migrar la Base de Datos
Después de configurar tu base de datos, ejecuta los siguientes comandos para migrar la base de datos:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Carga Inicial de Datos
Para cargar datos iniciales, sigue estos pasos:
1. Abre el shell de Django:
   ```bash
   python manage.py shell
   ```
2. Importa y ejecuta la función para cargar todos los datos:
   ```python
   from scripts.load_data import load_all
   load_all()
   ```

## Uso
Para iniciar el servidor de desarrollo, ejecuta:
```bash
python manage.py runserver
```

## Realizado por
- [Alexis Varela](https://github.com/AlexisVarela2811)
- [Francisco Cerda](https://github.com/frcerdas)

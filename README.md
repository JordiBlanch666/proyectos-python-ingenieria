# Python Project Suite: Biometría, Seguridad y Análisis de Datos

Este repositorio contiene una colección de herramientas desarrolladas en Python que demuestran la aplicación de algoritmos de visión artificial, seguridad criptográfica y gestión de datos multicanal.

## 🚀 Proyectos Incluidos

### 1. 👁️ Analizador Biométrico (`biometric.py`)
Un sistema de detección facial que utiliza **OpenCV** para identificar rostros en imágenes o tiempo real vía webcam.
- **Métricas calculadas:** Relación de aspecto, brillo medio de la región facial y proporción de área ocupada.
- **Modos:** Análisis de archivos estáticos y demo en vivo con anotaciones visuales.

### 2. 🔐 Generador de Contraseñas Seguras (`password_app.py`)
Herramienta robusta para la creación de credenciales utilizando el módulo `secrets` de Python, garantizando aleatoriedad de nivel criptográfico.
- **Características:** Soporta etiquetas personalizadas, guardado automático en archivos `.txt` y modo interactivo.

### 3. ✈️ Planificador de Viajes Inteligente (`Prueba.py`)
Un motor de cálculo de costos que integra datos de múltiples fuentes para proyectar presupuestos de viaje.
- **Fuentes de datos:** CSV, JSON y bases de datos SQLite.
- **Lógica:** Normalización de texto (eliminación de tildes/acentos) y cálculo de promedios estadísticos para vuelos y hospedajes.

---

## 🥗 La Nutrición en la Estructura de Datos

Mi formación en **Nutrición** ha sido fundamental para el diseño arquitectónico de estos proyectos. Al igual que en una evaluación nutricional se deben integrar múltiples indicadores (bioquímicos, antropométricos y dietéticos) para obtener un diagnóstico preciso, en estos desarrollos aplico un enfoque **holístico y cuantitativo**:

- **Análisis de Componentes:** En el proyecto de biometría, trato cada "métrica facial" como un macronutriente: datos aislados que solo cobran sentido cuando se analizan en conjunto para definir un perfil.
- **Equilibrio y Normalización:** En el planificador de viajes, la limpieza de datos (`normalizar_texto`) refleja la rigurosidad necesaria para estandarizar tablas de composición de alimentos, asegurando que fuentes heterogéneas (CSV, JSON, SQL) se integren sin "ruido".
- **Enfoque Basado en Evidencia:** La toma de decisiones en el software (como el cálculo de promedios de costos) emula el cálculo de requerimientos energéticos, donde la precisión de los datos de entrada determina la calidad del resultado final.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.12+
- **Visión Artificial:** `OpenCV` (haarcascades para detección frontal).
- **Procesamiento Numérico:** `NumPy` para análisis de brillo y matrices de imagen.
- **Bases de Datos:** `SQLite3` para almacenamiento persistente de hospedajes.
- **Seguridad:** Módulo `secrets` (aleatoriedad segura).
- **Formatos de Datos:** Manejo avanzado de `CSV` y `JSON`.

---

## 📦 Guía de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-de-tu-repositorio>
   cd PythonProject1
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows:
   .\.venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar las herramientas:**
   - **Biometría:** `python biometric.py --webcam`
   - **Contraseñas:** `python password_app.py --interactive`
   - **Viajes:** `python Prueba.py`

---

## 📄 Licencia
Este proyecto es de uso libre con fines educativos y de demostración técnica.

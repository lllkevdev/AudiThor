# Audithor

**Audithor** es una herramienta de auditoría estática desarrollada en Python para analizar proyectos y detectar ciertos patrones potencialmente peligrosos en el código fuente.

El proyecto está orientado a la práctica de análisis estático, manipulación de archivos, análisis sintáctico con AST y generación de informes para facilitar la revisión de código.

## Características

- **Escaneo de proyectos:** recorre directorios y selecciona archivos compatibles para su análisis.
- **Análisis estructural:** identifica clases, funciones, métodos e imports mediante el módulo `ast`.
- **Detección de patrones de riesgo:** busca usos de `eval()`, `exec()` y determinadas llamadas a `subprocess` con `shell=True`.
- **Protección de información sensible:** intenta ocultar secretos y credenciales reconocibles al incluir código fuente en el informe.
- **Manejo de errores:** contempla problemas de lectura, codificación y sintaxis.
- **Límites de tamaño:** evita procesar código fuente que supere el tamaño máximo configurado.
- **Informes:** presenta un resumen en consola y genera un informe JSON con los resultados y el código fuente redactado.

## Tecnologías

- Python 3.12
- `ast` para el análisis sintáctico
- `pathlib` para la gestión de rutas
- `dataclasses` para estructurar los resultados
- `json` para generar informes

## Estructura del proyecto

```text
audithor/
├── pyaudit/
│   ├── scanner.py
│   ├── analyzer.py
│   ├── security.py
│   ├── auditor.py
│   └── reporter.py
├── tests/
└── main.py
```

## Requisitos

- Python 3.12 o compatible.
- Git, si se desea clonar el repositorio.

## Instalación

Cloná el repositorio:

```bash
git clone https://github.com/TU_USUARIO/audithor.git
cd audithor
```

Creá un entorno virtual:

```bash
python -m venv .venv
```

Activá el entorno virtual.

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

## Uso

Ejecutá la herramienta indicando la ruta del proyecto que querés analizar:

```bash
python main.py "C:\ruta\al\proyecto"
```

Por ejemplo, en Windows:

```powershell
python main.py "C:\Users\kev\Documents\school-api"
```

Audithor mostrará un resumen en la consola y generará el archivo `pyaudit_report.json` en el directorio desde el que se ejecuta el programa.

## Ejemplo de salida

```text
=== REPORTE DE AUDITHOR ===
Proyecto: C:\ruta\al\proyecto
Archivos analizados: 61
Errores generales: 0
Hallazgos de seguridad: 0
```

*Los valores son ilustrativos y dependen del proyecto analizado.*

El informe JSON contiene información sobre los archivos procesados, su estructura, los errores encontrados y los hallazgos de seguridad detectados.

## Seguridad y limitaciones

Audithor utiliza **análisis estático**: examina el código fuente sin ejecutarlo.

Es importante tener en cuenta que:

- Los patrones detectados no representan una auditoría de seguridad exhaustiva.
- Puede haber falsos positivos y vulnerabilidades que no sean detectadas.
- La redacción automática de secretos se basa en patrones reconocibles y no garantiza eliminar todas las credenciales.
- El informe contiene código fuente del proyecto analizado, por lo que debe revisarse antes de compartirlo.
- Un resultado sin hallazgos no significa que el proyecto sea completamente seguro.

Se recomienda complementar los resultados con pruebas automatizadas, revisión manual y herramientas especializadas de seguridad.

## Pruebas

Si las dependencias de prueba están instaladas, ejecutá:

```bash
python -m pytest
```

## Objetivos de aprendizaje

Este proyecto permite practicar:

- Diseño modular en Python.
- Análisis de código mediante AST.
- Recorrido y filtrado de directorios.
- Manejo de excepciones.
- Expresiones regulares para redactar información sensible.
- Serialización de datos a JSON.
- Separación de responsabilidades.
- Pruebas automatizadas y control de versiones con Git.

## Estado del proyecto

**Versión inicial — 1.0**

Audithor es un proyecto educativo y de portfolio que puede ampliarse con nuevas reglas de análisis, formatos de informe y mejoras en la detección de riesgos.

## Autor

Desarrollado como proyecto personal de aprendizaje de Python y análisis estático de código.

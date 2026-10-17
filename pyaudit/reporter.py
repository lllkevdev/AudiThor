import json
import re

from pyaudit.analyzer import MAX_FILE_SIZE
from dataclasses import asdict
from pathlib import Path
from pyaudit.auditor import AuditResult


PATRONES_SECRETOS = [
    # Asignaciones como SECRET_KEY = "valor"
    re.compile(
        r"""(?im)^(\s*["']?[\w.-]*(?:secret|token|password|passwd|"""
        r"""api[_-]?key|private[_-]?key|access[_-]?key|"""
        r"""credential|client[_-]?secret|authorization)"""
        r"""[\w.-]*["']?\s*[:=]\s*)"""
        r"""(["'])(.*?)\2""",
    ),

    # Valores sensibles en diccionarios, como {"api_key": "valor"}
    re.compile(
        r"""(?i)(["'][^"']*(?:secret|token|password|passwd|"""
        r"""api[_-]?key|private[_-]?key|access[_-]?key|"""
        r"""credential|client[_-]?secret|authorization)"""
        r"""[^"']*["']\s*:\s*)"""
        r"""(["'])(.*?)\2""",
    ),
]


def redactar_secretos(codigo: str) -> str:
    for patron in PATRONES_SECRETOS:
        codigo = patron.sub(
            lambda coincidencia: (
                coincidencia.group(1)
                + coincidencia.group(2)
                + "<REDACTADO>"
                + coincidencia.group(2)
            ),
            codigo,
        )

    # Eliminar bloques de claves privadas PEM.
    codigo = re.sub(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
        r".*?"
        r"-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "[CLAVE PRIVADA REDACTADA]",
        codigo,
        flags=re.DOTALL,
    )

    return codigo


def leer_codigo_fuente(ruta: Path) -> str:
    try:
        if ruta.stat().st_size > MAX_FILE_SIZE:
            return "[Omitido: archivo supera el límite de tamaño]"

        codigo = ruta.read_text(encoding="utf-8")
        return redactar_secretos(codigo)

    except (OSError, UnicodeDecodeError):
        return "[Omitido: no se pudo leer el archivo]"


def report_console(resultado: AuditResult) -> None:
    print("=== REPORTE DE AUDITHOR ===")
    print(f"Proyecto: {resultado.ruta_proyecto}")
    print(
        f"Archivos analizados: "
        f"{len(resultado.archivos_analizados)}"
    )
    print(
        f"Errores generales: "
        f"{len(resultado.errores_generales)}"
    )
    total_hallazgos = sum(
        len(archivo.hallazgos_seguridad)
        for archivo in resultado.archivos_analizados
    )

    print(f"Hallazgos de seguridad: {total_hallazgos}")

    for archivo in resultado.archivos_analizados:
        for hallazgo in archivo.hallazgos_seguridad:
            print()
            print(f"[{hallazgo.regla}] {archivo.ruta}:{hallazgo.linea}")
            print(f"  {hallazgo.mensaje}")

    if resultado.errores_generales:
        print()
        print("Errores generales:")

        for error in resultado.errores_generales:
            print(f"- {error}")


def report_json(
    resultado: AuditResult,
    destino: Path,
) -> None:
    datos = {
        "proyecto": str(resultado.ruta_proyecto),
        "archivos_analizados": [],
        "errores_generales": resultado.errores_generales,
    }

    for archivo in resultado.archivos_analizados:
        datos["archivos_analizados"].append({
            "ruta": str(archivo.ruta),
            "codigo_fuente": leer_codigo_fuente(
                resultado.ruta_proyecto / archivo.ruta
            ),
            "clases": archivo.resultado.clases,
            "funciones": archivo.resultado.funciones,
            "metodos": archivo.resultado.metodos,
            "imports": archivo.resultado.imports,
            "error_sintaxis": archivo.resultado.error_sintaxis,
            "error_lectura": archivo.resultado.error_lectura,
            "hallazgos_seguridad": [
                {
                    "regla": hallazgo.regla,
                    "mensaje": hallazgo.mensaje,
                    "linea": hallazgo.linea,
                }
                for hallazgo in archivo.hallazgos_seguridad
            ],
        })

    destino.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

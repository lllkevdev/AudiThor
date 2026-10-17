from dataclasses import dataclass
from pathlib import Path

from pyaudit.scanner import scan_project
from pyaudit.analyzer import (
    MAX_FILE_SIZE,
    AnalysisResult,
    analyze_file,
)
from pyaudit.security import SecurityIssue, analyze_security


@dataclass
class FileAnalysis:
    ruta: Path
    resultado: AnalysisResult
    hallazgos_seguridad: list[SecurityIssue]


@dataclass
class AuditResult:
    ruta_proyecto: Path
    archivos_analizados: list[FileAnalysis]
    errores_generales: list[str]


def audit_project(root: Path) -> AuditResult:
    errores_generales = []
    archivos_analizados = []

    try:
        archivos = scan_project(root)
    except (FileNotFoundError, NotADirectoryError, OSError) as error:
        return AuditResult(
            ruta_proyecto=root,
            archivos_analizados=[],
            errores_generales=[str(error)],
        )


    for ruta_relativa in archivos:
        if ruta_relativa.suffix.lower() != ".py":
            continue

        ruta_completa = root / ruta_relativa

        try:
            if ruta_completa.stat().st_size > MAX_FILE_SIZE:
                resultado = analyze_file(ruta_completa)
                hallazgos_seguridad = []
            else:
                codigo = ruta_completa.read_text(
                    encoding="utf-8"
                )
                resultado = analyze_file(
                    ruta_completa,
                    codigo=codigo,
                )

                try:
                    hallazgos_seguridad = analyze_security(
                        codigo
                    )
                except SyntaxError:
                    hallazgos_seguridad = []

        except(OSError, UnicodeDecodeError) as error:
            resultado = AnalysisResult(
                clases=[],
                funciones=[],
                imports=[],
                metodos=[],
                error_lectura=str(error),
            )
            hallazgos_seguridad = []

        archivos_analizados.append(
            FileAnalysis(
                ruta=ruta_relativa,
                resultado=resultado,
                hallazgos_seguridad=hallazgos_seguridad,
            )
        )

    return AuditResult(
        ruta_proyecto=root,
        archivos_analizados=archivos_analizados,
        errores_generales=errores_generales,
    )       
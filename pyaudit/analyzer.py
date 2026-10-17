import ast
from pathlib import Path
from dataclasses import dataclass

MAX_FILE_SIZE = 1_000_000

@dataclass
class AnalysisResult:
    clases: list[str]
    funciones: list[str]
    imports: list[str]
    metodos: list[str]
    error_sintaxis: str | None = None
    error_lectura: str | None = None


def analyze_file(
        ruta: Path,
        codigo: str | None = None,
    ) -> AnalysisResult:
    try:
        if codigo is None:
            if ruta.stat().st_size > MAX_FILE_SIZE:
                return AnalysisResult(
                    clases=[],
                    funciones=[],
                    imports=[],
                    metodos=[],
                    error_lectura="Archivo demasiado grande",
                )

            codigo = ruta.read_text(encoding="utf-8")

    except (OSError, UnicodeDecodeError) as error:
        return AnalysisResult(
            clases=[],
            funciones=[],
            imports=[],
            metodos=[],
            error_lectura=str(error),
        )

    try:
        arbol = ast.parse(codigo)
    except SyntaxError as error:
        return AnalysisResult(
            clases=[],
            funciones=[],
            imports=[],
            metodos=[],
            error_sintaxis=str(error),
        )

    clases = []
    funciones = []
    imports = []
    metodos = []

    for nodo in arbol.body:
        if isinstance(nodo, ast.ClassDef):
            clases.append(nodo.name)

            for miembro in nodo.body:
                if isinstance(
                    miembro,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    metodos.append(f"{nodo.name}.{miembro.name}")

        elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funciones.append(nodo.name)

        elif isinstance(nodo, ast.Import):
            for alias in nodo.names:
                imports.append(alias.name)

        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module is not None:
                imports.append(nodo.module)

    return AnalysisResult(
        clases=sorted(set(clases)),
        funciones=sorted(set(funciones)),
        imports=sorted(set(imports)),
        metodos=sorted(set(metodos)),
    )
import ast
import subprocess
from dataclasses import dataclass


@dataclass
class SecurityIssue:
    regla: str
    mensaje: str
    linea: int


def analyze_security(codigo: str) -> list[SecurityIssue]:
    arbol = ast.parse(codigo)
    hallazgos = []
    alias_modulos = {}
    alias_funciones = {}

    # Identificar alias de subprocess.
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                if alias.name == "subprocess":
                    nombre = alias.asname or alias.name
                    alias_modulos[nombre] = "subprocess"

        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module == "subprocess":
                for alias in nodo.names:
                    if alias.name in {
                        "run",
                        "call",
                        "Popen",
                        "check_output",
                    }:
                        nombre = alias.asname or alias.name
                        alias_funciones[nombre] = alias.name

    # Analizar las llamadas.
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Call):
            continue

        if isinstance(nodo.func, ast.Name):
            if nodo.func.id == "eval":
                hallazgos.append(
                    SecurityIssue(
                        regla="PY001",
                        mensaje="Uso de eval()",
                        linea=nodo.lineno,
                    )
                )

            elif nodo.func.id == "exec":
                hallazgos.append(
                    SecurityIssue(
                        regla="PY002",
                        mensaje="Uso de exec()",
                        linea=nodo.lineno,
                    )
                )

        nombre_funcion = None

        if isinstance(nodo.func, ast.Attribute):
            if isinstance(nodo.func.value, ast.Name):
                modulo = alias_modulos.get(nodo.func.value.id)

                if (
                    modulo == "subprocess"
                    and nodo.func.attr in {
                        "run",
                        "call",
                        "Popen",
                        "check_output",
                    }
                ):
                    nombre_funcion = nodo.func.attr

        elif isinstance(nodo.func, ast.Name):
            nombre_funcion = alias_funciones.get(nodo.func.id)

        if nombre_funcion is None:
            continue

        usa_shell_true = any(
            argumento.arg == "shell"
            and isinstance(argumento.value, ast.Constant)
            and argumento.value.value is True
            for argumento in nodo.keywords
        )

        if usa_shell_true:
            hallazgos.append(
                SecurityIssue(
                    regla="PY003",
                    mensaje=(
                        f"Uso de subprocess.{nombre_funcion}() "
                        "con shell=True"
                    ),
                    linea=nodo.lineno,
                )
            )

    return hallazgos
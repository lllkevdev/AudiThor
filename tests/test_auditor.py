from pathlib import Path
from pyaudit.auditor import audit_project
from pyaudit.analyzer import analyze_file

def test_audita_archivo_python(tmp_path: Path) -> None:
    archivo = tmp_path / "main.py"
    archivo.write_text(
        "class Alumno:\n"
        "    def saludar(self):\n"
        "        pass\n"
        "\n"
        "def iniciar():\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = audit_project(tmp_path)

    assert resultado.ruta_proyecto == tmp_path
    assert resultado.errores_generales == []
    assert len(resultado.archivos_analizados) == 1

    analisis = resultado.archivos_analizados[0]

    assert analisis.ruta == Path("main.py")
    assert analisis.resultado.clases == ["Alumno"]
    assert analisis.resultado.funciones == ["iniciar"]
    assert analisis.resultado.metodos == ["Alumno.saludar"]


def test_ignora_archivos_que_no_son_python(tmp_path: Path) -> None:
    archivo_python = tmp_path / "main.py"
    archivo_texto = tmp_path / "README.md"

    archivo_python.write_text(
        "def iniciar():\n"
        "    pass\n",
        encoding="utf-8",
    )
    archivo_texto.write_text(
        "# Documentación del proyecto",
        encoding="utf-8",
    )

    resultado = audit_project(tmp_path)

    assert len(resultado.archivos_analizados) == 1
    assert resultado.archivos_analizados[0].ruta == Path("main.py")


def test_audita_archivo_con_error_de_sintaxis(tmp_path: Path) -> None:
    archivo = tmp_path / "main.py"
    archivo.write_text(
        "def funcion(:\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = audit_project(tmp_path)

    assert len(resultado.archivos_analizados) == 1

    analisis = resultado.archivos_analizados[0].resultado

    assert analisis.error_sintaxis is not None
    assert analisis.funciones == []


def test_audita_ruta_inexistente(tmp_path: Path) -> None:
    ruta_inexistente = tmp_path / "proyecto_que_no_existe"

    resultado = audit_project(ruta_inexistente)

    assert resultado.ruta_proyecto == ruta_inexistente
    assert resultado.archivos_analizados == []
    assert len(resultado.errores_generales) == 1
    assert "No existe la ruta" in resultado.errores_generales[0]


def test_no_modifica_archivos_auditados(tmp_path: Path) -> None:
    archivo = tmp_path / "main.py"
    contenido_original = (
        "def iniciar():\n"
        "    return 'hola'\n"
    )
    archivo.write_text(contenido_original, encoding="utf-8")

    audit_project(tmp_path)

    contenido_final = archivo.read_text(encoding="utf-8")

    assert contenido_final == contenido_original


def test_continua_si_un_archivo_no_se_puede_leer(tmp_path: Path) -> None:
    archivo_invalido = tmp_path / "invalido.py"
    archivo_valido = tmp_path / "valido.py"

    archivo_invalido.write_bytes(b"\xff\xfe\xfa")
    archivo_valido.write_text(
        "def iniciar():\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = audit_project(tmp_path)

    assert len(resultado.archivos_analizados) == 2

    analisis_invalido = next(
        archivo.resultado
        for archivo in resultado.archivos_analizados
        if archivo.ruta == Path("invalido.py")
    )
    analisis_valido = next(
        archivo.resultado
        for archivo in resultado.archivos_analizados
        if archivo.ruta == Path("valido.py")
    )

    assert analisis_invalido.error_lectura is not None
    assert analisis_valido.funciones == ["iniciar"]
    assert analisis_valido.error_lectura is None
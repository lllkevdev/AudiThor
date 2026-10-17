from pathlib import Path
from pyaudit.analyzer import analyze_file, MAX_FILE_SIZE


def test_detecta_clases_y_funciones(tmp_path: Path) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "class Alumno:\n"
        "    pass\n"
        "\n"
        "def saludar():\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.clases == ["Alumno"]
    assert resultado.funciones == ["saludar"]
    assert resultado.error_sintaxis is None


def test_detecta_importaciones(tmp_path: Path) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "import os\n"
        "import json\n"
        "from pathlib import Path\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.imports == ["json", "os", "pathlib"]
    assert resultado.error_sintaxis is None


def test_detecta_error_de_sintaxis(tmp_path: Path) -> None:
    archivo = tmp_path / "incorrecto.py"
    archivo.write_text(
        "def saludar(:\n"
        "    print('Hola')\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.error_sintaxis is not None
    assert resultado.clases == []
    assert resultado.funciones == []
    assert resultado.imports == []


def test_detecta_funciones_asincronas(tmp_path: Path) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "async def obtener_alumnos():\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.funciones == ["obtener_alumnos"]
    assert resultado.error_sintaxis is None


def test_no_confunde_metodos_con_funciones(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "class Alumno:\n"
        "    def saludar(self):\n"
        "        pass\n"
        "\n"
        "def iniciar():\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.clases == ["Alumno"]
    assert resultado.funciones == ["iniciar"]


def test_detecta_metodos_y_los_asocia_a_su_clase(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "class Alumno:\n"
        "    def saludar(self):\n"
        "        pass\n"
        "\n"
        "    async def cargar_datos(self):\n"
        "        pass\n"
        "\n"
        "class Materia:\n"
        "    def saludar(self):\n"
        "        pass\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.clases == ["Alumno", "Materia"]
    assert resultado.funciones == []
    assert resultado.metodos == [
        "Alumno.cargar_datos",
        "Alumno.saludar",
        "Materia.saludar",
    ]
    assert resultado.error_sintaxis is None


def test_no_confunde_funciones_anidadas(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "def iniciar():\n"
        "    def preparar():\n"
        "        pass\n"
        "    pass\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.funciones == ["iniciar"]
    assert resultado.metodos == []


def test_elimina_importaciones_duplicadas(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "ejemplo.py"
    archivo.write_text(
        "import os\n"
        "import json\n"
        "import os\n"
        "from os import path\n",
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.imports == ["json", "os"]


def test_detecta_error_de_lectura_por_codificacion(
    tmp_path: Path,
) -> None:
    archivo = tmp_path / "incorrecto.py"
    archivo.write_bytes(b"\xff\xfe\xfa")

    resultado = analyze_file(archivo)

    assert resultado.error_lectura is not None
    assert resultado.error_sintaxis is None
    assert resultado.clases == []
    assert resultado.funciones == []
    assert resultado.imports == []
    assert resultado.metodos == []


def test_detecta_archivo_inexistente(tmp_path: Path) -> None:
    archivo = tmp_path / "no_existe.py"

    resultado = analyze_file(archivo)

    assert resultado.error_lectura is not None
    assert resultado.error_sintaxis is None
    assert resultado.clases == []
    assert resultado.funciones == []
    assert resultado.imports == []
    assert resultado.metodos == []


def test_rechaza_archivo_demasiado_grande(tmp_path: Path) -> None:
    archivo = tmp_path / "grande.py"
    archivo.write_text(
        "x = 1\n" * 200_000,
        encoding="utf-8",
    )

    resultado = analyze_file(archivo)

    assert resultado.error_lectura is not None
    assert "archivo demasiado grande" in resultado.error_lectura.lower()


def test_acepta_archivo_del_tamano_maximo(tmp_path: Path) -> None:
    archivo = tmp_path / "limite.py"
    contenido = "x" * MAX_FILE_SIZE

    archivo.write_text(contenido, encoding="utf-8")

    assert archivo.stat().st_size == MAX_FILE_SIZE

    resultado = analyze_file(archivo)

    assert resultado.error_lectura is None
    assert resultado.error_sintaxis is None
import pytest
from pathlib import Path
from pyaudit.scanner import scan_project


def test_detecta_archivos_python(tmp_path: Path) -> None:
    archivo = tmp_path / "main.py"
    archivo.touch()

    archivos = scan_project(tmp_path)

    assert archivo.relative_to(tmp_path) in archivos


def test_directorio_temporal_vacio(tmp_path: Path) -> None:
    archivos = scan_project(tmp_path)

    assert archivos == []


def test_detecta_archivos_en_subcarpetas(tmp_path: Path) -> None:
    archivo_principal = tmp_path / "main.py"
    carpeta_app = tmp_path / "app"
    archivo_modelos = carpeta_app / "models.py"

    carpeta_app.mkdir()
    archivo_principal.touch()
    archivo_modelos.touch()

    archivos = scan_project(tmp_path)

    assert archivo_principal.relative_to(tmp_path) in archivos
    assert archivo_modelos.relative_to(tmp_path) in archivos


def test_excluir_env_venv(tmp_path: Path):
    archivo_principal = tmp_path / "main.py"
    archivo_env = tmp_path / ".env"

    carpeta_venv = tmp_path / ".venv"
    archivo = carpeta_venv / "interno.py"

    carpeta_venv.mkdir()
    archivo.touch()

    archivo_env.touch()
    archivo_principal.touch()

    archivos = scan_project(tmp_path) 

    assert archivo_principal.relative_to(tmp_path) in archivos
    assert archivo_env.relative_to(tmp_path) not in archivos
    assert archivo.relative_to(tmp_path) not in archivos


def test_ruta_inexistente(tmp_path: Path) -> None:
    ruta_inexistente = tmp_path / "no_existe"

    with pytest.raises(FileNotFoundError):
        scan_project(ruta_inexistente)


def test_ruta_es_archivo(tmp_path: Path) -> None:
    archivo = tmp_path / "documento.py"
    archivo.touch()

    with pytest.raises(NotADirectoryError):
        scan_project(archivo)


def test_excluir_git_y_pycache(tmp_path: Path) -> None:
    carpeta_git = tmp_path / ".git"
    carpeta_cache = tmp_path / "__pycache__"

    carpeta_git.mkdir()
    carpeta_cache.mkdir()

    archivo_git = carpeta_git / "config"
    archivo_cache = carpeta_cache / "modulo.pyc"

    archivo_git.touch()
    archivo_cache.touch()

    archivos = scan_project(tmp_path)

    assert archivo_git.relative_to(tmp_path) not in archivos
    assert archivo_cache.relative_to(tmp_path) not in archivos  


def test_archivos_ordenados(tmp_path: Path) -> None:
    (tmp_path / "z.py").touch()
    (tmp_path / "a.py").touch()
    (tmp_path / "m.py").touch()

    archivos = scan_project(tmp_path)

    assert archivos == [
        Path("a.py"),
        Path("m.py"),
        Path("z.py"),
    ]


def test_excluir_variantes_env(tmp_path: Path) -> None:
    nombres_env = [
        ".env",
        ".env.local",
        ".env.development",
        ".env.production",
        ".env.test",
        ".env.development.local",
        ".env.production.local",
        ".env.test.local",
    ]

    for nombre in nombres_env:
        (tmp_path / nombre).touch()

    (tmp_path / "main.py").touch()

    archivos = scan_project(tmp_path)

    assert Path("main.py") in archivos

    for nombre in nombres_env:
        assert Path(nombre) not in archivos


def test_incluye_solo_archivos_relevantes(tmp_path: Path) -> None:
    archivos = [
        "main.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "config.yaml",
        "settings.ini",
        "datos.json",
        "imagen.png",
        "documento.pdf",
        "programa.exe",
    ]

    for nombre in archivos:
        (tmp_path / nombre).write_text(
            "contenido de prueba",
            encoding="utf-8",
        )

    resultado = scan_project(tmp_path)

    esperados = {
        Path("main.py"),
        Path("pyproject.toml"),
        Path("requirements.txt"),
        Path("README.md"),
        Path("config.yaml"),
        Path("settings.ini"),
        Path("datos.json"),
    }

    assert set(resultado) == esperados


def test_incluye_archivos_especiales_sin_extension(
    tmp_path: Path,
) -> None:
    nombres = ["Dockerfile", "Makefile", "Procfile"]

    for nombre in nombres:
        (tmp_path / nombre).write_text(
            "contenido de prueba",
            encoding="utf-8",
        )

    resultado = scan_project(tmp_path)

    esperados = {Path(nombre) for nombre in nombres}

    assert set(resultado) == esperados


def test_excluye_env_con_mayusculas(tmp_path: Path) -> None:
    nombres = [
        ".ENV",
        ".Env.local",
        ".env.STAGING",
        ".eNv.custom",
    ]

    for nombre in nombres:
        (tmp_path / nombre).touch()

    (tmp_path / "main.py").touch()

    resultado = scan_project(tmp_path)

    assert resultado == [Path("main.py")]


def test_excluye_archivos_con_nombres_sensibles(
    tmp_path: Path,
) -> None:
    sensibles = [
        "secrets.json",
        "credentials.json",
        "secrets.yaml",
        "secrets.yml",
    ]

    for nombre in sensibles:
        (tmp_path / nombre).write_text(
            '{"API_KEY": "valor_de_prueba"}',
            encoding="utf-8",
        )

    (tmp_path / "config.json").write_text(
        '{"modo": "desarrollo"}',
        encoding="utf-8",
    )

    resultado = scan_project(tmp_path)

    assert resultado == [Path("config.json")]
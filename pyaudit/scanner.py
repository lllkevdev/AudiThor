from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "node_modules",
    "dist",
    "build",
}


ALLOWED_EXTENSIONS = {
    ".py",
    ".toml",
    ".txt",
    ".md",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".json",
}


ALLOWED_FILENAMES = {
    "Dockerfile",
    "Makefile",
    "Procfile",
}


SENSITIVE_FILENAMES = {
    "secrets.json",
    "credentials.json",
    "secrets.yaml",
    "secrets.yml",
}


SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


def is_env_file(nombre: str) -> bool:
    nombre = nombre.lower()
    return nombre == ".env" or nombre.startswith(".env.")


def scan_project(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"No existe la ruta: {root}")

    if not root.is_dir():
        raise NotADirectoryError(
            f"La ruta no es un directorio: {root}"
        )

    archivos: list[Path] = []

    for carpeta, directorios, nombres_archivos in root.walk(
        top_down=True
    ):
        directorios[:] = [
            nombre
            for nombre in directorios
            if nombre not in EXCLUDED_DIRS
        ]

        for nombre in nombres_archivos:
            if is_env_file(nombre):
                continue

            if nombre.lower() in SENSITIVE_FILENAMES:
                continue
            
            ruta = carpeta / nombre

            if (
                ruta.suffix.lower() not in ALLOWED_EXTENSIONS
                and nombre.lower() not in {
                    nombre_permitido.lower()
                    for nombre_permitido in ALLOWED_FILENAMES
                }
            ):
                continue

            if Path(nombre).suffix.lower() in SENSITIVE_EXTENSIONS:
                continue

            archivos.append(ruta.relative_to(root))

    return sorted(archivos)
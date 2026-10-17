import sys
from pathlib import Path

from pyaudit.auditor import audit_project
from pyaudit.reporter import report_console, report_json


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Uso: python main.py <ruta_del_proyecto>"
        )
        return

    proyecto = Path(sys.argv[1])

    resultado = audit_project(proyecto)
    report_console(resultado)
    
    destino = Path("pyaudit_report.json")
    report_json(resultado, destino)
    print(f"Informe JSON guardado en: {destino.resolve()}")


if __name__ == "__main__":
    main()

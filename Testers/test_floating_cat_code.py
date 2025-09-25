import importlib.util
import traceback
import sys
import os
from pathlib import Path

MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "floating_cat.py"))

errors = []
warnings = []

def check_imports():
    required = ["PyQt6", "pydub"]
    for mod in required:
        if importlib.util.find_spec(mod) is None:
            errors.append(f"Dependencia faltante: {mod}")

def check_run():
    try:
        import subprocess
        # Simular entorno sin zenity
        orig_check_output = subprocess.check_output
        subprocess.check_output = lambda *a, **kw: b"/tmp/fake.png"
        orig_run = subprocess.run
        subprocess.run = lambda *a, **kw: type('Fake', (), {'returncode': 1})()
        # Simular archivos válidos
        orig_exists = Path.exists
        Path.exists = lambda self: True
        # Ejecutar el script
        spec = importlib.util.spec_from_file_location("floating_cat", MODULE_PATH)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["floating_cat"] = mod
        spec.loader.exec_module(mod)
        # Restaurar mocks
        subprocess.check_output = orig_check_output
        subprocess.run = orig_run
        Path.exists = orig_exists
    except Exception as e:
        tb = traceback.format_exc()
        errors.append(f"Error de ejecución: {e}\n{tb}")

def main():
    print(f"Probando bugs de ejecución y dependencias en: {MODULE_PATH}\n")
    check_imports()
    check_run()
    print("\n--- RESULTADOS ---")
    if errors:
        print("\nERRORES:")
        for e in errors:
            print("-", e)
    else:
        print("Sin errores críticos.")
    if warnings:
        print("\nADVERTENCIAS:")
        for w in warnings:
            print("-", w)
    else:
        print("Sin advertencias.")
    print("\nPrueba finalizada.")

if __name__ == "__main__":
    main()

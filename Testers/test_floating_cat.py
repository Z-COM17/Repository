import os
import sys
from pathlib import Path
import re

ROUTES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rutas.conf"))

SECTIONS = ["imagen", "sonido", "audio_config"]

errors = []
warnings = []

def check_file_exists():
    if not Path(ROUTES_FILE).exists():
        errors.append(f"Archivo {ROUTES_FILE} no encontrado.")
        return False
    return True

def parse_config():
    secciones = {}
    current = None
    with open(ROUTES_FILE, "r", encoding="utf-8") as f:
        for i, linea in enumerate(f, 1):
            l = linea.strip()
            if not l or l.startswith("#"):
                continue
            m = re.match(r"\[(.+)\]", l)
            if m:
                current = m.group(1).lower()
                if current not in secciones:
                    secciones[current] = []
                continue
            if current:
                secciones[current].append((i, l))
    return secciones

def check_section_format(secciones):
    for sec in secciones:
        if sec not in SECTIONS:
            warnings.append(f"Sección desconocida: [{sec}]")
        if not secciones[sec]:
            warnings.append(f"Sección vacía: [{sec}]")

def check_imagenes(secciones):
    if "imagen" not in secciones:
        errors.append("No se encontró la sección [imagen].")
        return
    rutas = set()
    for i, ruta in secciones["imagen"]:
        r = ruta.strip('"')
        if not r:
            warnings.append(f"Línea {i}: Ruta de imagen vacía.")
        if r in rutas:
            warnings.append(f"Línea {i}: Imagen duplicada: {r}")
        rutas.add(r)
        if not Path(r).exists():
            errors.append(f"Línea {i}: Imagen no encontrada: {r}")

def check_sonidos(secciones):
    if "sonido" not in secciones:
        errors.append("No se encontró la sección [sonido].")
        return
    rutas = set()
    for i, ruta in secciones["sonido"]:
        r = ruta.strip('"')
        if not r:
            warnings.append(f"Línea {i}: Ruta de sonido vacía.")
        if r in rutas:
            warnings.append(f"Línea {i}: Sonido duplicado: {r}")
        rutas.add(r)
        if not Path(r).exists():
            errors.append(f"Línea {i}: Sonido no encontrado: {r}")

def check_audio_config(secciones):
    if "audio_config" not in secciones:
        warnings.append("No se encontró la sección [audio_config].")
        return
    config = {}
    last_ruta = None
    for i, linea in secciones["audio_config"]:
        if linea.startswith("ruta="):
            last_ruta = linea.split("=",1)[1].strip('"')
            config[last_ruta] = {}
        elif linea.startswith("start="):
            try:
                config[last_ruta]["start"] = float(linea.split("=",1)[1])
            except Exception:
                errors.append(f"Línea {i}: Valor inválido para start en {last_ruta}")
        elif linea.startswith("duration="):
            try:
                config[last_ruta]["duration"] = float(linea.split("=",1)[1])
            except Exception:
                errors.append(f"Línea {i}: Valor inválido para duration en {last_ruta}")
    for ruta, vals in config.items():
        if not Path(ruta).exists():
            errors.append(f"[audio_config] Ruta no encontrada: {ruta}")
        if "start" not in vals or "duration" not in vals:
            errors.append(f"[audio_config] Faltan valores para {ruta}")
        if "duration" in vals and vals["duration"] > 10:
            warnings.append(f"[audio_config] Duración inusualmente larga para {ruta}: {vals['duration']}s")

def main():
    print(f"Probando archivo de configuración: {ROUTES_FILE}\n")
    if not check_file_exists():
        print("ERROR: El archivo de configuración no existe.")
        sys.exit(1)
    secciones = parse_config()
    check_section_format(secciones)
    check_imagenes(secciones)
    check_sonidos(secciones)
    check_audio_config(secciones)
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

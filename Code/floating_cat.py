#!/usr/bin/env python3

from PyQt6 import QtWidgets, QtGui, QtCore
import sys
import random
import math
import subprocess
import os
from pathlib import Path
from pydub import AudioSegment
import tempfile
import threading

# Archivo de rutas
ROUTES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Routes", "rutas.conf"))

# Inicializamos listas de recursos

imagenes = []
sonidos = []

# Verificamos existencia del archivo
if not Path(ROUTES_FILE).exists():
    print(f"Archivo {ROUTES_FILE} no encontrado.")
    exit(1)

# Leer todas las rutas de imagen y sonido
seccion = None
with open(ROUTES_FILE, "r", encoding="utf-8") as f:
    for linea in f:
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if linea.lower() == "[imagen]":
            seccion = "imagen"
            continue
        elif linea.lower() == "[sonido]":
            seccion = "sonido"
            continue
        if seccion == "imagen":
            imagenes.append(linea.strip('"'))
        elif seccion == "sonido":
            sonidos.append(linea.strip('"'))

# Buscar la primera imagen válida
default_img = None
for ruta in imagenes:
    if Path(ruta).exists():
        default_img = ruta
        break

# Si ninguna imagen es válida, pedir al usuario una nueva
while default_img is None:
    # Usar zenity para pedir la ruta
    try:
        nueva_ruta = subprocess.check_output([
            "zenity", "--file-selection", "--title=Non valide image was found. Select a new one"
        ]).decode().strip()
    except Exception:
        print("No image was selected, closing...")
        exit(1)
    if Path(nueva_ruta).exists():
        default_img = nueva_ruta
        nueva_ruta_agregada = nueva_ruta.strip('"')
        # Insertar la ruta en la sección [imagen]
        with open(ROUTES_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        nueva_lineas = []
        imagen_insertado = False
        for i, linea in enumerate(lineas):
            nueva_lineas.append(linea)
            if linea.strip().lower() == "[imagen]":
                # Buscar el final de la sección de imágenes
                j = i + 1
                while j < len(lineas) and lineas[j].strip() and not lineas[j].strip().startswith("["):
                    nueva_lineas.append(lineas[j])
                    j += 1
                nueva_lineas.append(f'"{nueva_ruta}"\n')
                imagen_insertado = True
                nueva_lineas += lineas[j:]
                break
        if not imagen_insertado:
            nueva_lineas.append("[imagen]\n")
            nueva_lineas.append(f'"{nueva_ruta}"\n')
        with open(ROUTES_FILE, "w", encoding="utf-8") as f:
            f.writelines(nueva_lineas)
        print(f"Ruta añadida correctamente a la sección [imagen] en {ROUTES_FILE}")
        # Preguntar si se quieren eliminar rutas no válidas
        respuesta = subprocess.run([
            "zenity", "--question", "--text=Do you want to remove invalid image paths from the config?", "--title=Remove invalid paths?"
        ])
        if respuesta.returncode == 0:
            # Eliminar rutas no válidas de la sección [imagen]
            with open(ROUTES_FILE, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            nueva_lineas = []
            seccion = None
            nueva_ruta_presente = False
            for linea in lineas:
                if linea.strip().lower() == "[imagen]":
                    seccion = "imagen"
                    nueva_lineas.append(linea)
                    continue
                elif linea.strip().startswith("["):
                    seccion = None
                    nueva_lineas.append(linea)
                    continue
                if seccion == "imagen":
                    ruta = linea.strip('"').strip()
                    # Mantener la nueva ruta agregada aunque no exista aún
                    if ruta == nueva_ruta_agregada or ruta == default_img:
                        nueva_lineas.append(linea)
                        nueva_ruta_presente = True
                    elif ruta and Path(ruta).exists():
                        nueva_lineas.append(linea)
                else:
                    nueva_lineas.append(linea)
                    
            # Si la nueva ruta agregada no está presente, añadirla al final de la sección
            if not nueva_ruta_presente:
                idx = None
                for i, linea in enumerate(nueva_lineas):
                    if linea.strip().lower() == "[imagen]":
                        idx = i
                        break
                if idx is not None:
                    nueva_lineas.insert(idx + 1, f'"{nueva_ruta_agregada}"\n')
                else:
                    nueva_lineas.append("[imagen]\n")
                    nueva_lineas.append(f'"{nueva_ruta_agregada}"\n')

            with open(ROUTES_FILE, "w", encoding="utf-8") as f:
                f.writelines(nueva_lineas)
            print("Invalid image paths removed.")
    else:
        subprocess.run([
            "zenity", "--error", "--text=Invalid image, try again."
        ])

# Buscar la primera ruta de sonido válida
default_sound = None
for ruta in sonidos:
    if Path(ruta).exists():
        default_sound = ruta
        break

# Si ninguna ruta de sonido es válida, pedir al usuario una nueva
while default_sound is None:
    try:
        nueva_ruta = subprocess.check_output([
            "zenity", "--file-selection", "--title=No valid sound was found. Select a new one"
        ]).decode().strip()
    except Exception:
        print("No sound was selected, closing...")
        exit(1)
    if Path(nueva_ruta).exists():
        default_sound = nueva_ruta
        # Insertar la ruta en la sección [sonido]
        with open(ROUTES_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        nueva_lineas = []
        sonido_insertado = False
        for i, linea in enumerate(lineas):
            nueva_lineas.append(linea)
            if linea.strip().lower() == "[sonido]":
                # Buscar el final de la sección de sonidos
                j = i + 1
                while j < len(lineas) and lineas[j].strip() and not lineas[j].strip().startswith("["):
                    nueva_lineas.append(lineas[j])
                    j += 1
                nueva_lineas.append(f'"{nueva_ruta}"\n')
                sonido_insertado = True
                nueva_lineas += lineas[j:]
                break
        if not sonido_insertado:
            nueva_lineas.append("[sonido]\n")
            nueva_lineas.append(f'"{nueva_ruta}"\n')
        with open(ROUTES_FILE, "w", encoding="utf-8") as f:
            f.writelines(nueva_lineas)
        print(f"Ruta añadida correctamente a la sección [sonido] en {ROUTES_FILE}")
        # Preguntar si se quieren eliminar rutas no válidas
        respuesta = subprocess.run([
            "zenity", "--question", "--text=Do you want to remove invalid sound paths from the config?", "--title=Remove invalid paths?"
        ])
        if respuesta.returncode == 0:
            # Eliminar rutas no válidas de la sección [sonido]
            with open(ROUTES_FILE, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            nueva_lineas = []
            seccion = None
            for linea in lineas:
                if linea.strip().lower() == "[sonido]":
                    seccion = "sonido"
                    nueva_lineas.append(linea)
                    continue
                elif linea.strip().startswith("["):
                    seccion = None
                    nueva_lineas.append(linea)
                    continue
                if seccion == "sonido":
                    ruta = linea.strip('"').strip()
                    # Mantener la nueva ruta aunque no exista aún
                    if ruta == default_sound or ruta == nueva_ruta or (ruta and Path(ruta).exists()):
                        nueva_lineas.append(linea)
                else:
                    nueva_lineas.append(linea)
            with open(ROUTES_FILE, "w", encoding="utf-8") as f:
                f.writelines(nueva_lineas)
            print("Invalid sound paths removed.")
    else:
        subprocess.run([
            "zenity", "--error", "--text=Invalid sound, try again."
        ])

# Mostrar resultados
print(f"Default Image: {default_img}")
print(f"Default Sound: {default_sound}")

# Clase principal de la aplicación, incluye las funcionalidades del widget
class FloatingImage(QtWidgets.QWidget):
    def __init__(self, image_path, sound_path):
        super().__init__()
        self.setup_click_logic()  # Inicializa click_count, click_timer, pending_event
        self.sound = sound_path
        self.sound_segment = None  # Para almacenar el segmento si es necesario
        self.sound_segment_path = None
        self._check_and_prepare_sound_segment(sound_path)  # Inicialización del segmento de sonido
        # Inicialización de variables de movimiento y rotación
        size = 64
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.pixmap = QtGui.QPixmap(image_path).scaled(size, size, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        window_size = int(math.ceil(size * math.sqrt(2))) # tamaño para evitar recortes al rotar
        self.setFixedSize(window_size, window_size) # Bloqueo de la maximizacion de la ventana
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.BypassGraphicsProxyWidget # evita que se enfoque
        )
        # Posición inicial aleatoria
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.x = random.randint(0, screen.width() - self.width())
        self.y = random.randint(0, screen.height() - self.height())
        self.move(self.x, self.y)
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        # Angulo de rotación
        self.angle = 0
        self.rotation_speed = 0.8 # grados por frame
        # Velocidad en píxeles por movimiento
        self.dx = 1
        self.dy = 1
        # Timer para mover la imagen
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.move_diagonal)
        self.timer.start(16) # cada 16 ms (~60 fps)
        # --- NUEVO: contador de clics y temporizador ---
        self.click_count = 0
        self.first_click_time = None
    def setup_click_logic(self):
        self.click_count = 0
        self.click_timer = QtCore.QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._delayed_play)
        self.pending_event = None

    def _delayed_play(self):
        # Si no se llegó a 3 clics, reproducir audio
        if self.click_count < 3:
            self.play_system_notification()
        self.click_count = 0
        self.pending_event = None
    def _check_and_prepare_sound_segment(self, sound_path):
        """
        Si el audio dura más de 5s, prepara un segmento de 3s por defecto y permite seleccionar segmento/duración (máx 5s).
        """
        # Verificar si existen ajustes guardados en audio_config
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Routes", "rutas.conf"))
        start = None
        duration = None
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            in_section = False
            ruta_actual = None
            start_actual = None
            duration_actual = None
            for line in lines:
                if line.strip().lower() == "[audio_config]":
                    in_section = True
                    continue
                if in_section:
                    if line.startswith("ruta="):
                        if ruta_actual and start_actual is not None and duration_actual is not None:
                            if ruta_actual == sound_path:
                                start = start_actual
                                duration = duration_actual
                        ruta_actual = line.split("=",1)[1].strip().strip('"')
                        start_actual = None
                        duration_actual = None
                    elif line.startswith("start="):
                        start_actual = float(line.split("=",1)[1].strip())
                    elif line.startswith("duration="):
                        duration_actual = float(line.split("=",1)[1].strip())
                    elif line.startswith("["):
                        break
            # Verificar el último config leído
            if ruta_actual and start_actual is not None and duration_actual is not None:
                if ruta_actual == sound_path:
                    start = start_actual
                    duration = duration_actual
            # Si la ruta coincide y hay valores, usar esos
            if start is not None and duration is not None:
                audio = AudioSegment.from_file(sound_path)
                segment = audio[int(start*1000):int((start+duration)*1000)]
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                segment.export(tmp.name, format="wav")
                self.sound_segment = segment
                self.sound_segment_path = tmp.name
                return
        except Exception:
            pass
        # Si no hay config, preguntar y guardar
        try:
            audio = AudioSegment.from_file(sound_path)
            duration = len(audio) / 1000.0  # duración en segundos
            if duration > 5:
                # Por defecto, reproducir los primeros 3s
                start = 0
                end = 3
                # Preguntar al usuario si quiere elegir segmento y duración
                try:
                    # Pedir inicio
                    start_str = subprocess.check_output([
                        "zenity", "--entry", "--title=Selecciona el inicio (s)", "--text=The audio lasts {:.2f}s. Please select the audio start (0-{})".format(duration, int(duration)-1)
                    ]).decode().strip()
                    if start_str:
                        start = max(0, min(float(start_str), duration-1))
                    # Pedir duración
                    dur_str = subprocess.check_output([
                        "zenity", "--entry", "--title=Segment duration (s)", "--text=How many secinds do you want to reproduce? (1-6)"
                    ]).decode().strip()
                    if dur_str:
                        end = max(1, min(float(dur_str), 6))
                except Exception:
                    pass
                # Recortar el segmento
                segment = audio[int(start*1000):int((start+end)*1000)]
                # Guardar en archivo temporal
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                segment.export(tmp.name, format="wav")
                self.sound_segment = segment  # Guardar el segmento de sonido
                self.sound_segment_path = tmp.name  # Guardar la ruta del segmento de sonido
                self._save_audio_config(sound_path, start, end)  # Guardar configuración de audio
            else:
                self.sound_segment = None
                self.sound_segment_path = None
        except Exception as e:
            print(f"Error al procesar el audio: {e}")
            self.sound_segment = None
            self.sound_segment_path = None
    def _save_audio_config(self, ruta, start, duration):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Routes", "rutas.conf"))
        # Leer el archivo actual
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Buscar sección [audio_config]
        new_lines = []
        in_section = False
        section_found = False
        configs = {}
        current_ruta = None
        current_start = None
        current_duration = None
        for line in lines:
            if line.strip().lower() == "[audio_config]":
                in_section = True
                section_found = True
                new_lines.append(line)
                continue
            elif line.strip().startswith("["):
                if in_section and current_ruta:
                    configs[current_ruta] = (current_start, current_duration)
                in_section = False
            if in_section:
                if line.startswith("ruta="):
                    if current_ruta:
                        configs[current_ruta] = (current_start, current_duration)
                    current_ruta = line.split("=",1)[1].strip().strip('"')
                    current_start = None
                    current_duration = None
                elif line.startswith("start="):
                    current_start = float(line.split("=",1)[1].strip())
                elif line.startswith("duration="):
                    current_duration = float(line.split("=",1)[1].strip())
                elif line.startswith("["):
                    pass
                continue
            if not in_section:
                new_lines.append(line)
        # Guardar el último config leído
        if in_section and current_ruta:
            configs[current_ruta] = (current_start, current_duration)
        # Actualizar o añadir el nuevo config
        configs[ruta] = (start, duration)
        # Escribir la sección [audio_config] con todos los configs
        new_lines.append("[audio_config]\n")
        for r, (s, d) in configs.items():
            new_lines.append(f'ruta="{r}"\n')
            new_lines.append(f'start={s}\n')
            new_lines.append(f'duration={d}\n')
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    # ...existing code...
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        # Centrar la rotación
        cx = self.width() / 2
        cy = self.height() / 2

        # Aplicar transformación
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        painter.translate(-cx, -cy)

        # Dibujar la imagen centrada en la ventana redimensionada
        offset  = int((self.width() - self.pixmap.width()) / 2)
        painter.drawPixmap(offset, offset, self.pixmap)

    def move_diagonal(self):
        # Actualizar posición
        self.x += self.dx
        self.y += self.dy
        self.angle += self.rotation_speed

        # Rebote con los bordes
        if self.x <= 0 or self.x + self.width() >= self.screen_width:
            self.dx *= -1 # invertir dirección X
        if self.y <= 0 or self.y + self.height() >= self.screen_height:
            self.dy *= -1 # invertir dirección Y
        if self.angle >= 360:
            self.angle -= 360
        
        self.update()

        self.move(self.x, self.y)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            menu = QtWidgets.QMenu(self)
            # Audios (solo los de la sección [sonido], no los de audio config)
            audio_menu = menu.addMenu("Cambiar audio por defecto")
            for audio_path in sonidos:
                # Filtrar cualquier ruta que sea de audio config (por ejemplo, si hay duplicados o rutas temporales)
                if audio_path and Path(audio_path).exists():
                    action = QtGui.QAction(os.path.basename(audio_path), self)
                    action.triggered.connect(lambda checked, p=audio_path: self._set_default_audio(p))
                    audio_menu.addAction(action)
            # Imágenes
            image_menu = menu.addMenu("Cambiar imagen por defecto")
            for img_path in imagenes:
                action = QtGui.QAction(os.path.basename(img_path), self)
                action.triggered.connect(lambda checked, p=img_path: self._set_default_image(p))
                image_menu.addAction(action)
            menu.exec(event.globalPosition().toPoint())
            return
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return  # Ignorar cualquier botón que no sea el izquierdo
        x = event.position().x()
        y = event.position().y()
        offset_x  = int((self.width() - self.pixmap.width()) / 2)
        offset_y  = int((self.height() - self.pixmap.height()) / 2)
        if (offset_x <= x <= offset_x + self.pixmap.width() and
            offset_y <= y <= offset_y + self.pixmap.height()):
            self.click_count += 1
            if not self.click_timer.isActive():
                self.click_timer.start(500)
            if self.click_count == 3:
                self.click_timer.stop()
                self.click_count = 0
                # Abrir ventana de zenity para seleccionar imagen
                try:
                    new_img = subprocess.check_output([
                        "zenity", "--file-selection", "--title=Select new image"
                    ]).decode().strip()
                    if new_img:
                        self.pixmap = QtGui.QPixmap(new_img).scaled(
                            64, 64, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
                        self.update()
                        self._update_config_section("imagen", new_img)
                except Exception:
                    pass
                # Abrir ventana de zenity para seleccionar sonido y pedir segmento
                try:
                    new_sound = subprocess.check_output([
                        "zenity", "--file-selection", "--title=Select new sound"
                    ]).decode().strip()
                    if new_sound:
                        self.sound = new_sound
                        audio = AudioSegment.from_file(new_sound)
                        duration_audio = len(audio) / 1000.0
                        start = 0
                        end = 3
                        try:
                            start_str = subprocess.check_output([
                                "zenity", "--entry", "--title=Selecciona el inicio (s)", f"--text=El audio dura {duration_audio:.2f}s. ¿Desde qué segundo quieres empezar? (0-{int(duration_audio)-1})"
                            ]).decode().strip()
                            if start_str:
                                start = max(0, min(float(start_str), duration_audio-1))
                            dur_str = subprocess.check_output([
                                "zenity", "--entry", "--title=Duración del segmento (s)", "--text=¿Cuántos segundos quieres reproducir? (1-5)"
                            ]).decode().strip()
                            if dur_str:
                                end = max(1, min(float(dur_str), 5))
                        except Exception:
                            pass
                        segment = audio[int(start*1000):int((start+end)*1000)]
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                        segment.export(tmp.name, format="wav")
                        self.sound_segment = segment
                        self.sound_segment_path = tmp.name
                        self._save_audio_config(new_sound, start, end)
                        self._update_config_section("sonido", new_sound)
                except Exception:
                    pass

    def _set_default_audio(self, audio_path):
        self.sound = audio_path
        self._check_and_prepare_sound_segment(audio_path)
        self._update_config_section("sonido", audio_path)
        self._reload_resources()

    def _set_default_image(self, img_path):
        self.pixmap = QtGui.QPixmap(img_path).scaled(
            64, 64, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.update()
        self._update_config_section("imagen", img_path)
        self._reload_resources()

    def _reload_resources(self):
        # Recarga las listas de imagenes y sonidos desde rutas.conf
        global imagenes, sonidos
        imagenes = []
        sonidos = []
        seccion = None
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Routes", "rutas.conf"))
        with open(config_path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if linea.lower() == "[imagen]":
                    seccion = "imagen"
                    continue
                elif linea.lower() == "[sonido]":
                    seccion = "sonido"
                    continue
                if seccion == "imagen":
                    imagenes.append(linea.strip('"'))
                elif seccion == "sonido":
                    sonidos.append(linea.strip('"'))
    def _update_config_section(self, section, new_path):
        # Actualiza rutas.conf para que new_path sea la primera ruta de la sección y elimina duplicados
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Routes", "rutas.conf"))
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        in_section = False
        section_found = False
        seen = set()
        for line in lines:
            if line.strip().lower() == f"[{section}]":
                new_lines.append(line)
                in_section = True
                section_found = True
                # Insertar la nueva ruta como primera de la sección
                new_lines.append(f'"{new_path}"\n')
                seen.add(new_path)
                continue
            elif line.strip().startswith("["):
                in_section = False
            if in_section:
                ruta = line.strip('"').strip()
                # No duplicar ninguna ruta
                if ruta in seen or ruta == new_path:
                    continue
                seen.add(ruta)
            new_lines.append(line)
        if not section_found:
            new_lines.append(f"[{section}]\n")
            new_lines.append(f'"{new_path}"\n')
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def play_system_notification(self):
        # Evitar superposición de sonidos: no reproducir si ya hay uno en curso
        if getattr(self, '_sound_playing', False):
            return
        self._sound_playing = True
        def play():
            try:
                if self.sound_segment_path:
                    subprocess.run(["paplay", self.sound_segment_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run(["paplay", str(self.sound)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Error al reproducir el sonido: {e}")
            finally:
                self._sound_playing = False
        threading.Thread(target=play, daemon=True).start()

#ejecución de la aplicación
app = QtWidgets.QApplication(sys.argv)
window = FloatingImage(image_path=default_img, sound_path=default_sound)
window.show()
sys.exit(app.exec())
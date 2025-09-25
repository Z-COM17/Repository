INSTALACIÓN DE FLOATING CAT

1. Instala el paquete .deb:
   sudo dpkg -i floating-cat.deb

2. El instalador hará:
   - Instalar dependencias (python3, pip, PyQt6, pydub, nano)
   - Copiar los archivos a ~/floating_cat_app
   - Configurar autostart
   - Dar permisos de ejecución

3. IMPORTANTE:
   - No muevas los archivos después de instalar.

4. Si falta alguna dependencia, instálala manualmente:
   sudo apt install <paquete>

5. Para desinstalar:
   sudo dpkg -r floating-cat

Compatibilidad: Ubuntu, Debian y derivados.

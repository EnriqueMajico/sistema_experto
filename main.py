import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path de Python
# para que las importaciones de 'interfaz' y 'motor' funcionen siempre.
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
if RUTA_BASE not in sys.path:
    sys.path.insert(0, RUTA_BASE)

from interfaz import ejecutar_interfaz


def main():
    """Punto de entrada principal del Sistema Experto de Cotización 3D."""
    try:
        ejecutar_interfaz()
    except KeyboardInterrupt:
        print("\n\n[!] Ejecución interrumpida por el usuario. Saliendo del sistema...")
        sys.exit(0)


if __name__ == "__main__":
    main()
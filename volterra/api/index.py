"""Punto de entrada serverless para Vercel.

Re-exporta la aplicación FastAPI de VOLTERRA para que el runtime
de Vercel pueda invocarla como función serverless.
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path
# para que los imports de apps.* funcionen correctamente.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import app

# Vercel busca la variable `app` o `handler` para invocar.
handler = app
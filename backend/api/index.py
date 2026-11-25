import sys
from pathlib import Path

# Pastikan root folder backend/ selalu ada di sys.path saat dijalankan di Vercel Serverless
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402, F401

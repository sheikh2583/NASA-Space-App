"""Optional same-origin React hosting; API routes must be registered first."""
from pathlib import Path

from fastapi.staticfiles import StaticFiles


def mount_frontend(app, directory: str) -> None:
    path = Path(directory)
    if not (path / 'index.html').is_file():
        raise RuntimeError(f'Frontend build missing: {path / "index.html"}')
    # Last route: /health, /docs, /aoi/*, /export and /meta/* keep API behavior.
    # Missing files remain 404; never return index.html for unknown API requests.
    app.mount('/', StaticFiles(directory=path, html=True), name='frontend')

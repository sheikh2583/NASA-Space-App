"""Same-origin routing tests. No scientific fitting or runtime datasets needed."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ws2_platform.api.frontend import mount_frontend


def test_static_host_preserves_api_routes_and_missing_file_status(tmp_path):
    (tmp_path / 'index.html').write_text('<html>FireSense</html>')
    (tmp_path / 'assets').mkdir()
    (tmp_path / 'assets/app.js').write_text('console.log("asset")')
    app = FastAPI()
    @app.get('/health')
    def health():
        return {'status': 'ok'}
    @app.post('/aoi/summary')
    def summary():
        return {'series': []}
    mount_frontend(app, str(tmp_path))
    with TestClient(app) as client:
        assert 'FireSense' in client.get('/').text
        assert client.get('/assets/app.js').status_code == 200
        assert client.get('/health').json() == {'status': 'ok'}
        assert client.post('/aoi/summary').json() == {'series': []}
        assert client.get('/docs').status_code == 200
        assert client.get('/aoi/missing').status_code == 404
        assert client.get('/assets/missing.js').status_code == 404


def test_missing_frontend_fails_at_startup(tmp_path):
    with pytest.raises(RuntimeError, match='Frontend build missing'):
        mount_frontend(FastAPI(), str(tmp_path))

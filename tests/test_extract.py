import os

os.environ["INTERNAL_API_KEY"] = "test-key"
os.environ["GEMINI_API_KEY"] = "fake"

import pytest
from fastapi.testclient import TestClient

from app import extractor
from app.main import app
from app.schemas import GeminiReceipt

client = TestClient(app)
H = {"X-Internal-Key": "test-key"}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50
# Solo la firma inicial: SOI + marcador JFIF o EXIF
JFIF = b"\xff\xd8\xff\xe0" + b"0" * 50
EXIF = b"\xff\xd8\xff\xe1" + b"0" * 50


def fake(receipt: GeminiReceipt):
    async def _f(data, mime):
        return receipt
    return _f


def test_requires_key():
    r = client.post("/extract", files={"file": ("a.png", PNG, "image/png")})
    assert r.status_code == 401


def test_ok_normalizes(monkeypatch):
    monkeypatch.setattr(extractor, "_call_gemini", fake(GeminiReceipt(
        es_comprobante=True, monto=1250000, moneda="cop", fecha="2026-11-20",
        referencia=" #M123456 ", banco="Bancolombia", confianza=0.95)))
    r = client.post("/extract", headers=H, files={"file": ("a.png", PNG, "image/png")})
    assert r.status_code == 200
    body = r.json()
    assert body["monto"] == "1250000.0"
    assert body["moneda"] == "COP"
    assert body["referencia"] == "M123456"
    assert body["requiere_revision"] is False


@pytest.mark.parametrize("data", [JFIF, EXIF], ids=["jfif", "exif"])
@pytest.mark.parametrize("filename", ["a.jpg", "a.jpeg", "A.JPEG"])
def test_accepts_jpeg(monkeypatch, data, filename):
    received = []

    async def _f(content, mime):
        received.append((content, mime))
        return GeminiReceipt(es_comprobante=True, monto=50000, confianza=0.9)

    monkeypatch.setattr(extractor, "_call_gemini", _f)
    r = client.post("/extract", headers=H, files={"file": (filename, data, "image/jpeg")})
    assert r.status_code == 200
    assert received == [(data, "image/jpeg")]


def test_missing_fields_need_review(monkeypatch):
    monkeypatch.setattr(extractor, "_call_gemini", fake(GeminiReceipt(
        es_comprobante=True, monto=50000, fecha="no-es-fecha", confianza=0.9)))
    r = client.post("/extract", headers=H, files={"file": ("a.png", PNG, "image/png")})
    body = r.json()
    assert r.status_code == 200
    assert body["requiere_revision"] is True
    assert body["fecha"] is None
    assert any("No se pudo leer" in a for a in body["advertencias"])


def test_not_a_receipt(monkeypatch):
    monkeypatch.setattr(extractor, "_call_gemini", fake(GeminiReceipt(
        es_comprobante=False, confianza=0.9)))
    r = client.post("/extract", headers=H, files={"file": ("a.png", PNG, "image/png")})
    assert r.status_code == 422


def test_rejects_fake_extension():
    r = client.post("/extract", headers=H, files={"file": ("a.png", b"MZ not an image", "image/png")})
    assert r.status_code == 415


def test_timeout(monkeypatch):
    import asyncio

    async def slow(data, mime):
        await asyncio.sleep(1)

    monkeypatch.setattr(extractor, "_call_gemini", slow)
    monkeypatch.setattr(extractor, "GEMINI_TIMEOUT_S", 0.05)
    r = client.post("/extract", headers=H, files={"file": ("a.png", PNG, "image/png")})
    assert r.status_code == 504

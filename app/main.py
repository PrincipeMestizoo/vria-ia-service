import os
import secrets

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile

from .extractor import ExtractionError, extract_receipt
from .schemas import ExtractedReceipt

MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "8")) * 1024 * 1024

app = FastAPI(title="VRIA - Servicio de IA")


def verify_internal_key(x_internal_key: str = Header(default="")) -> None:
    """Solo Spring Boot conoce esta clave. Comparación en tiempo constante."""
    expected = os.getenv("INTERNAL_API_KEY", "")
    if not expected or not secrets.compare_digest(x_internal_key, expected):
        raise HTTPException(status_code=401, detail="No autorizado")


def detect_mime(data: bytes) -> str | None:
    """Detecta el tipo real por los primeros bytes; no confía en el Content-Type del cliente."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"%PDF"):
        return "application/pdf"
    return None


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractedReceipt, dependencies=[Depends(verify_internal_key)])
async def extract(file: UploadFile = File(...)) -> ExtractedReceipt:
    data = await file.read(MAX_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el tamaño permitido")

    mime = detect_mime(data)
    if mime is None:
        raise HTTPException(status_code=415, detail="Formato no soportado. Usa JPG, PNG, WEBP o PDF")

    try:
        return await extract_receipt(data, mime)
    except ExtractionError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

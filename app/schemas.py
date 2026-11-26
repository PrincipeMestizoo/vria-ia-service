from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class GeminiReceipt(BaseModel):
    """Esquema que Gemini debe devolver (salida estructurada)."""

    es_comprobante: bool = Field(
        description="true solo si la imagen o PDF es un comprobante de pago o transferencia."
    )
    monto: Optional[float] = Field(
        default=None,
        description="Valor transferido o pagado. Solo el número: sin símbolo de moneda ni "
        "separadores de miles. Decimales con punto.",
    )
    moneda: Optional[str] = Field(default=None, description="Código ISO 4217, por ejemplo COP.")
    fecha: Optional[str] = Field(
        default=None, description="Fecha de la transacción en formato YYYY-MM-DD."
    )
    referencia: Optional[str] = Field(
        default=None,
        description="Número de referencia, aprobación, comprobante o transacción.",
    )
    banco: Optional[str] = Field(
        default=None, description="Banco o billetera (Bancolombia, Nequi, Daviplata...)."
    )
    confianza: float = Field(
        description="Qué tan seguro estás de la lectura completa, de 0 a 1."
    )


class ExtractedReceipt(BaseModel):
    """Respuesta de la API: datos normalizados y validados, listos para Spring Boot."""

    monto: Optional[Decimal] = None
    moneda: Optional[str] = None
    fecha: Optional[date] = None
    referencia: Optional[str] = None
    banco: Optional[str] = None
    confianza: float = 0.0
    requiere_revision: bool = True
    advertencias: list[str] = []

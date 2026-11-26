from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class GeminiReceipt(BaseModel):
    """Esquema que Gemini debe devolver (salida estructurada).

    Ningún campo tiene valor por defecto: todos son obligatorios,
    aunque los Optional admiten null.
    """

    es_comprobante: bool = Field(
        description="true solo si la imagen o PDF es un comprobante de pago o transferencia."
    )
    monto: Optional[float] = Field(
        description="Valor transferido o pagado, no saldos ni comisiones. Solo el número: "
        "sin símbolo de moneda ni separadores de miles. Decimales con punto. "
        "null si no se puede leer."
    )
    moneda: Optional[str] = Field(
        description="Código ISO 4217. En un comprobante colombiano con '$' y sin otra "
        "moneda indicada es COP. null si no se puede determinar."
    )
    fecha: Optional[str] = Field(
        description="Fecha de la transacción en formato YYYY-MM-DD. "
        "null si no aparece completa o no se puede leer."
    )
    referencia: Optional[str] = Field(
        description="Número de referencia, aprobación, comprobante o transacción. "
        "null si no aparece."
    )
    banco: Optional[str] = Field(
        description="Entidad de ORIGEN, desde la que sale el dinero (Nequi, Bancolombia, "
        "Daviplata...). Se identifica por la app o entidad que generó el comprobante, "
        "no por el banco del destino. null si no se puede identificar."
    )
    cuenta_destino: Optional[str] = Field(
        description="Número de cuenta, celular o llave (@...) que recibe el dinero. No es "
        "el nombre del destinatario, la referencia ni la cuenta de origen. "
        "null si no aparece."
    )
    banco_destino: Optional[str] = Field(
        description="Entidad que recibe el dinero. En un comprobante de Nequi es la del "
        "campo 'Banco'. null si no aparece."
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
    destino: Optional[str] = None
    cuenta_destino: Optional[str] = None
    banco_destino: Optional[str] = None
    confianza: float = 0.0
    requiere_revision: bool = True
    advertencias: list[str] = Field(default_factory=list)
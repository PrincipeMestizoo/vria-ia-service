# VRIA - Servicio de IA

Este servicio lee comprobantes de pago por ti. Le envías la foto o el PDF de una transferencia y te devuelve los datos más importantes, ya organizados. Para leerlos usa Gemini, la inteligencia artificial de Google.

Funciona con comprobantes de Colombia, como los de Bancolombia, Nequi, Daviplata, Davivienda o BBVA.

## ¿Qué datos entrega?

- **Monto:** cuánto se pagó.
- **Moneda:** por ejemplo, COP.
- **Fecha:** cuándo se hizo el pago.
- **Referencia:** el número de aprobación o de comprobante.
- **Banco:** el banco o la billetera que se usó.

También indica qué tan segura está la IA de lo que leyó (un valor de 0 a 1).

## ¿Cuándo hay que revisar a mano?

El servicio marca un comprobante para revisión (`requiere_revision`) en estos casos:

- No pudo leer el monto, la fecha, la referencia o el banco.
- El monto leído no es válido.
- La fecha no se entiende o está en el futuro.
- La IA no está lo bastante segura de la lectura (menos de 0.8).

En las advertencias se explica qué problema encontró. Si el único motivo es la poca seguridad de la IA, no aparece ninguna advertencia.

> Este servicio solo lee el comprobante. **No confirma que el pago sea real** ni que el dinero haya llegado.

## ¿Qué archivos se pueden enviar?

- Imágenes **JPG o JPEG**, **PNG** y **WEBP**.
- Documentos **PDF**.

Cada archivo puede pesar hasta 8 MB (este límite se puede cambiar).

Cambiar el nombre de un archivo no cambia su formato. El servicio revisa el contenido para saber qué tipo de archivo es.

## Cómo ponerlo a funcionar

Necesitas tener Python instalado y una clave de Gemini. Los comandos son para Linux o WSL y se escriben en la terminal, dentro de la carpeta del proyecto.

**1. Prepara el proyecto.** Esto se hace una sola vez.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Si ya tienes la carpeta `.venv`, puedes saltarte el primer comando.

**2. Crea tu archivo de configuración.** Si ya tienes un archivo `.env`, no ejecutes este comando, porque lo reemplazaría.

```bash
cp .env.example .env
```

**3. Abre el archivo `.env` y completa estos datos.** Reemplaza los textos de ejemplo y no dejes las notas entre paréntesis.

| Dato | Para qué sirve |
|---|---|
| `GEMINI_API_KEY` | Tu clave de Gemini. |
| `GEMINI_MODEL` | El modelo de Gemini que quieres usar, por ejemplo `gemini-2.5-flash`. |
| `GEMINI_TIMEOUT_S` | Cuántos segundos esperar la respuesta de Gemini. |
| `INTERNAL_API_KEY` | Una contraseña que inventas tú. Debe ser larga y difícil de adivinar. |
| `MAX_UPLOAD_MB` | El peso máximo de cada archivo, en MB. |

**4. Enciende el servicio.**

```bash
.venv/bin/uvicorn app.main:app --env-file .env --reload
```

Para apagarlo, presiona `Ctrl + C`.

## Cómo probarlo

1. Con el servicio encendido, abre <http://127.0.0.1:8000/docs> en tu navegador.
2. Haz clic en **`/extract`** y luego en **Try it out**.
3. En `x-internal-key`, escribe la misma contraseña que pusiste en `INTERNAL_API_KEY`.
4. En `file`, elige tu comprobante.
5. Haz clic en **Execute** y mira la respuesta más abajo.

Este es un ejemplo de respuesta, con datos inventados:

```json
{
  "monto": "50000.0",
  "moneda": "COP",
  "fecha": "2026-11-20",
  "referencia": "M123456",
  "banco": "Nequi",
  "confianza": 0.95,
  "requiere_revision": false,
  "advertencias": []
}
```

Si solo quieres saber si el servicio está encendido, abre <http://127.0.0.1:8000/health>.

## Si algo sale mal

El servicio responde con un número que ayuda a saber qué pasó:

| Número | Qué significa | Qué puedes hacer |
|---|---|---|
| 400 | El archivo está vacío. | Elige otro archivo. |
| 401 | La contraseña falta o no es correcta. | Compárala con `INTERNAL_API_KEY`. |
| 413 | El archivo pesa demasiado. | Envía uno más liviano. |
| 415 | El formato no se acepta. | Usa JPG, JPEG, PNG, WEBP o PDF. |
| 422 | El archivo no parece un comprobante, o faltó adjuntarlo. | Lee el mensaje y revisa el archivo. |
| 500 | Algo falló en el servicio; por ejemplo, falta la clave de Gemini. | Revisa el archivo `.env` y los mensajes de la terminal. |
| 502 | Hubo un problema con la respuesta de Gemini. | Revisa tu clave y el modelo, o intenta más tarde. |
| 504 | Gemini tardó demasiado. | Intenta de nuevo. |

## Cuida los datos

- Los comprobantes tienen **datos personales**. Para leerlos, el archivo se envía a Google (Gemini).
- No compartas tu archivo `.env`, porque contiene tus claves.
- Si guardas comprobantes de prueba en la carpeta `comprobantes/`, Git no los incluirá en el proyecto.
- El servicio está pensado para que lo use el sistema principal de VRIA (hecho en Spring Boot). La contraseña interna solo deben conocerla quienes administran estos servicios.

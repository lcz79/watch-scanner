# Immagine ufficiale Playwright — ha già Chromium + tutte le dipendenze
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

# Tesseract OCR (per stories)
RUN apt-get update -qq && apt-get install -y -qq tesseract-ocr tesseract-ocr-ita && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Escludi venv e dati locali (gestiti dal volume)
RUN mkdir -p /app/data

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

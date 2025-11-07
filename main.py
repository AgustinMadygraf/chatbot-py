"""
Path: main.py
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def root():
    return "hola mundo, desde FastAPI en Railway"

# opcional: mismo texto en /hola-mundo
@app.get("/hola-mundo", response_class=PlainTextResponse)
def hola():
    return "hola mundo, desde FastAPI en Railway"

# healthcheck para probar despliegue
@app.get("/health")
def health():
    return {"status": "ok"}

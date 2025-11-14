# TODO: Migración a flujo no bloqueante (async) para FastAPI → AgentGateway

## Objetivo
Evitar que las llamadas a Rasa y Gemini bloqueen el event loop de FastAPI, mejorando la latencia y el throughput del sistema.

---

## Tareas principales

- [x] Migrar `AgentGateway.get_response` a método `async`, usando `httpx.AsyncClient` para llamadas a Rasa.
- [x] Migrar `RequestsHttpClient` a versión asíncrona (o eliminarlo si se usa directamente `httpx.AsyncClient`).
- [x] En el fallback Gemini, envolver la llamada bloqueante al SDK de Gemini con `asyncio.to_thread` para no bloquear el event loop.
- [x] Hacer `GenerateAgentResponseUseCase.execute` un método `async` y propagar `await` en todos los controladores y rutas.
- [ ] Eliminar o reducir el uso de `asyncio.sleep(3)` en el webhook de Telegram para evitar bloqueos artificiales.
- [ ] Actualizar los tests de gateways y use cases para soportar métodos asíncronos (`pytest.mark.asyncio` o `pytest.mark.anyio`).
- [ ] Revisar y actualizar los controladores (`TelegramMessageController`, `WebchatMessageController`) para que usen los nuevos métodos async.
- [ ] Documentar el nuevo flujo y las dependencias asíncronas.

---

## Notas técnicas

- El fallback Gemini seguirá siendo internamente síncrono, pero se ejecutará en un thread aparte usando `asyncio.to_thread`.
- Los tests actuales llaman a métodos síncronos; deben migrarse a async.
- Revisar todos los puntos de entrada FastAPI para asegurar que no haya cuellos de botella bloqueantes.
- Considerar la eliminación de `RequestsHttpClient` si toda la comunicación HTTP pasa a ser asíncrona.

---

## Archivos afectados

- `src/interface_adapter/gateways/agent_gateway.py`
- `src/infrastructure/requests/requests_http_client.py`
- `src/use_cases/generate_agent_response_use_case.py`
- `src/interface_adapter/controller/telegram_controller.py`
- `src/interface_adapter/controller/webchat_controller.py`
- `src/infrastructure/fastapi/fastapi_webhook.py`
- `tests/test_gateways.py`
- `tests/test_use_cases.py`

---

## Referencias

- [httpx.AsyncClient](https://www.python-httpx.org/async/)
- [asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/)
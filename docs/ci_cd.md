## Cobertura mínima obligatoria

El pipeline de CI/CD exige una cobertura mínima del 70% de líneas y 50% de ramas (branch coverage) para aprobar cualquier cambio. Si la cobertura baja de esos umbrales, el workflow fallará automáticamente.

Puedes ajustar los umbrales en `.coveragerc` con las opciones `fail_under` (líneas) y `fail_under_branch` (ramas).
## Dependencias de desarrollo

Para un entorno de desarrollo completo y aislado, utiliza los archivos `requirements-dev.in` y `requirements-dev.txt`:

1. Edita `requirements-dev.in` para agregar/quitar herramientas de desarrollo (pytest, flake8, black, pip-tools, etc.).
2. Genera/actualiza `requirements-dev.txt` ejecutando:
	```sh
	pip-compile requirements-dev.in
	```
3. Instala todas las dependencias de desarrollo con:
	```sh
	pip install -r requirements-dev.txt
	```
4. Esto instalará tanto las dependencias de producción como las de desarrollo.

Recuerda hacer commit de ambos archivos (`requirements-dev.in` y `requirements-dev.txt`) tras cualquier cambio relevante.
## Instalación y uso de pip-tools en desarrollo

Para asegurar la reproducibilidad y facilitar la gestión de dependencias, se recomienda instalar pip-tools en el entorno de desarrollo:

```sh
pip install pip-tools
```

Esto permitirá compilar y actualizar `requirements.txt` a partir de `requirements.in` siguiendo el flujo documentado más arriba.
# CI/CD y DevOps

## Proveedores
- CI/CD: GitHub Actions
- Despliegue: Railway
- Cobertura: Codecov

## Flujo de trabajo
1. Entrenamiento de modelos Rasa localmente.
2. Commit y push a GitHub.
3. GitHub Actions ejecuta linting, tests y cobertura.
4. Si pasa, despliega a Railway.
5. Railway sirve el modelo entrenado.


## Gestión de secretos y configuración
- Variables sensibles en GitHub Secrets.
- Las variables de entorno críticas y su validación se centralizan en `src/shared/config.py`.
- **Variables obligatorias:**
	- `TELEGRAM_API_KEY` (string): API key del bot de Telegram.
	- `GOOGLE_GEMINI_API_KEY` (string): API key de Gemini.
- **Variables opcionales:**
	- `RASA_REST_URL` (string): URL del endpoint REST de Rasa. Default: `http://localhost:5005/webhooks/rest/webhook`
	- `DISABLE_RASA` (bool): Deshabilita Rasa si es `true`. Default: `false`.
	- `LOG_MESSAGE_MAX_LENGTH` (int): Longitud máxima de mensajes en logs. Default: `160`.
- Si falta una variable obligatoria o su valor es inválido, el sistema lo reportará en el arranque y detendrá la ejecución.

## Gestión y auditoría de dependencias
- Dependabot crea PRs automáticos para actualizar dependencias (ver .github/dependabot.yml).
- Auditoría de seguridad automática con [Safety](https://pypi.org/project/safety/) en cada CI. **El pipeline fallará si se detectan vulnerabilidades en dependencias de producción o desarrollo.**
- Uso recomendado de [pip-tools](https://github.com/jazzband/pip-tools) para generar requirements.txt desde requirements.in.
- Revisar y aprobar PRs de dependencias solo si pasan los tests y auditoría.

### Uso de pip-tools para mantener requirements.txt

1. Instalar pip-tools localmente:
	```sh
	pip install pip-tools
	```
2. Editar `requirements.in` para agregar/quitar dependencias.
3. Generar/actualizar `requirements.txt` ejecutando:
	```sh
	pip-compile requirements.in
	```
4. (Opcional) Para actualizar todas las dependencias a la última versión compatible:
	```sh
	pip-compile --upgrade requirements.in
	```
5. Hacer commit de ambos archivos (`requirements.in` y `requirements.txt`).
6. Validar los cambios con CI antes de mergear a main.

## Buenas prácticas para PRs de dependencias

- Cuando Dependabot (o cualquier PR de actualización de dependencias) modifique archivos `.in`, es obligatorio compilar y commitear los archivos `.txt` correspondientes (`requirements.txt`, `requirements-dev.txt`).
- Si el PR de Dependabot no incluye los archivos compilados, realiza un commit adicional en la misma rama o solicita al autor que los agregue.
- El pipeline de CI fallará si los archivos `.txt` no están sincronizados con los `.in`.

## Rollback y monitoreo
- [Explicar lo que ofrece Railway y cómo se usa]

## Enlaces útiles
- [Workflow de GitHub Actions](../.github/workflows/)
- [Documentación Railway](https://docs.railway.app/)

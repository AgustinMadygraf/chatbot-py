## Compatibilidad y entorno Python

**Versión recomendada:** Python 3.10.x

- El proyecto requiere Python 3.10 para garantizar compatibilidad con Rasa 3.6.x y evitar errores de instalación en Railway y CI/CD.
- No es compatible con Python 3.12+.
- Railway y CI usan la versión especificada en `runtime.txt` (ejemplo: `python-3.10.14`).
- Si usas Windows, se recomienda usar WSL2 (Ubuntu) para gestionar dependencias y evitar problemas de paquetes exclusivos de Windows (ej: `pywin32`).

## Cobertura mínima obligatoria

El pipeline de CI/CD exige una cobertura mínima del 70% de líneas y 50% de ramas (branch coverage) para aprobar cualquier cambio. Si la cobertura baja de esos umbrales, el workflow fallará automáticamente.

Puedes ajustar los umbrales en `.coveragerc` con las opciones `fail_under` (líneas) y `fail_under_branch` (ramas).
## Flujo multiplataforma para dependencias

**Importante:** Para evitar errores de instalación en Railway y otros entornos Linux, **siempre genera `requirements.txt` y `requirements-dev.txt` en un entorno Linux** (idealmente WSL2 o una VM Ubuntu). Esto previene la inclusión de dependencias exclusivas de Windows.

### Pasos recomendados:
1. Usa WSL2/Ubuntu o una VM Linux para gestionar dependencias.
2. Instala [pyenv](https://github.com/pyenv/pyenv) para obtener la versión exacta de Python (ej: 3.10.14).
3. Crea y activa un entorno virtual limpio.
4. Instala `pip-tools` y compila los archivos `.txt` desde los `.in`.
5. Haz commit de los archivos generados.

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

1. Instala pip-tools en el entorno Linux:
	```sh
	pip install pip-tools
	```
2. Edita `requirements.in` para agregar/quitar dependencias.
3. **Asegúrate de incluir y fijar versiones de `pip` y `setuptools` en `requirements.in`** (ejemplo: `pip==24.0`, `setuptools==70.3.0`) para evitar advertencias y errores de hash en CI/CD.
4. Genera/actualiza `requirements.txt` ejecutando:
	```sh
	pip-compile requirements.in
	```
5. (Opcional) Para actualizar todas las dependencias a la última versión compatible:
	```sh
	pip-compile --upgrade requirements.in
	```
6. Haz commit de ambos archivos (`requirements.in` y `requirements.txt`).
7. Valida los cambios con CI antes de mergear a main.

#### Troubleshooting común

- **Error de hash mismatch en pip:**
	- Asegúrate de compilar los requirements en Linux y de que todas las dependencias estén fijadas correctamente.
	- Verifica que no haya dependencias exclusivas de Windows (ej: `pywin32`).
- **Error de incompatibilidad de versión de Python:**
	- Railway y CI requieren Python 3.10.x. Verifica `runtime.txt` y tu entorno local.
- **Advertencia de pip/setuptools no fijados:**
	- Añade `pip==24.0` y `setuptools==70.3.0` en `requirements.in`.

## Buenas prácticas para PRs de dependencias

- Cuando Dependabot (o cualquier PR de actualización de dependencias) modifique archivos `.in`, es obligatorio compilar y commitear los archivos `.txt` correspondientes (`requirements.txt`, `requirements-dev.txt`).
- Si el PR de Dependabot no incluye los archivos compilados, realiza un commit adicional en la misma rama o solicita al autor que los agregue.
- El pipeline de CI fallará si los archivos `.txt` no están sincronizados con los `.in`.

## Rollback y monitoreo

### Railway

- Railway permite hacer rollback a despliegues anteriores desde su dashboard web.
- Cada despliegue queda registrado y puede revertirse manualmente si se detecta un fallo en producción.
- Consulta la [documentación oficial de Railway](https://docs.railway.app/deploy/deployments#rollback) para detalles y mejores prácticas.

### Monitoreo

- Railway ofrece logs en tiempo real y métricas básicas desde el dashboard.
- Se recomienda monitorear errores críticos y fallos de arranque desde la interfaz de Railway y configurar alertas si es necesario.

## Enlaces útiles
- [Workflow de GitHub Actions](../.github/workflows/)
- [Documentación Railway](https://docs.railway.app/)
- [pyenv: gestión de versiones Python](https://github.com/pyenv/pyenv)
- [pip-tools: gestión de dependencias](https://github.com/jazzband/pip-tools)

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

## Gestión de secretos
- Variables sensibles en GitHub Secrets.

## Rollback y monitoreo
- [Explicar lo que ofrece Railway y cómo se usa]

## Enlaces útiles
- [Workflow de GitHub Actions](../.github/workflows/)
- [Documentación Railway](https://docs.railway.app/)

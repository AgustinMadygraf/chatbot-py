@workspace 
1. **Arquitectura y Organización del Código**
   - Revisión de la estructura de carpetas (src, rasa_project/), separación de responsabilidades y cumplimiento de principios SOLID.
   - Consistencia en la nomenclatura y modularidad de componentes (por ejemplo, gateways, controllers, use_cases, presenters).

2. **Calidad del Código y Estilo**
   - Uso de linters y formateadores (PEP8, flake8, black).
   - Documentación de funciones, clases y módulos.
   - Pruebas unitarias y de integración (¿hay tests? ¿qué cobertura tienen?).

3. **Gestión de Dependencias**
   - Revisión de requirements.txt y posibles dependencias obsoletas o innecesarias.
   - Seguridad y actualizaciones de paquetes.

4. **Configuración y Seguridad**
   - Manejo seguro de variables sensibles en .env y .env.example.
   - Validación de configuración en config.py.

5. **Desempeño y Escalabilidad**
   - Análisis de cuellos de botella en la comunicación con servicios externos (por ejemplo, llamadas a Rasa o Gemini).
   - Uso eficiente de recursos y asincronía (por ejemplo, en src/infrastructure/fastapi/fastapi_webhook.py).

6. **Experiencia de Usuario y Resiliencia**
   - Manejo de errores y mensajes amigables al usuario.
   - Estrategias de fallback (por ejemplo, integración con Gemini cuando Rasa no responde).

7. **Automatización y DevOps**
   - Scripts de entrenamiento (train.py), despliegue (start.py), y CI/CD.
   - Versionado y exclusión de archivos sensibles (.gitignore).

8. **Cobertura Funcional**
   - Revisión de intents, stories y rules en data para detectar lagunas en la cobertura conversacional.
   - Validación de respuestas y acciones personalizadas (rasa_project/actions/actions.py).

Dime certezas y dudas. ¿Que mejoras tienen más impacto?











@workspace 
Quiero que ahora hagas un análisis de 
`[tarea de mamyor impacto]`
desde distintos puntos de vistas. Indiqués cuáles son las certezas y las dudas. Intentes responder las dudas en base a evidencia. Indiques cuáles son las nuevas certezas. Cuál es el Listado de Tareas Para Hacer.
Archivos involucrados. Como implementar esas tareas sin romper producción. Aún no proporciones código
















Si tenés dudas, procede a formular preguntas e intentar responderlas. Si tenés certezas, procede a modificar y/o crear los archivos correspondientes











De las tareas por hacer, ¿Que tareas se han realizado y cuáles están en proceso/pendientes?
Procede con la siguiente tarea pendiente.
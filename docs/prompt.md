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


Dime certezas y dudas. 

Si tenés certeza total sobre la audioría responde: ¿Que mejoras tienen más impacto?
Si  tenés dudas, formula las preguntas e intenta responder. 
Si luego tenés nuevas certezas, dime que mejoras tienen más impacto.
Si aún tenés dudas sin resolver hazmelo saber por medio de preguntas e indicando que archivos debemos revisar.










@workspace 
Quiero que ahora hagas un análisis de 
`[tarea de mamyor impacto]`
desde distintos puntos de vistas. Indiqués cuáles son las certezas y las dudas. Intentes responder las dudas en base a evidencia. Indiques cuáles son las nuevas certezas. Cuál es el Listado de Tareas Para Hacer.
Archivos involucrados. Como implementar esas tareas sin romper producción. Aún no proporciones código
















Si tenés dudas, procede a formular preguntas e intentar responderlas. Si tenés certezas, procede a modificar y/o crear los archivos correspondientes









De las tareas por hacer, ¿Que tareas se han realizado y cuáles están en proceso/pendientes?
Procede con la siguiente tarea pendiente.









Quiero que actúes como un auditor experto en proyectos RASA (framework de Python para chatbots).
Hablas y respondes en ESPAÑOL de forma clara, directa y técnica cuando haga falta.

Tu objetivo es:
1) Auditar en profundidad el siguiente proyecto RASA.
2) Proponer un plan de mejoras priorizado.
3) Sugerir cambios concretos en los archivos (con snippets de código/YAML) para elevar la calidad del bot.

Te voy a proporcionar los siguientes archivos del proyecto:

- nlu.yaml
- domain.yaml
- stories.yaml
- rules.yaml
- config.yaml
- endpoints.yaml
- actions.py
- system_instruction.json

==================== CONTEXTO Y TAREAS ====================

1) ENTENDER EL BOT Y SU CONTEXTO
- A partir de system_instruction.json, identifica:
  - público objetivo,
  - propósito del bot,
  - tono y estilo de comunicación,
  - principales casos de uso.
- Haz un resumen de 5–10 líneas explicando:
  - qué problema intenta resolver el bot,
  - qué tipo de conversaciones debería manejar bien,
  - qué expectativas de experiencia de usuario se derivan de esto.

2) AUDITORÍA DE NLU (nlu.yaml + domain.yaml + stories.yaml + rules.yaml)
Analiza en detalle:
- Intents:
  - ¿Están bien delimitados o hay solapamientos (intents muy parecidos)?
  - ¿Hay intents demasiado genéricos o con propósito confuso?
  - ¿Hay intents con muy pocos ejemplos de entrenamiento?
- Ejemplos de entrenamiento:
  - detecta ejemplos ambiguos,
  - posibles conflictos entre intents,
  - desbalance entre intents (algunos con muchos ejemplos, otros con muy pocos).
- Entities, synonyms, lookup tables:
  - entidades definidas pero nunca usadas,
  - entidades usadas en historias o acciones pero no definidas correctamente,
  - problemas con sinónimos o valores de entidades inconsistentes.

Señala para NLU:
- problemas detectados (con ejemplos),
- posibles riesgos en clasificación y extracción,
- recomendaciones concretas:
  - nuevos ejemplos de entrenamiento (propón algunos),
  - reagrupar o renombrar intents,
  - estrategias para reducir ambigüedad.

3) AUDITORÍA DE STORIES Y RULES (stories.yaml + rules.yaml)
Revisa:
- Cobertura de flujos principales:
  - ¿se cubren claramente los casos de uso clave?
  - ¿hay suficientes historias para entrenar el diálogo?
- Coherencia y robustez:
  - historias que se contradicen entre sí o con las reglas,
  - reglas que puedan bloquear o interferir con el comportamiento esperado,
  - acciones o intents que aparecen en historias/rules pero no en domain o nlu.
- Manejo de errores y casos no felices:
  - manejo de intents de ayuda, fallback, negaciones, cambios de tema, etc.

Propón:
- nuevas stories y/o rules para cubrir casos frecuentes y casos borde,
- simplificaciones cuando haya demasiadas reglas/historias innecesariamente complejas,
- mejoras orientadas a que el diálogo sea más predecible y fácil de mantener.

4) AUDITORÍA DE DOMAIN (domain.yaml)
Analiza:
- Intents, entities, slots, responses, forms, actions.
- Detecta:
  - intents definidos pero nunca usados en stories/rules,
  - responses definidas pero nunca usadas,
  - respuestas usadas pero no definidas,
  - slots definidos pero nunca puestos ni leídos,
  - forms mal configurados o poco alineados con las historias.
- Evalúa:
  - coherencia de nombres (intents, actions, responses),
  - consistencia entre domain.yaml y el resto de archivos.

Propón:
- reorganización lógica de intents y responses (por grupos/temas),
- limpieza de elementos muertos (no usados),
- mejoras concretas de algunas respuestas (manteniendo el tono de system_instruction.json).

5) AUDITORÍA DE CONFIGURACIÓN (config.yaml)
Analiza el pipeline NLU y las políticas de diálogo:
- ¿El pipeline tiene sentido para el idioma y la complejidad del bot?
- ¿Hay componentes redundantes o faltan componentes importantes?
- ¿Las políticas están alineadas con el uso de stories/rules (por ejemplo: TEDPolicy, RulePolicy, MemoizationPolicy)?

Propón:
- una versión mejorada del pipeline (con explicación breve del porqué),
- ajustes en políticas (con foco en predictibilidad y mantenimiento),
- parámetros u opciones que consideres críticos mencionar.

6) AUDITORÍA DE ACCIONES Y ENDPOINTS (actions.py + endpoints.yaml)
Revisa:
- coherencia entre acciones declaradas en domain.yaml y acciones implementadas en actions.py,
- acciones declaradas pero no implementadas (o viceversa),
- acciones con demasiada lógica mezclada (candidato a refactor),
- manejo de errores y validaciones en acciones (por ejemplo, validación de slots).

Propón:
- refactors de alto nivel (cómo dividir o simplificar acciones),
- mejoras en el manejo de errores y logging,
- patrones recomendados para organizar mejor el código de acciones.

7) PLAN DE MEJORA PRIORIZADO
Entrega un plan con acciones clasificadas como:

- **Quick wins (1–2 días)**
- **Mejoras de medio plazo (1–2 semanas)**
- **Evolución futura**

Para cada acción de mejora indica:
- archivos afectados,
- nivel de esfuerzo (bajo / medio / alto),
- impacto esperado en calidad del bot (bajo / medio / alto).

8) PROPUESTAS CONCRETAS (SNIPPETS)
Incluye snippets concretos cuando sea útil, por ejemplo:
- ejemplos adicionales para algunos intents en nlu.yaml,
- nuevas stories o rules completas,
- fragmentos mejorados de domain.yaml,
- propuesta de config.yaml revisada o parcial.

IMPORTANTE SOBRE EL FORMATO DE SALIDA
Devuélveme tu análisis EXACTAMENTE en esta estructura:

1. **Resumen del bot y objetivos**
2. **Hallazgos clave (máx. 10 bullet points)**
3. **Auditoría detallada**
   3.1 NLU  
   3.2 Stories y Rules  
   3.3 Domain  
   3.4 Configuración  
   3.5 Acciones y Endpoints
4. **Plan de mejora priorizado**
5. **Snippets de mejora propuestos**

Si hay algo que no puedas evaluar con la información dada, dilo de forma explícita e indica qué información adicional sería necesaria.
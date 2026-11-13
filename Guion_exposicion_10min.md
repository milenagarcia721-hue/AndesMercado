# Guion de exposición (10 minutos) — AndesMercado

## Diapositiva 1 — Apertura (30 s)
Buenos días. Somos el equipo consultor de AndesMercado. Presentamos una propuesta para que un error de datos como el ocurrido en Black Friday no vuelva a llegar a los tableros ni afecte decisiones de inventario. La idea central es que la calidad del dato sea una condición obligatoria antes de publicar.

## Diapositiva 2 — El problema (1 min)
AndesMercado tiene 45 tiendas y un canal digital que ya representa el 35 % de los ingresos. El caso muestra que e-commerce cambió el campo monto de pesos con decimales a centavos enteros, sin avisar al equipo de datos. El pipeline nocturno no tuvo un error de ejecución, por eso cargó los valores. El tablero mostró un crecimiento de 9.800 % y se aprobó una compra urgente de COP 850 millones. El incidente demuestra que validar solo si el código ejecuta no es suficiente: también hay que validar el significado y la distribución de los datos.

## Diapositiva 3 — CALMS (1 min)
En CALMS encontramos madurez muy baja. Cultura está en uno porque los equipos operan en silos; Automatización está en uno porque se copia por SFTP y se modifica cron manualmente; Lean está en dos porque no hay un flujo seguro y la recuperación genera reproceso; Medición está en uno porque el error se detecta por quejas entre dos y cinco días después; Compartir está en uno porque los scripts están en la carpeta personal de Andrés. La prioridad es automatizar y medir, pero esto requiere colaboración entre las áreas.

## Diapositiva 4 — Causa raíz (1 min)
Aplicando los cinco porqués: la gerencia compró con datos erróneos porque el tablero mostró ventas infladas; esto ocurrió porque el pipeline interpretó centavos como pesos; no se detectó porque faltaban reglas de unidad, monto y volumen; esas reglas no existían porque no había contrato ni proceso compartido; y la causa de fondo fue una operación manual sin gobierno de cambios, con conocimiento concentrado. No buscamos culpables: el sistema de trabajo permitió que el error avanzara.

## Diapositiva 5 — Arquitectura (1 min 15 s)
Proponemos que todo cambio comience en GitHub mediante una rama y un Pull Request. GitHub Actions ejecuta pruebas y validaciones. El cambio pasa a desarrollo y luego a QA, donde se prueban integración, esquema y resultados. Dos revisores, uno de datos y uno del área productora cuando el contrato cambia, aprueban antes de producción. Airflow orquesta las cargas y la observabilidad monitorea logs, volumen, distribución, frescura, esquema y linaje. Terraform define la infraestructura para que no dependa de configuraciones manuales.

## Diapositiva 6 — Contrato de datos (1 min)
El contrato define cuatro campos. El identificador debe ser único y obligatorio; fecha usa formato ISO; canal solo acepta tienda o en línea; y monto es decimal en pesos colombianos, nunca centavos enteros. Los cambios se notifican con anticipación, se versionan y se revisan por PR. Un cambio incompatible necesita una nueva versión y una migración controlada. Así el productor y el consumidor comparten la misma interpretación.

## Diapositiva 7 — Implementación (1 min)
La implementación Python revisa columnas, identificadores, canales, montos y totales diarios. Si el archivo no cumple, el programa devuelve código uno. GitHub Actions ejecuta pytest y después valida el CSV. Esto hace que un dato defectuoso bloquee el flujo antes de la carga al warehouse. Las pruebas cubren datos correctos y un caso inválido para cada regla.

## Diapositiva 8 — Evidencia (1 min)
En el archivo original, tres ventas en línea del 28 de noviembre llegan con valores de 18 millones 990 mil, 45 millones 990 mil y 8 millones 990 mil 50 pesos. Cada una supera el máximo de cinco millones. El total diario del canal también supera tres veces el promedio previo. Para la demostración, se normalizan esos tres valores dividiéndolos por cien, porque el contrato exige pesos. El total queda en 739 mil 700 pesos con 50 centavos. El canal tienda no se toca. El repositorio permite ejecutar ambas situaciones y el workflow manual permite seleccionar el anexo para ver el fallo.

## Diapositiva 9 — Métricas y adopción (1 min)
Proponemos pasar de un despliegue mensual a uno o dos por semana; reducir el tiempo de entrega de tres semanas a tres días; bajar la tasa de fallos del 40 al 10 por ciento; y recuperar el servicio en cuatro horas o menos. En 90 días se construye primero el control básico, luego CI y QA, y finalmente el despliegue controlado y monitoreo.

## Diapositiva 10 — Cierre (30 s)
Solicitamos aprobar el plan de 90 días, asignar responsables de e-commerce y datos y exigir revisión por pares. La solución no es solamente corregir un CSV; es cambiar el proceso para que ningún dato sin validar llegue a una decisión comercial. Muchas gracias.

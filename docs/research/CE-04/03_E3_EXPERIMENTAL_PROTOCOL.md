HLS — CE-04 / E3
PROTOCOLO EXPERIMENTAL: HETEROGENEIDAD Y COMPLEMENTARIEDAD
Fecha: 26/10/2026
Estado: PROPUESTO — SIN EJECUCIÓN

1. OBJETIVO

Determinar cómo afectan la composición de capacidades,
la política de asignación y el tamaño organizativo al
porcentaje de tareas completadas correctamente dentro
del plazo.

No se presupone ventaja de heterogeneidad ni de una
política organizativa más compleja.

No hay aprendizaje individual ni transferencia.

2. ESCENARIO

Organizaciones de N = 12, 24 y 48 agentes.

Cuatro familias de capacidades: F1, F2, F3 y F4.
Cuatro tipos de tareas: T1, T2, T3 y T4.

Cada agente:
- Procesa una tarea simultáneamente.
- Dispone de una unidad de capacidad operativa.
- Tiene una familia primaria de competencia.
- Mantiene capacidades constantes durante la campaña.

Competencia:

Probabilidad de resolución correcta:
- Familia coincidente con tarea: 0,90.
- Familia no coincidente: 0,65.

Tiempo de servicio:
- Coincidencia: media 1,0.
- No coincidencia: media 1,5.

Distribución lognormal con CV = 0,30.
Muestreo independiente condicionado al par agente-tarea.

Estos parámetros son supuestos experimentales,
no propiedades generales de agentes heterogéneos.

3. COMPOSICIONES

H0: composición homogénea.
    100 % de agentes F1.

H1: heterogeneidad moderada.
    50 % F1; el 50 % restante distribuido entre
    F2, F3 y F4 mediante redondeo determinista.

H2: heterogeneidad equilibrada.
    25 % de cada familia.

Para N=12/24/48:

H0: (12,0,0,0) / (24,0,0,0) / (48,0,0,0)
H1: (6,2,2,2) / (12,4,4,4) / (24,8,8,8)
H2: (3,3,3,3) / (6,6,6,6) / (12,12,12,12)

CONTROL CRÍTICO:

El diseño anterior iguala número de agentes y
presupuesto operativo nominal, pero NO iguala
competencia agregada por tipo de tarea.

Por tanto, una diferencia H0-H2 puede reflejar
tanto diversidad como adecuación de competencias.

Para aislar el efecto de composición, añadir
un análisis de control con competencia agregada
igualada por tipo de tarea.

No afirmar que H0-H2 están igualadas en competencia
si únicamente se iguala su promedio global.

4. DEMANDA

Horizonte: 400 unidades temporales.

Llegadas Poisson, con intensidad proporcional a N.

Tres fases:

Fase A: t = 0–150
Distribución T1/T2/T3/T4 = 40/20/20/20 %

Fase B: t = 150–300
Distribución = 10/40/40/10 %

Fase C: t = 300–400
Distribución = 25/25/25/25 %

Intensidad nominal: 0,55 llegadas por agente
y unidad temporal.

Cada tarea tiene plazo:
llegada + 3 unidades temporales.

El plazo incluye espera y servicio.

Los cambios de demanda son exógenos y conocidos
únicamente cuando ocurren.

5. RECURSOS Y ESCALA

DISEÑO PRINCIPAL: RECURSOS PROPORCIONALES.

N agentes implican N unidades de capacidad.

La intensidad de llegada también escala con N.

Esto permite estudiar efectos de tamaño
organizativo manteniendo aproximadamente
constante la carga nominal por agente.

No interpretar un aumento del rendimiento total
debido simplemente a disponer de más agentes
como ventaja organizativa.

El presupuesto fijo NO forma parte de esta campaña.

6. POLÍTICAS ORGANIZATIVAS

P0: ASIGNACIÓN ALEATORIA FACTIBLE
Seleccionar uniformemente entre agentes disponibles.
No utilizar información de competencia.

P1: ASIGNACIÓN POR COMPETENCIA
Entre agentes disponibles, elegir el de mayor
probabilidad de acierto para el tipo de tarea.
Desempate mediante identificador aleatorizado.

P2: ASIGNACIÓN POR FINALIZACIÓN ESPERADA
Elegir entre agentes disponibles el que maximice:

P(correcto) × P(finalizar antes del plazo).

Utilizar únicamente parámetros conocidos,
estado actual y estimaciones de servicio.

Todas las políticas:
- Comparten información de disponibilidad.
- Tienen idénticas restricciones operativas.
- No pueden anticipar llegadas futuras.
- No interrumpen tareas en ejecución.
- Rechazan tareas que no puedan admitirse.

Registrar por separado el coste de decisión.

P2 reutiliza una regla estándar de decisión;
no constituye un algoritmo HLS nuevo.

7. MATRIZ FACTORIAL

Factores:

Composición: H0, H1, H2.
Organización: P0, P1, P2.
Escala: 12, 24, 48.

Total: 3 × 3 × 3 = 27 condiciones.

Cada condición utiliza los mismos escenarios
exógenos que sus comparadores emparejados.

8. MÉTRICAS

PRINCIPAL

Success-on-time:

Número de tareas correctas y completadas
dentro del plazo / número de tareas llegadas.

Las tareas rechazadas, incorrectas o tardías
cuentan como fallos.

SECUNDARIAS

- Latencia media y percentil 95.
- Utilización media por agente y familia.
- Fracción de tareas rechazadas.
- Fracción incorrecta.
- Fracción tardía.
- Coste operativo total y por tarea correcta.
- Tiempo de decisión organizativa.
- Rendimiento por tipo de tarea.
- Rendimiento por fase de demanda.
- Recuperación tras cambios de demanda.

Definir recuperación como el primer instante
posterior al cambio en que la tasa de éxito
de una ventana de 50 unidades temporales
alcanza el 95 % de su referencia estable
predefinida.

Si no se alcanza, registrar "no recuperado".
No redefinir la ventana tras observar resultados.

9. SEMILLAS Y EMPAREJAMIENTO

PILOTO TÉCNICO:
3 semillas: 0, 1 y 2.

CAMPAÑA COMPLETA:
30 semillas: 1000–1029.

Para cada semilla:
- Generar una trayectoria exógena de llegadas.
- Generar tipos de tarea y sus plazos.
- Generar resultados potenciales de servicio
  y corrección por agente y tarea.
- Reutilizar la misma realización exógena
  entre condiciones comparables.

Separar flujos aleatorios de:
demanda, composición, servicio, corrección
y desempates.

Evitar que una decisión de una política altere
la secuencia aleatoria de otra.

10. ANÁLISIS ESTADÍSTICO

Contrastes pareados por semilla:

- H1-H0 y H2-H0 para cada política y escala.
- P1-P0 y P2-P0 para cada composición y escala.
- Interacción composición × organización.
- Contrastes N=24 frente a 12 y N=48 frente a 24.

Utilizar diferencias de tasas de éxito en
puntos porcentuales.

Calcular:
- Media de diferencias.
- IC del 95 % por bootstrap pareado
  sobre réplicas independientes.
- Tamaño del efecto.
- Consistencia de signo entre semillas.

Bootstrap: 10.000 remuestreos de semillas.

No remuestrear tareas como si fueran
observaciones independientes.

Umbral de relevancia práctica:
2 puntos porcentuales.

Aplicar ajuste Holm a los contrastes
confirmatorios predefinidos.

Los análisis por tarea y fase son secundarios.

11. CRITERIOS DE INTERPRETACIÓN

VENTAJA DE HETEROGENEIDAD:
Diferencia favorable >= 2 pp y límite inferior
del IC ajustado > 0.

VENTAJA ORGANIZATIVA:
Mismo criterio, comparando políticas bajo
composición y escala constantes.

INTERACCIÓN:
Contraste de diferencias-en-diferencias
composición × política con IC que excluya cero.
Informar también magnitud práctica.

EFECTO DE ESCALA:
Cambio sistemático del rendimiento normalizado
por carga ofrecida, no del volumen bruto.

AUSENCIA DE VENTAJA RELEVANTE:
Exigir equivalencia mediante TOST con margen
de ±2 pp; un resultado no significativo
no demuestra equivalencia.

RESULTADO INDETERMINADO:
IC demasiado amplio para distinguir ventaja,
perjuicio o equivalencia.

No seleccionar únicamente resultados favorables.

12. PILOTO TÉCNICO

Ejecutar las 27 condiciones con 3 semillas.

Verificar exclusivamente:
- Reproducibilidad.
- Conservación de tareas.
- Cumplimiento de plazos.
- Integridad de emparejamientos.
- Ausencia de fugas de futuro.
- Escalado de carga y recursos.
- Cálculo de métricas.
- Ausencia de errores de simulación.

No modificar parámetros según el signo
de los efectos observados.

13. CAMPAÑA COMPLETA

27 condiciones × 30 semillas = 810 simulaciones.

Cada réplica:
400 unidades temporales.

Llegadas esperadas por simulación:
N=12: 2.640
N=24: 5.280
N=48: 10.560

Volumen aproximado:
4,75 millones de tareas llegadas.

Coste computacional:
O(eventos × evaluación de agentes elegibles).

Estimación preliminar:
orden de minutos a decenas de minutos en CPU
moderna, sujeto a implementación y medición
del piloto técnico.

No requiere GPU ni entrenamiento.

14. CONGELACIÓN Y ENTREGABLES

Antes del piloto:
- Congelar configuración y código.
- Registrar hashes y versión.
- Congelar semillas y contrastes.
- Documentar los supuestos.
- Documentar las limitaciones de comparabilidad.

Entregar:
- Configuración reproducible.
- Matriz factorial.
- Logs de tareas y asignaciones.
- Métricas por réplica.
- Contrastes e intervalos.
- Coste computacional.
- Informe de resultados positivos, negativos
  y nulos.

No ejecutar experimentos en esta fase.
No desarrollar algoritmos nuevos.
No ajustar el escenario para favorecer HLS.

ALCANCE DE LAS CONCLUSIONES:

Los resultados serán observaciones de un modelo
sintético concreto, no propiedades universales
de la heterogeneidad ni de HLS.

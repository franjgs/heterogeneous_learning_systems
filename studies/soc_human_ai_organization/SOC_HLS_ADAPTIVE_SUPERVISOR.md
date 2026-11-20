# HLS-A: supervisor D1/P1 y piloto de desarrollo

**Estado:** implementación operativa y piloto de **desarrollo**; no se realizó una validación independiente preespecificada de HLS-A como candidato primario. Posteriormente se incluyó como comparador fijo en la [validación de HLS-B](SOC_HLSB_VALIDATION_RESULTS.md). D1 y P1 no fueron modificadas. HLS-A elige cuál de sus despachadores originales se aplica en cada época. Los resultados previos de [D1/P1](SOC_CONFIRMATORY_RESULTS.md) motivan el diseño, pero sus semillas y resultados no se usaron para seleccionar umbrales.

## Regla causal

Para cada clase pendiente \(k\), sea \(E_k\) el conjunto de analistas elegibles, \(B_k(t)\) los elegibles ocupados o en despacho y \(Q_k(t)\) las alertas pendientes de la clase. \(s_{ia}\) es el tiempo de servicio configurado para la pareja y \(\bar s_k=|E_k|^{-1}\sum_{i\in E_k}s_{ia_k}\), donde \(a_k\) es una alerta pendiente de esa clase (en este modelo la duración depende de analista y clase, no de la alerta). Se define:

\[
z_k(t)=\frac{|B_k(t)|}{|E_k|}+\frac{\sum_{a\in Q_k(t)}\min_{i\in E_k}s_{ia}}{|E_k|\bar s_k},\qquad z(t)=\max_{k:Q_k(t)\ne\varnothing}z_k(t).
\]

Una cola vacía produce \(z=0\). La primera parte mide ocupación de capacidad elegible; la segunda expresa el trabajo pendiente en servicios medios por analista elegible. El máximo por clase evita tratar los especialistas de distintas clases como perfectamente intercambiables. Es un **indicador heurístico adimensional**, no una estimación de utilización estacionaria ni de capacidad futura. Solo lee alertas que ya llegaron, disponibilidad, elegibilidad y duraciones configuradas; no recibe ρ, semilla, calendario de cambios ni resultados futuros.

HLS-A empieza en D1. En una época con analista libre y cola pendiente, pasa a P1 si \(z\ge h\); estando en P1 vuelve a D1 si \(z\le l\), con \(0\le l<h\). Entre ambos límites conserva el modo. El modo elegido se aplica al despacho actual; trabajos iniciados no se reasignan. No se introduce espera, latencia ni coste adicional. Las dos funciones originales y sus desempates permanecen en `src/hls/rq1_allocation.py`; `simulate_l1_l2` transmite la configuración HLS-A a los pools L1 y L2 existentes. Cada pool tiene estado de modo propio, porque su cola y capacidad difieren. `hlsa_history` registra instante, modo, presión, pendientes, ocupados y cambio. El runner guarda el historial L1 completo en `mode_history.csv` y sus conmutaciones en `switches.csv`.

## Piloto prefijado y reproducible

La [configuración](config/soc_hlsa_pilot.json) fija seis semillas nuevas `261170000–261170005`, distintas de A0, A3.2 y las 100 confirmatorias; H=24 h, D=24 h, roster y parámetros humanos de la campaña confirmatoria. Se probaron **solo tres parejas** \((l,h)=(0,5;1),(1;2),(2;3)\), sin ajuste por escenario. Escenarios: estacionarios ρ=0,85/1,00/1,25; ráfaga ρ=0,85 durante 0–8 h, 1,25 durante 8–16 h y 0,85 durante 16–24 h; y sobrecarga 1,25 durante 0–8 h seguida de 0,85 durante 8–24 h. El generador ya soporta `burst_window` y `arrival_rate_shift_after`; no se añadió batching. Las medias de demanda de ambos episodios variables son ρ≈0,983, de modo que pueden no acumular congestión sostenida.

La variable del piloto es R/N terminal: suma de probabilidades modeladas de corrección de alertas finalizadas dentro del deadline en H+D, dividida por admitidas; una escalada finaliza en L2. Las mismas trazas generadas por semilla se entregaron a D1, P1 y todos los candidatos. Los CSV por episodio y conmutación en `results/soc_hlsa_pilot/` (local, ignorado por Git) se generan con [run_soc_hlsa_pilot.py](run_soc_hlsa_pilot.py). Esta prueba de seis semillas sirve para elegir una configuración de desarrollo y observar fallos, no para inferencia confirmatoria.

## Resultados del piloto: R/N terminal medio; cambios L1 por episodio entre paréntesis

| Escenario | D1 | P1 | HLS-A 0,5/1 | HLS-A 1/2 | HLS-A 2/3 |
|---|---:|---:|---:|---:|---:|
| Estacionario 0,85 | 0,6554 | 0,6329 | 0,6340 (9,33) | 0,6445 (6,00) | 0,6540 (2,33) |
| Estacionario 1,00 | 0,6707 | 0,6350 | 0,6324 (1,67) | 0,6382 (2,67) | 0,6446 (6,67) |
| Estacionario 1,25 | 0,5202 | 0,5995 | 0,6019 (1,00) | **0,6044 (2,00)** | 0,6037 (2,00) |
| Ráfaga y recuperación | 0,6670 | 0,6341 | 0,6335 (3,33) | 0,6379 (3,67) | 0,6388 (2,33) |
| Sobrecarga inicial y recuperación | 0,6704 | 0,6327 | 0,6324 (1,00) | 0,6345 (2,33) | 0,6398 (2,33) |

Promediando las cinco celdas con el mismo peso, D1=0,6367; P1=0,6268; HLS-A 0,5/1=0,6268, 1/2=0,6319 y 2/3=0,6362. **Configuración propuesta para congelar antes de una evaluación independiente: \(l=2,h=3\)**, por mayor R/N medio entre los tres candidatos y baja conmutación en ρ=0,85. No se optimizó por separado para cada régimen. Sigue perdiendo frente a D1 en ρ=1,00 y en ambos episodios variables. No se afirma ventaja adaptativa demostrada. El efecto del orden de clases, SLA y calidad, así como las conmutaciones L2, requieren lectura de los datos por episodio antes de una interpretación de mecanismo más fuerte.

Con 2/3, P1 gobernó el 6,5 % de las épocas L1 en ρ=0,85, el 67,2 % en ρ=1,00, el 93,4 % en ρ=1,25, el 66,1 % en ráfaga y el 85,8 % en sobrecarga inicial. La presión detecta carga acumulada, pero en estas trazas no separa bien un régimen ρ=1,00 favorable a D1 de uno ρ=1,25 favorable a P1. Tras los intervalos de sobrecarga, la cola residual puede mantener P1 activo durante la recuperación; esta es una explicación compatible con el registro de modos, no una atribución causal aislada.

## Verificación y límites

Las pruebas comparan asignaciones y métricas del L1/L2 completo: HLS-A forzada permanentemente a D1 coincide con D1; forzada a P1 coincide con P1. Otras pruebas comprueban histéresis, reproducibilidad, cola vacía, elegibilidad restringida y unicidad de asignaciones. Pasaron **72 pruebas relevantes** en aquella etapa, incluidas cuatro nuevas de HLS-A. Los parámetros humanos, deadlines y escalado son sintéticos. El piloto no incluye costes de monitorización del supervisor y no reutiliza las 100 semillas confirmatorias para ajuste. El [diagnóstico directo](SOC_HLS_ADAPTIVE_DIAGNOSTIC.md) sustituye la reconstrucción de snapshots no equivalente, y HLS-A sigue sin ventaja demostrada en los episodios variables examinados.

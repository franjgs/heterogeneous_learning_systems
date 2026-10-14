# HLS Laboratory v1 — Contratos científicos y pruebas de aceptación

**Estado:** propuesta técnica CE-22, 14-10-2026. **No implementado ni validado experimentalmente.**

## 0. Pregunta y frontera

**Pregunta experimental inicial:** ¿Cómo interactúan la complementariedad funcional, el aprendizaje individual y el aprendizaje de una regla organizativa para determinar la capacidad de un equipo heterogéneo de satisfacer requisitos de problemas sucesivos, bajo recursos e información comparables?

Tres objetos independientes: **problema**, **experto**, **organización**. Se prohíbe identificar recompensa CES con cumplimiento funcional, competencia latente con rendimiento observado, o selección condicionada al estado con aprendizaje de la política. Se reutilizará MIS-v2 y, cuando sea compatible, producción multidimensional y acciones conjuntas de Small Problem World. No se hereda su contrato de tres decisiones por problema sin redefinirlo.

## 1. Contrato del problema

Un episodio contiene `problem_id`, vector de requisitos `r∈R_+^K`, dificultad `d`, restricciones de recursos `B`, horizonte `H` y protocolo de evaluación. `r` y `d` se especifican **independientemente** de cualquier función de recompensa y de las competencias del equipo; se registra su procedencia. Para v1: `K=2`, `H=1` decisión por problema. Esto elimina la ambigüedad de si tres decisiones eran intentos, etapas o acumulación. Una secuencia de problemas genera aprendizaje entre episodios. En versiones futuras, `H>1` exigirá especificar explícitamente acumulación, intentos o etapas.

**Producción inicial reutilizable:** `Y_k=Σ_i x_ik s_ik`, con `x_ik≥0`, `Σ_ik x_ik≤B` y restricciones de acción declaradas. **Éxito:** `all(Y_k≥r_k)`. **Déficit:** `Σ_k max(0,r_k−Y_k)/max(r_k,ε)` para `r_k>0`, omitiendo requisitos nulos; **margen:** `min_{k:r_k>0}(Y_k−r_k)`. Registrar además `Y`, esfuerzo ejecutado y, si existe, coste organizativo por separado. No presentar esfuerzo como coste monetario. La recompensa para aprendizaje organizativo se define antes de cada experimento (p. ej., éxito menos coste explícito), nunca se ajusta tras observar resultados.

**Separación orientación/dificultad:** orientación `u=r/Σr`; escala de exigencia `ρ=Σr`; `d` puede afectar una eficiencia de producción **solo si se especifica y controla**. En v1 basta usar `d=ρ` como etiqueta operacional de exigencia, sin introducir una segunda física artificial. Comparar pares con `u` igual y `ρ` distinto, y pares con `ρ` igual y `u` distinto.

## 2. Contrato del experto

Por experto `i`: competencia latente real `s_i(t)∈[0,1]^K`, estimación accesible a la organización `ŝ_i(t)`, exposición acumulada `e_i(t)`, política individual `π_i` (fija en v1), resultado atribuible `y_i(t)`, y transición `F_i`.

**Control de conocimiento perfecto:** `ŝ_i(t)=s_i(t)`. La estimación imperfecta queda como extensión, no se finge inferencia. El evaluador puede leer `s`; la política solo puede leer su vista informacional declarada. **MIS-v2:** `s_ik(t+1)=1−(1−s_ik(t)) exp(−λ x_ik(t))`; `e_ik(t+1)=e_ik(t)+x_ik(t)`. Con aprendizaje individual OFF, `s(t+1)=s(t)` aunque la exposición pueda registrarse. El rendimiento individual `y_ik=x_ik s_ik` se mide **antes** de la transición; no se interpreta como estimación de `s` sin controlar esfuerzo y dificultad.

**Invariantes:** sin exposición no cambia la competencia; competencia acotada; aprendizaje individual OFF no modifica `s`; la evolución del problema por sí sola no modifica `s`; cambios de resultado con `s` congelado pueden deberse a asignación o problema, no a aprendizaje.

## 3. Contrato de la organización

Organización `O=(π_θ,θ,I,A,U,c)` con vista informacional `I`, acciones factibles `A`, política `π_θ`, estado persistente `θ`, regla de actualización `U`, y costes explícitos `c`. Separar `a_t=π_{θ_t}(I_t)` de `θ_{t+1}=U(θ_t,I_t,a_t,o_t)`; la observación `o_t` se recibe **después** de ejecutar la acción. No permitir acceso a resultados futuros.

Tres clases, con idéntico espacio de acciones y presupuesto:

- **Fija por tipo:** tabla `q_tipo→acción` congelada a lo largo de la secuencia. Puede asignar agentes diferentes a tipos distintos; no usar como único comparador un experto global fijo.
- **Adaptativa no aprendida:** función determinista preespecificada de la vista actual, con `θ` inmutable. Puede variar la acción sin aprender.
- **Aprendida:** mismo contrato informacional y de acciones; `θ` cambia mediante un método estándar mínimo, p. ej. estimación incremental de valor por `(contexto discreto, acción)` con exploración predeclarada. No atribuir originalidad al algoritmo. La actualización debe modificar efectivamente futuras elecciones en un caso de prueba.

Para comparar **aprendizaje organizativo ON/OFF**, usar exactamente la misma clase de política, inicialización, secuencia, observaciones accesibles y regla de decisión; variar solo si `U` actualiza `θ`. Para comparar arquitecturas distintas, declarar que el efecto es de **paquete organizativo**, no de un único mecanismo causal.

**Cuidado metodológico:** con recompensas dependientes de competencias que cambian, el entorno de aprendizaje organizativo no es estacionario. En el primer control causal, congelar competencias y verificar aprendizaje organizativo aisladamente.

## 4. Factores y métricas predefinidos

Factores binarios independientes: aprendizaje individual `LI∈{OFF,ON}`; aprendizaje organizativo `LO∈{OFF,ON}`. Cuatro celdas `(0,0),(1,0),(0,1),(1,1)` para **la misma organización parametrizada**, cuando exista. Para el control de adaptación no aprendida, `LO=OFF` por definición. Misma secuencia de problemas, equipo inicial, restricciones, y semillas acopladas por comparación.

**Métricas primarias:** tasa de éxito por episodio, déficit medio y rendimiento acumulado neto de costes declarados. **Secundarias:** esfuerzo, margen, variación de competencias `Δs`, cambio de parámetros `Δθ`, frecuencia de cambio de asignaciones, arrepentimiento frente a referencia informada bajo el mismo presupuesto cuando computable. Registrar rendimiento de expertos solos y del equipo.

**Complementariedad:** para cada problema y estado inicial, comparar factibilidad del equipo con la mejor solución de un único experto **bajo el mismo presupuesto total**. Etiqueta `team_only = feasible_team && !any(feasible_single_i)`; esto identifica complementariedad funcional operacional, no sinergia superaditiva ni prueba de emergencia. También registrar casos `single_sufficient` y `none_feasible`. No construir todos los escenarios para forzar `team_only`.

## 5. Pruebas de aceptación obligatorias (fixtures analíticos, no resultados observados)

**P1. Independencia del problema.** `(r=(0.6,0.4), d=1)` y `(r=(0.9,0.6), d=1.5)` comparten orientación pero no exigencia; `(r=(0.4,0.6), d=1)` cambia orientación con igual exigencia. La producción de una acción dada es independiente de la recompensa CES; la evaluación depende de `r`.

**P2. Complementariedad genuina.** Dos expertos `s1=(1,0)`, `s2=(0,1)`; presupuesto total `B=2`, esfuerzo máximo por experto `≤1`, requisitos `(0.8,0.8)`. Equipo factible con una unidad de esfuerzo por experto; cada experto solo es incapaz de satisfacer ambos requisitos incluso con presupuesto total 2. Control adicional: requisitos `(0.8,0)` permiten suficiencia individual. Nota: si el espacio de acciones original prohíbe esta asignación, no declarar que el componente sirve sin adaptación explícita.

**P3. No complementariedad.** Dos expertos `s1=s2=(1,1)`, requisitos `(0.5,0.5)` y presupuesto 1; al menos un experto solo puede satisfacer el problema distribuyendo esfuerzo. No clasificarlo como `team_only`.

**P4. Aprendizaje individual aislado.** Con `LI=ON`, `λ>0`, exposición positiva en capacidad no dominada, `s` aumenta según MIS-v2; con `LI=OFF`, `s` no cambia; `θ` idéntico en ambos cuando `LO=OFF`.

**P5. Aprendizaje organizativo aislado.** Con `LI=OFF`, dos acciones organizativas y dos contextos recurrentes de rendimientos opuestos, el actualizador cambia `θ` y altera una decisión futura tras evidencia suficiente; con `LO=OFF` la misma política no cambia `θ`. Registrar también casos donde explorar no mejora rendimiento neto.

**P6. Adaptación ≠ aprendizaje.** Una política determinista puede elegir acciones distintas ante dos estados sin variar `θ`. La traza debe reflejar `action_changed=True`, `policy_updated=False`.

**P7. Causalidad e información.** Para cada pareja LI/LO, comprobar que solo se interviene el mecanismo anunciado, que las políticas no leen `s` real cuando su contrato solo ofrece `ŝ`, que no existe acceso a observaciones futuras y que se preservan semillas y recursos.

**P8. Antisaturación antes de factorial.** En una micro-muestra preregistrada de orientaciones y exigencias, verificar que existen casos factibles/no factibles y que no todas las organizaciones tienen éxito 100%. Si falla, revisar el dominio de problemas por razones de cobertura, no ajustar retrospectivamente para favorecer HLS.

**P9. Reproducibilidad.** Igual configuración y semilla producen la misma trayectoria; serializar `problem, s, ŝ, e, θ, action, y, Y, success, deficit, costs, updates` por episodio.

## 6. Ensamblaje mínimo y límites

Reutilizar **MIS-v2** para evolución; **Small Problem World** para producción multidimensional/acciones conjuntas solo si el contrato de recursos es compatible; **G3** como referencia de asignación; **CE-16** para patrones de trazabilidad, no sus definiciones de éxito; **G0** como fuente de comparadores, no como definición universal. No fusionar físicamente todos los laboratorios. `finite_problem_belief` se mantiene fuera de v1: sus creencias son sobre problemas, no sobre competencias.

**No implementar todavía:** FAST/DEEP, META-VOC, redes neuronales, incertidumbre de `ŝ`, comunicación, jerarquías, transferencia entre expertos, problemas con dependencias DAG, metaaprendizaje. La primera versión debe permitir agregar estos mecanismos mediante interfaces sin atribuirlos ya al simulador.

**Entrega de ingeniería siguiente:** identificar adaptadores existentes y construir una vertical slice que supere P1–P9 con un solo equipo y una secuencia corta. Solo después se justifica un factorial. No commits/push sin autorización.

## 7. Riesgos científicos explícitos

1. Un `team_only` positivo puede deberse a complementariedad funcional por restricciones y no a aprendizaje organizativo: analizarlo por separado.
2. La política aprendida puede necesitar exploración y perder inicialmente frente a una política informada: comparar coste de aprendizaje y rendimiento fuera de entrenamiento.
3. Un método tabular no generaliza por sí solo a equipos nuevos: la generalización es una pregunta posterior con holdouts por geometría, no por semilla.
4. La representación aditiva de producción no permite estudiar interdependencias complejas: documentar ese límite, sin inventar sinergias.
5. La ley MIS-v2 no está calibrada empíricamente; toda afirmación sobre velocidad de aprendizaje exige sensibilidad en `λ`.

---

**Trazabilidad de incorporación (CE-23):** este archivo reproduce el documento de referencia `/Users/fran/Downloads/HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md`, proporcionado por la dirección científica. La implementación ejecutable y su estado de validación se documentan por separado en `HLS_LAB_V1.md`; no se reescriben aquí las decisiones del contrato.

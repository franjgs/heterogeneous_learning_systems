C3.0 — Especificación teórica y experimental

Estado: C3.0 — CONCEPTUALLY CLOSED; NUMERICAL DESIGN PENDING
Objeto: Campaign 3 — Adaptive Prospective Reasoning
Dependencia: C0–C2 cerradas; Campaign 2 clasificada ROBUST POSITIVE WITH IMPORTANT NULL RESULT; auditoría de cobertura posterior: INSUFFICIENT COVERAGE.
Regla: C3 no modifica la física, inferencia, aprendizaje o políticas prospectivas existentes salvo decisión explícita posterior.

⸻

1. Pregunta científica

C3 estudia:

\boxed{\text{When and how much is it worth anticipating future consequences of a decision?}}

en un sistema adaptativo donde las decisiones presentes modifican simultáneamente:

\text{acción}
\rightarrow
\begin{cases}
\text{información futura},\\
\text{capacidad futura},
\end{cases}

y, por tanto, alteran el estado desde el que se tomarán decisiones posteriores.

Las cuatro políticas existentes se utilizan como instrumentos experimentales que representan diferentes formas de anticipación, no como niveles ordenados de inteligencia:

Q^{00}:\varnothing,\qquad
Q^{10}:I,\qquad
Q^{01}:D,\qquad
Q^{11}:I+D.

C3 no presupone que Q^{11} sea óptima ni que mayor anticipación produzca mayor rendimiento.

⸻

2. Motivación empírica

C2 estableció, bajo la física y test range congelados, que:

1. la anticipación prospectiva modifica decisiones de forma no trivial;
2. la anticipación de información Q^{10} y conjunta Q^{11} produjo beneficio realizado condicional positivo en estados divergentes del banco de referencia Q11 bajo el endpoint local utilizado;
3. Q^{01} no mostró utilidad realizada condicional detectable bajo ese mismo endpoint y banco de estados;
4. \Delta Q>0 no implica \Delta G>0;
5. Q^{11} no estableció superioridad sobre Q^{10};
6. existe no separabilidad prospectiva I+D, pero con baja prevalencia;
7. los resultados de C2 están condicionados a estados visitados por Q^{11}.

El último punto impide utilizar directamente C2 para construir un selector adaptativo: un selector modifica sus propias trayectorias y, por tanto, la distribución futura de estados.

C3 no reinterpreta ni reabre C2.

⸻

3. Física congelada

C3 mantiene, salvo modificación explícitamente autorizada:

N=3,\qquad K=2,\qquad s_{ik}\in[0,1],

CES con:

\rho=0.5,

observaciones gaussianas:

r_t\sim\mathcal N(\mu_t,\sigma^2),
\qquad\sigma=0.10,

MIS-v2:

s_{ik}^{+}
=
1-(1-s_{ik})e^{-\lambda x_{ik}},

con el valor de \lambda correspondiente al \eta=0.35 congelado,

\lambda=-\log(0.65),

belief model finito:

\hat{\mathcal Z}
=
\{(.8,.2),(.5,.5),(.2,.8)\},

Bayes sobre dicho soporte, MPC de horizonte heredado, mismo action space, misma cuadratura y mismas reglas de tie-breaking.

Continúan fuera de C3.0:

* TMS;
* transferencia entre capacidades;
* forgetting;
* comunicación;
* REFRAME;
* nuevas formas de aprendizaje;
* nuevos mecanismos organizativos.

⸻

4. Mundo de problemas

El dominio físico congelado se parametriza mediante:

z(p)=(p,1-p),
\qquad
p\in[0,1],

de modo que:

\mathcal Z_{\rm physics}
=
\{z(p):p\in[0,1]\}.

El dominio inicial del generador experimental de C3 es únicamente el
subconjunto:

\mathcal Z_{\rm C3}
=
\{z(p):p\in[0.2,0.8]\}
\subset
\mathcal Z_{\rm physics}.

Esta restricción pertenece al diseño experimental de C3 y no redefine la
física ni la ontología continua del problema HLS.

Se mantiene la distancia de producción derivada:

d_R(p,q)
=
|p-q|\left(1+|p+q-1|\right).

Los descriptores existentes conservan su significado:

C_j=d_R(p_j,p_{j-1}),

N_j=\min_{k<j}d_R(p_j,p_k),

M_j=\min_{\hat p\in\{.8,.5,.2\}}d_R(p_j,\hat p).

C,N,M son variables del experimentador; no son automáticamente observables por el agente.

⸻

5. Dinámica de problemas

Una historia deja de ser un tratamiento diseñado manualmente y pasa a ser una realización de un proceso:

\mathcal H=(p_1,\ldots,p_J),

p_{j+1}\sim K_\phi(\cdot\mid p_j,\mathcal H_j).

La familia inicial utiliza tres mecanismos:

p_{j+1}=
\begin{cases}
p_j & \mathrm{STAY},\\
\operatorname{reflect}(p_j+\epsilon_j) & \mathrm{MOVE},\\
p_k,\quad p_k\in\mathcal R_j & \mathrm{RETURN}.
\end{cases}

RETURN es recurrencia histórica estricta. Su conjunto elegible es:

\mathcal R_j
=
\{p_k:k<j\ \text{y}\ p_k\ne p_j\}.

RETURN muestrea un valor de \(\mathcal R_j\). Si \(\mathcal R_j\) está vacío,
RETURN no está disponible en esa transición y se renormalizan las
probabilidades de los mecanismos disponibles STAY y MOVE. STAY conserva
\(p_{j+1}=p_j\). MOVE no impone una restricción explícita de novedad.

con:

\phi=
(\alpha_{\rm stay},
\alpha_{\rm return},
\sigma_{\rm move}),

\alpha_{\rm move}
=
1-\alpha_{\rm stay}-\alpha_{\rm return}.

MOVE utiliza reflexión, no clipping, en [0.2,0.8].

\sigma_{\rm move} parametriza la distribución de desplazamientos en p; no se identifica directamente con change scale. El cambio físico realizado se mide mediante d_R.

Esta familia es un generador experimental HLS, no un modelo empírico de entornos reales.

⸻

6. Horizonte temporal

La unidad temporal estructural es el problema, no simplemente el timestep.

Cada problema mantiene inicialmente las tres decisiones actuales.

Sea \(j(t)\) el problema que contiene la decisión \(t\), y sea \(e(j)\) el
timestep final del problema \(j\). Para todo \(\ell\) tal que
\(j(t)+\ell\le J\), se define:

\[
G_t(\ell)
=
\sum_{\tau=t}^{e(j(t)+\ell)}\mu_\tau^{true}.
\]

Por tanto, \(\ell=0\) incluye desde la decisión actual hasta el final del
problema actual; \(\ell=1\) incluye ese remanente más el problema siguiente
completo; y, en general, \(\ell=L\) incluye el remanente actual más \(L\)
problemas posteriores.

Para una intervención en \(t\), definimos el perfil de consecuencia:

\boxed{
\Delta G_m(\ell\mid h_t)
}

donde \(\ell\) representa exactamente el número de problemas completos
posteriores al problema actual incluidos en la evaluación, además del
remanente del problema actual.

No se utiliza descuento:

\gamma=1.

Se conservará como diagnóstico histórico separado:

\Delta G_{t,2},

para continuidad con C2. Este endpoint contiene exactamente dos recompensas
reales dentro del mismo problema y no se identifica con \(\ell=0\), que llega
hasta el final del problema actual.

El outcome de largo alcance incluye efectos persistentes de S a través de fronteras entre problemas.

Una firma posible —no presupuesta— es:

\Delta G_{\rm short}<0,
\qquad
\Delta G_{\rm long}>0,

que representaría sacrificio inmediato con amortización posterior.

⸻

7. Horizon-sensitivity gate

No se declara a priori que seis problemas ni doce problemas sean suficientes para valorar desarrollo persistente.

C3.0 utilizará inicialmente:

\boxed{J_{\rm pilot}=12\text{ problemas}}

como ventana diagnóstica, no como constante científica ni horizonte confirmatorio.

Para cada intervención se estudiará:

\Delta G_m(0),\Delta G_m(1),\ldots

y la contribución marginal:

\delta_\ell
=
\Delta G_m(\ell)-\Delta G_m(\ell-1).

Se examinarán:

* estabilidad del signo;
* evolución de magnitud;
* inversiones short-term/long-term;
* persistencia de contribuciones marginales.

Si doce problemas no permiten una valoración temporal suficientemente estable, el horizonte de development se ampliará antes de congelar el diseño confirmatorio.

Los datos utilizados para decidir este horizonte quedan clasificados como development/pilot, nunca confirmatory.

No se exige convergencia de S.

Las observaciones están censuradas por el final de historia: para estimar horizonte \ell, sólo son elegibles estados con suficiente futuro observado. No se imputa valor cero al futuro inexistente.

⸻

8. Frontera epistemológica

Sea \mathcal F_t el conjunto de información realmente disponible inmediatamente antes de la decisión.

Regla fundamental:

\boxed{
\text{A selector feature is admissible only if it can be computed from }
\mathcal F_t
\text{ before the decision.}
}

Las primitivas admisibles son:

S_t,\qquad b_t,\qquad\tau_t.

También son admisibles transformaciones deterministas de información disponible.

Se distinguen cinco clases.

Clase	Ejemplos	Uso
A — primitivas	S,b,\tau	selector
B — observables derivados baratos	\mathcal H(b),H_S(S)	selector
C — deliberativos	D_I,D_{I,\mathrm{loss}},A_I,A_D,A_{ID},\Gamma	diagnóstico o selector con coste explícito
D — experimenter-only	z,p,M,C,N,\phi,\mu^{true}	análisis
E — futuro/contrafactual	\Delta G,z_{\rm future},\epsilon_{\rm future}	target/evaluación

En particular, D_I no es gratuito porque requiere resolver acciones óptimas condicionadas a hipótesis.

No se proporcionarán IDs como G07, TR-G, seed o identificadores equivalentes.

Las variables de historia observable r_{<t},X_{<t},b_{\le t} son legítimas en principio, pero no se realizará feature engineering histórico antes de comprobar la capacidad predictiva de la representación básica.

⸻

9. Valor local y valor de estrategia

C3 distingue dos estimandos.

9.1 Consecuencia local de una decisión prospectiva

Para modo inicial m, continuación c y horizonte \ell:

Y_m^c(h_t,\ell)
=
E\left[
G_t(\ell)
\mid
do(m_t=m),
\pi_{t+1:}=Q^c,
h_t
\right].

Las ramas contrafactuales utilizan common random numbers compartiendo innovaciones gaussianas, no observaciones brutas.

No existe un supuesto «true local value» independiente de la continuación.

9.2 Valor de una estrategia secuencial

Un selector adaptativo es:

M:h_t^{obs}\mapsto m_t.

Su ejecución es:

m_t=M(h_t),

X_t=\pi^{m_t}(h_t),

h_{t+1}\sim P(\cdot\mid h_t,X_t),

m_{t+1}=M(h_{t+1}).

Su rendimiento es:

\boxed{
J(M)=
E_M\left[
\sum_{t=1}^{T}\mu_t^{true}
\right].
}

Por construcción:

\boxed{
\text{local prospective value}\neq
\text{sequential selector value}.
}

La evaluación final del selector será on-policy.

⸻

10. Gate G1 — Continuation sensitivity

C3 no asumirá que una etiqueta local de «mejor modo» sea estable.

Se utilizarán dos continuaciones contrastantes congeladas:

\boxed{c\in\{Q00,Q11\}.}

Para cada una:

m_c^*(h,\ell)
=
\arg\max_mY_m^c(h,\ell).

Se estudiarán:

* acuerdo de argmax;
* estabilidad de contrastes pairwise;
* dependencia del horizonte;
* regrets cruzados.

Por ejemplo:

R_{00\rightarrow11}
=
Y_{m^*_{11}}^{11}
-
Y_{m^*_{00}}^{11},

R_{11\rightarrow00}
=
Y_{m^*_{00}}^{00}
-
Y_{m^*_{11}}^{00}.

No se fija un porcentaje arbitrario de aprobación.

G1 admite tres resultados:

ROBUST LOCAL STRUCTURE: la decisión relevante es ampliamente estable y los desacuerdos tienen consecuencias pequeñas.

PARTIAL LOCAL STRUCTURE: existen regiones robustas y regiones fuertemente dependientes de continuación.

STRONG POLICY DEPENDENCE: las decisiones cambian materialmente según la continuación.

En el último caso:

\boxed{\text{se abandona la ruta de selector supervisado local}}

y C3 pasa a formulación directamente secuencial.

G1 es empírico; actualmente sólo queda congelado su protocolo.

⸻

11. Gate G2 — Hybrid state coverage

Sólo se ejecuta como gate de la ruta local si G1 no la descarta.

La behavior policy inicial será:

\boxed{
\beta_U(m\mid h)=1/4
}

sobre los cuatro modos.

No es una estrategia candidata. Es un instrumento de generación de estados.

El dataset inicial de development procede de:

\boxed{
D_{\rm dev}^{(0)}
=
D_{00}\cup D_{10}\cup D_{01}\cup D_{11}
\cup D_{\beta_U}.
}

La cobertura se audita en tres niveles.

Mode → action

K_X(h)
=
|\{X^{00},X^{10},X^{01},X^{11}\}|.

Se registran también divergencias pairwise.

Action → state

Se examinan separadamente cambios inducidos en:

S_{t+1}

y

b_{t+1}.

No se introduce inicialmente una métrica escalar arbitraria conjunta.

State coverage

La cobertura relevante se evalúa en el espacio observable/admisible para el selector, no mediante variables ocultas del mundo.

Randomización de modos no implica automáticamente cobertura de estados.

Durante development puede realizarse:

D_{\rm dev}
\rightarrow
M_{\rm provisional}
\rightarrow
D_M

para comprobar si el selector provisional visita regiones fuera del soporte de development.

Si ocurre, el development set puede ampliarse y el selector reentrenarse.

Esta iteración está prohibida utilizando confirmatory data.

No se introduce \epsilon-greedy ni otro mecanismo exploratorio salvo que G2 demuestre su necesidad.

⸻

12. Counterfactual outcome coverage

Desde cada estado de development elegible, el simulador puede clonarse y evaluar:

m\in\{00,10,01,11\}.

Esto proporciona:

Y^{00},Y^{10},Y^{01},Y^{11}

bajo las continuaciones y horizontes especificados.

Por tanto se distinguen:

\mathcal C_S:\text{state coverage},

\mathcal C_A:\text{action/mode coverage},

\mathcal C_Y:\text{outcome coverage}.

Branching contrafactual proporciona directamente \mathcal C_A y \mathcal C_Y en los estados observados.

G2 se centra principalmente en:

\boxed{\mathcal C_S.}

⸻

13. Espacio de equipos

Los equipos iniciales pertenecen a:

\mathcal S=
\left\{
S\in[0,1]^{3\times2}:
\sum_i s_{i1}=1.5,\;
\sum_i s_{i2}=1.5
\right\}.

Las identidades iniciales de agentes son intercambiables, por lo que el espacio experimental relevante es:

\boxed{\mathcal S/\mathfrak S_3.}

Cada equipo se representa canónicamente ordenando sus filas mediante una regla determinista.

La separación geométrica se mide mediante:

\boxed{
d_S(S_A,S_B)
=
\min_{P\in\mathfrak S_3}
\|S_A-PS_B\|_F.
}

d_S es una distancia de diseño experimental. No se interpreta como distancia cognitiva ni diferencia de rendimiento.

⸻

14. Gate G3 — Team-space design

Los equipos no se muestrearán ingenuamente de forma uniforme.

Se generará un pool de candidatos que satisfaga los presupuestos de capacidad, se eliminarán equivalencias por permutación y se seleccionará un diseño space-filling/maximin bajo d_S.

Los equipos históricos:

G00,G04,G05,G07

se mantienen como anchors obligatorios.

El conjunto se dividirá antes de observar performance C3 en:

\mathcal S_{\rm dev}

y

\mathcal S_{\rm test}.

Los equipos confirmatorios deberán representar regiones geométricas retenidas, no simples permutaciones ni nuevas seeds.

G3 queda congelado como principio de diseño; el diseño numérico queda pendiente.

⸻

15. Generalización

C3 distingue explícitamente:

G_{\rm stochastic}
\subset
G_{\rm temporal}
\subset
G_{\rm team}
\subset
G_{\rm structural}.

El diseño confirmatorio distinguirá:

	Dinámica conocida	Dinámica retenida
Equipo conocido	interpolación / stochastic-temporal	dynamic generalization
Equipo retenido	team generalization	structural generalization

El caso más exigente es:

\boxed{
S_{\rm unseen}\times K_{\phi,\rm unseen}.
}

Una dinámica retenida significa una región de \Phi excluida de development antes del entrenamiento, no simplemente una nueva realización.

Un equipo retenido significa una geometría excluida de development, no una permutación.

⸻

16. C3.2 — Predictability gate

Si G1 permite una formulación local y G2 proporciona cobertura suficiente, C3.2 pregunta:

\boxed{
\text{Does ex-ante observable information predict the prospective
consequences of different forms of anticipation?}
}

No se utilizará inicialmente clasificación directa del ganador.

Se preferirá estimar:

\widehat Y_m(h,\ell)

o contrastes relativos:

\widehat{\Delta Y}_{m,n}(h,\ell).

Esto conserva información sobre magnitud.

El regret de selección puede expresarse como:

R_M(h)
=
Y_{m^*}(h)-Y_{M(h)}(h).

Se utilizarán mecanismos estándar comprados, preferentemente interpretables, antes de inventar un nuevo algoritmo.

Baselines obligatorios:

\text{always }Q00,\quad
\text{always }Q10,\quad
\text{always }Q01,\quad
\text{always }Q11,

más best-fixed determinado exclusivamente con development data.

Si la información predecisional no proporciona reducción fuera de muestra útil respecto a baselines fijos:

\boxed{\text{PREDICTABILITY GATE FAIL}.}

No se construirá entonces un selector más sofisticado para rescatar retrospectivamente el resultado.

⸻

17. C3.3 — Sequential adaptive selection

Sólo después de superar el predictability gate se construye un selector:

M(h_t^{obs})\rightarrow m_t.

Su evaluación será mediante ejecución real en el simulador.

No se inferirá su rendimiento únicamente de los contrafactuales offline de C3.2.

Esto permite que:

M
\rightarrow X_t
\rightarrow(S_{t+1},b_{t+1})
\rightarrow M(h_{t+1})

genere endógenamente su propia distribución de estados.

El selector se congela antes de C3-confirmatory.

⸻

18. Deliberation effort

C3 medirá desde el comienzo esfuerzo deliberativo como outcome secundario ortogonal.

No se modifica la recompensa:

\boxed{R'=R-\lambda C\quad\text{PROHIBIDO en C3}.}

No se introduce ponderación arbitraria performance/coste.

La unidad primaria será el número lógico de solicitudes de evaluación del modelo:

\boxed{N_g^{request}}.

Se registrarán además:

N_g^{eval},
\quad
N_R,
\quad
N_B,
\quad
N_F,
\quad
N_{\max},
\quad
N_{\rm branch}.

N_g^{request} caracteriza el algoritmo; N_g^{eval} permite observar efectos de caching/implementación.

CPU y wall time son diagnósticos secundarios.

⸻

19. Coste del selector

Toda operación necesaria para decidir qué planner ejecutar forma parte del coste online:

\boxed{
C_{\rm adaptive}
=
C_M+C_m.
}

Por tanto, una feature deliberativa no es gratuita.

El coste de generar datos, entrenar modelos y producir contrafactuales:

C_{\rm data/train}

se registra si resulta útil para reproducibilidad, pero no forma parte de la frontera de deployment.

⸻

20. Performance–deliberation frontier

Para estrategia M:

P(M)
=
E\left[\sum_t\mu_t^{true}\right],

C(M)
=
E\left[\sum_tN_{g,t}^{request}\right].

La evaluación secundaria considera:

\boxed{(C(M),P(M)).}

No se exige:

P(M)>P(Q11).

Un selector puede ser relevante si aproxima el rendimiento de una política más costosa con menor deliberación.

Igualmente puede resultar dominado por una política fija.

La interpretación será Pareto, no mediante utilidad escalar inventada.

⸻

21. Hipótesis de trabajo

Estas hipótesis deben refinarse y preregistrarse después de los gates de diseño, pero C3.0 establece la siguiente estructura.

H1 — Conditional prospective value

El valor realizado de anticipar consecuencias futuras depende del estado predecisional y del tipo de consecuencia anticipada.

No se presupone que esta dependencia sea suficientemente predecible.

H2 — Temporal structure

Diferentes formas de anticipación pueden producir perfiles temporales diferentes:

\Delta G_m(\ell).

En particular, C3 comprobará si la valoración de DEVELOPMENT cambia al ampliar el horizonte respecto al endpoint local de C2.

No se presupone que aparezca beneficio a largo plazo.

H3 — Local predictability

Información legítimamente disponible antes de la decisión puede contener señal suficiente para discriminar regiones donde distintos modos tienen diferente prospective value.

Puede ser falsada por G1/C3.2.

H4 — Sequential utility

Una regla de selección basada en señal local no tiene garantizado producir mejor rendimiento secuencial, porque modifica su propia distribución futura de estados.

Debe demostrarse on-policy.

H5 — Performance–deliberation

Si existe predictabilidad explotable, una estrategia adaptativa puede ocupar una región no dominada del plano performance–deliberation respecto a políticas fijas.

No se presupone superioridad.

⸻

22. Resultados negativos explícitamente admisibles

C3 se considera científicamente informativa si demuestra cualquiera de los siguientes:

* el prospective value depende demasiado de continuation para admitir una etiqueta local estable;
* randomized hybrid behavior no proporciona cobertura adecuada;
* las features observables no predicen prospective value;
* DEVELOPMENT continúa sin mostrar valor realizado a horizontes mayores;
* un selector local funciona offline pero falla on-policy;
* el selector no generaliza a nuevos equipos;
* no generaliza a nuevas dinámicas;
* queda dominado por una política fija;
* el coste de decidir qué planner usar elimina cualquier ventaja deliberativa;
* ninguna estrategia adaptativa mejora la frontera de políticas fijas.

Estos resultados no serán reinterpretados retrospectivamente como éxitos de otra hipótesis.

⸻

23. Prohibiciones metodológicas

Antes de C3-confirmatory no se permitirá:

1. modificar la física para favorecer discriminación;
2. calibrar \eta para producir beneficio de DEVELOPMENT;
3. cambiar \hat Z después de observar resultados;
4. utilizar p,z,M,C,N,\phi como features del selector;
5. introducir IDs de equipo/escenario;
6. seleccionar el horizonte que maximice performance del selector;
7. elegir una continuation después de ver cuál produce etiquetas más predecibles;
8. introducir una ponderación arbitraria performance/computation;
9. utilizar confirmatory data para feature engineering;
10. iterar coverage sobre confirmatory data;
11. presentar Q11 como oracle;
12. interpretar \Gamma como causal synergy;
13. interpretar d_S como distancia funcional o cognitiva;
14. promover análisis exploratorios a hipótesis confirmatorias después de observar resultados.

⸻

24. Orden operativo

La secuencia queda congelada conceptualmente como:

\boxed{
\begin{array}{c}
\text{C3.0 SPECIFICATION}\\
\downarrow\\
\text{Problem-space numerical design}\\
+\text{ Team-space numerical design}\\
\downarrow\\
\text{12-problem horizon pilot}\\
\downarrow\\
\text{G1 Continuation Sensitivity}\\
\downarrow\\
\text{G2 Hybrid State Coverage}\\
\downarrow\\
\text{C3.2 Predictability}\\
\downarrow\\
\text{freeze selector}\\
\downarrow\\
\text{C3.3 On-policy Development Evaluation}\\
\downarrow\\
\text{freeze confirmatory protocol}\\
\downarrow\\
\text{C3.4 Confirmatory Generalization}
\end{array}}

G1 puede cancelar la ruta de predictor local.

G2 puede exigir modificar únicamente el mecanismo de development state collection, no la física.

C3.2 puede cancelar la construcción del selector.

⸻

25. Estado de freeze

Con esta especificación quedan conceptualmente congelados:

\boxed{
\begin{aligned}
&\text{pregunta científica de C3},\\
&\text{separación local/secuencial},\\
&\text{frontera epistemológica},\\
&\text{tratamiento del horizonte},\\
&\text{familia STAY/MOVE/RETURN},\\
&\text{dominio experimental inicial }\mathcal Z_{\rm C3}
  =\{z(p):p\in[.2,.8]\}\subset\mathcal Z_{\rm physics},\\
&\text{principio de diseño del team space},\\
&\text{continuation-sensitivity gate},\\
&\text{hybrid-coverage gate},\\
&\text{full counterfactual labeling},\\
&\text{evaluación final on-policy},\\
&\text{separación development/confirmatory},\\
&\text{medición de deliberation effort},\\
&\text{interpretación Pareto}.
\end{aligned}}

Quedan deliberadamente sin congelar hasta sus respectivos gates:

\boxed{
\begin{aligned}
&J_{\rm confirmatory},\\
&\text{valores numéricos de }\Phi_{\rm dev/test},\\
&\text{número y selección exacta de nuevos equipos},\\
&\text{métrica operativa final de state coverage},\\
&\text{feature set final},\\
&\text{modelo predictor comprado},\\
&\text{selector final},\\
&\text{protocolo estadístico confirmatorio}.
\end{aligned}}

Clasificación

\boxed{\textbf{C3.0 — CONCEPTUALLY CLOSED; NUMERICAL DESIGN PENDING}}

Campaign 3 no debe ejecutarse todavía ni debe iniciarse una implementación amplia. El siguiente trabajo es diseñar numéricamente, sin performance runs, los espacios \Phi y \mathcal S. Sólo entonces tendría sentido implementar el horizon pilot y G1.

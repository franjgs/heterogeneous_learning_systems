import csv,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'results/soc_hls_overload_duration'
def read(n):return list(csv.DictReader((OUT/n).open()))
d=read('d1.csv');ds=read('d1_timeseries.csv');e=read('episodes.csv');c=read('cohorts.csv');ts=read('timeseries.csv');mo=read('modes.csv');meta=json.loads((OUT/'physical_metadata.json').read_text());cfg=meta['config'];durations=cfg['durations_h'];profiles=[]
mean=statistics.mean;sd=statistics.stdev
def paired(rows,dur,a,b,cut=48.):
 x={int(z['seed']):float(z['RN']) for z in rows if int(z['duration_h'])==dur and z['policy']==a and float(z['cutoff_h'])==cut};y={int(z['seed']):float(z['RN']) for z in rows if int(z['duration_h'])==dur and z['policy']==b and float(z['cutoff_h'])==cut};assert x.keys()==y.keys();v=[x[k]-y[k] for k in sorted(x)];m=mean(v);s=sd(v);h=2.093*s/(len(v)**.5);return m,s,m-h,m+h,sum(z>0 for z in v)
assert len(d)==120 and len(e)==720 and len(ts)==34920
for dur in durations:
 for seed in {int(x['seed']) for x in d if int(x['duration_h'])==dur}:
  a=next(x for x in d if int(x['duration_h'])==dur and int(x['seed'])==seed);z=[x for x in e if int(x['duration_h'])==dur and int(x['seed'])==seed];assert len(z)==6 and len({x['trace_sha256'] for x in z})==1 and len({x['admitted'] for x in z})==1 and all(int(x['admitted'])==int(x['completed'])+int(x['pending']) for x in z);assert a['trace_sha256']==z[0]['trace_sha256'] and int(a['admitted'])==int(z[0]['admitted'])
lines=['# Duración crítica de sobrecarga y recuperación dinámica','',
'**Estado:** piloto exploratorio de 20 semillas nuevas por duración. HLS-B congelada (ventana 4 h, umbral bajo 1,05, alto 1,20). No es validación independiente ni se reajusta el supervisor.','',
'## Hipótesis física y diseño','',
'Con tasa de llegada mayor que la capacidad, el trabajo pendiente crece aproximadamente como la diferencia de tasas acumulada, modificada por clases, elegibilidad, deadlines, escalado y orden D1. Tras volver a la tasa normal, la cola residual determina cuánto tarda en recuperarse el sistema. Por ello, R/N depende conjuntamente de duración del pulso, volumen esperado, tiempo de recuperación restante dentro de H y estados heredados; no se atribuirán todas las diferencias a duración aislada.','',
'ρ normal=0,85, ρ pulso=1,25; H=24 h, D=24 h; inicio del pulso t=4 h; fin t=4+d; retorno inmediato a ρ=0,85 hasta H. Duraciones d=2,4,6,8,12,16 h. Drenaje sin nuevas llegadas hasta t=48. Roster 6 L1/3 L2, servicios, elegibilidad, competencias, deadlines y reglas de escalado son los del estudio HLS-B; se mantienen congelados. Capacidad fluida L1 = '+f'{meta["mu_l1"]:.3f}'+ ' alertas/h. Semillas 261230000–261230019.','',
'Tasa esperada normal/pulso/recuperación: '+f'{.85*meta["mu_l1"]:.2f}'+ '/'+f'{1.25*meta["mu_l1"]:.2f}'+ '/'+f'{.85*meta["mu_l1"]:.2f}'+ ' alertas/h. Llegadas esperadas en H son '+f'{meta["expected_arrivals_by_duration"]}'+ '. El pulso aporta '+f'{1.25*meta["mu_l1"]:.2f}'+ ' d llegadas esperadas durante su duración; al aumentar d, aumenta volumen y disminuye recuperación previa a H.','',
'## Verificación física D1','',
'Primero se ejecutaron 120 episodios D1. Congestión real se define aquí como cola L1+L2 positiva al final del pulso y trabajo pendiente positivo. Recuperación operacional: primer instante postpulso donde durante tres muestras consecutivas de 0,5 h la suma de colas L1+L2 y la suma de trabajo nominal pendiente no superan sus respectivos valores en t=4 h. Recuperar cola no equivale a cumplir SLA. Recuperables: alertas pendientes cuyo deadline aún permite finalización inmediata por al menos un analista elegible del pool, usando su servicio modelado; es un diagnóstico optimista que no reserva esa capacidad. Irrecuperables: deadline ya vencido.','',
'| d (h) | Pulso: llegadas observadas/esperadas | Cola L1 fin | Cola L2 fin | Trabajo L1+L2 (h) | L1/L2 ocupados | Recuperables L1/L2 | Vencidas L1/L2 | Pendientes a H | R/N D1 H+D | Recuperación cola/trabajo desde fin pulso |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
recovery={}
for dur in durations:
 end=4+dur;dd=[x for x in d if int(x['duration_h'])==dur];snap=[x for x in ds if int(x['duration_h'])==dur and float(x['time_h'])==end]
 qs=[];w=[];l1q=[];l2q=[];occ=[];rec=[];exp=[];rec_times=[]
 for seed in sorted({int(x['seed']) for x in dd}):
  s=next(x for x in dd if int(x['seed'])==seed);q=next(x for x in snap if int(x['seed'])==seed);qs.append(int(q['queue_l1'])+int(q['queue_l2']));w.append(float(q['work_l1_h'])+float(q['work_l2_h']));l1q.append(int(q['queue_l1']));l2q.append(int(q['queue_l2']));occ.append(f'{q["active_l1"]}/{q["active_l2"]}')
  rec.append(f'{q["recoverable_l1"]}/{q["recoverable_l2"]}');exp.append(f'{q["expired_l1"]}/{q["expired_l2"]}')
  base=next(x for x in ds if int(x['duration_h'])==dur and int(x['seed'])==seed and float(x['time_h'])==4);post=sorted([x for x in ds if int(x['duration_h'])==dur and int(x['seed'])==seed and float(x['time_h'])>=end],key=lambda x:float(x['time_h']));hit=None
  for i in range(len(post)-2):
   tri=post[i:i+3]
   if all(int(x['queue_l1'])+int(x['queue_l2'])<=int(base['queue_l1'])+int(base['queue_l2']) and float(x['work_l1_h'])+float(x['work_l2_h'])<=float(base['work_l1_h'])+float(base['work_l2_h']) for x in tri):hit=float(tri[0]['time_h'])-end;break
  rec_times.append(hit)
 recovery[dur]=rec_times
 rv=[x for x in rec_times if x is not None];pulse=[int(x['pulse_arrivals']) for x in dd];expected=meta['mu_l1']*1.25*dur
 d1rn=mean(float(x['RN']) for x in e if int(x['duration_h'])==dur and x['policy']=='D1' and float(x['cutoff_h'])==48)
 rt=f'{mean(rv):.2f} h ({len(rv)}/20)' if rv else f'no recuperado en H ({len(rv)}/20)'
 lines.append(f'| {dur} | {mean(pulse):.1f}/{expected:.1f} | {mean(l1q):.1f} | {mean(l2q):.1f} | {mean(w):.1f} | {mean(int(x.split("/")[0]) for x in occ):.1f}/{mean(int(x.split("/")[1]) for x in occ):.1f} | {mean(int(x.split("/")[0]) for x in rec):.1f}/{mean(int(x.split("/")[1]) for x in rec):.1f} | {mean(int(x.split("/")[0]) for x in exp):.1f}/{mean(int(x.split("/")[1]) for x in exp):.1f} | {mean(int(x["pending_H"]) for x in dd):.1f} | {d1rn:.4f} | {rt} |')
lines+=['','En t=24 se separan L1 y L2 pendientes; durante D no entran nuevos trabajos. La recuperación se busca hasta H+D=48 h; colas vacías al corte no garantizan SLA, pues alertas pueden finalizar tarde. La tabla de D1 separa deadlines vencidos y trabajos con posibilidad inmediata de terminar puntualmente.','',
'## Comparación de políticas','',
'R/N terminal es suma de calidad esperada modelada para resoluciones puntuales L1/L2 dividida por todas las admitidas; corte 48 h. IC95 % t pareado exploratorio (19 gl), sin ajuste por las seis duraciones ni por selección de mejor fija. Mejor fija por duración = mayor media de D1/P1 y se selecciona en esta muestra.','',
'| d (h) | R/N D1 | R/N P1 | R/N HLS-B | HLS-B−D1 [IC95] | HLS-B−P1 [IC95] | Mejor fija | HLS-B−mejor fija [IC95] |','|---:|---:|---:|---:|---|---|---|---|']
summary={}
for dur in durations:
 means={p:mean(float(x['RN']) for x in e if int(x['duration_h'])==dur and x['policy']==p and float(x['cutoff_h'])==48) for p in ('D1','P1','HLS-B')};best=max(('D1','P1'),key=lambda p:means[p]);summary[dur]=means
 a=paired(e,dur,'HLS-B','D1');b=paired(e,dur,'HLS-B','P1');z=paired(e,dur,'HLS-B',best)
 lines.append(f'| {dur} | {means["D1"]:.4f} | {means["P1"]:.4f} | {means["HLS-B"]:.4f} | {a[0]:+.4f} [{a[2]:+.4f}; {a[3]:+.4f}] | {b[0]:+.4f} [{b[2]:+.4f}; {b[3]:+.4f}] | {best} | {z[0]:+.4f} [{z[2]:+.4f}; {z[3]:+.4f}] |')
lines+=['','### Cohortes de llegada','',
'Cohortes pre pulso [0,4), pulso [4,4+d) y postpulso [4+d,24); outcomes evaluados en 48 h, ponderados por admitidas. El tamaño de cohorte pulso crece con d y la cohorte de recuperación se acorta.','',
'| d (h) | Cohorte | n medio | D1 | P1 | HLS-B |','|---:|---|---:|---:|---:|---:|']
for dur in durations:
 for label in ('pre','pulse','post'):
  z={p:[x for x in c if int(x['duration_h'])==dur and x['policy']==p and x['cohort']==label] for p in ('D1','P1','HLS-B')};n=mean(int(x['admitted']) for x in z['D1']);vals={p:sum(float(x['RN'])*int(x['admitted']) for x in a)/sum(int(x['admitted']) for x in a) for p,a in z.items()};lines.append(f'| {dur} | {label} | {n:.1f} | {vals["D1"]:.4f} | {vals["P1"]:.4f} | {vals["HLS-B"]:.4f} |')
lines+=['','## Conmutación HLS-B e inercia','',
'Primer cambio D1→P1 y primer retorno P1→D1 después de acabar el pulso. Cola es L1+L2 en la marca temporal más próxima de la serie de 0,5 h. Fracción P1 durante pulso es proporción de tiempo del intervalo [4,4+d) según las épocas de modo registradas; interpolación por intervalos entre decisiones.','',
'| d (h) | Activación desde t=4 (media; episodios) | Retorno desde fin pulso (media; episodios) | Backlog L1+L2 al retorno (media) | Trabajo pendiente al retorno (h) | P1 fracción del pulso |','|---:|---|---|---:|---:|---:|']
for dur in durations:
 end=4+dur;on=[];off=[];qret=[];wret=[];frac=[]
 for seed in sorted({int(x['seed']) for x in e if int(x['duration_h'])==dur}):
  z=sorted([x for x in mo if int(x['duration_h'])==dur and int(x['seed'])==seed and x['policy']=='HLS-B'],key=lambda x:float(x['time_h']));a=next((float(x['time_h']) for x in z if x['mode']=='P1' and x['switched']=='True'),None);b=next((float(x['time_h']) for x in z if float(x['time_h'])>=end and x['mode']=='D1' and x['switched']=='True'),None)
  if a is not None:on.append(a-4)
  if b is not None:
   off.append(b-end);near=min([x for x in ts if int(x['duration_h'])==dur and int(x['seed'])==seed and x['policy']=='HLS-B'],key=lambda x:abs(float(x['time_h'])-b));qret.append(int(near['queue_l1'])+int(near['queue_l2']));wret.append(float(near['work_l1_h'])+float(near['work_l2_h']))
  pts=sorted(set([4.,end]+[float(x['time_h']) for x in z if 4<float(x['time_h'])<end]));mode='D1';now=4.;area=0.
  for x in z:
   t=float(x['time_h'])
   if t<=4:mode=x['mode'];continue
   area+=max(0.,min(t,end)-now)*(1 if mode=='P1' else 0);now=max(now,t);mode=x['mode']
  area+=max(0,end-now)*(1 if mode=='P1' else 0);frac.append(area/dur)
 lines.append(f'| {dur} | {mean(on):.2f} h ({len(on)}/20) | {mean(off):.2f} h ({len(off)}/20) | {mean(qret):.1f} | {mean(wret):.1f} | {mean(frac):.3f} |')
lines+=['','La entrada a P1 puede ocurrir después de que el pulso termine si la ventana 4 h retarda la estimación; estos casos cuentan con tiempo de activación superior al pulso y se detallan en modes.csv. El retorno a D1 no significa que la cola haya alcanzado su nivel basal. La tabla contrasta explícitamente el backlog residual al retorno.','',
'## Curvas de duración e incertidumbre','',
'IC95 % exploratorios pareados t (19 gl), sin corrección por multiplicidad. La mejor fija se elige por escenario/duración a posteriori.','',
'![Diferencias HLS-B frente a D1 y P1 según duración del pulso](figures/soc_hls_overload_duration_effect.svg)','',
'## Interpretación y respuestas','']
for dur in durations:
 m=summary[dur];a=paired(e,dur,'HLS-B','D1');b=paired(e,dur,'HLS-B','P1');best=max(('D1','P1'),key=lambda p:m[p]);z=paired(e,dur,'HLS-B',best);lines.append(f'- **{dur} h:** HLS-B−D1 {a[0]:+.4f} [{a[2]:+.4f}; {a[3]:+.4f}], HLS-B−P1 {b[0]:+.4f} [{b[2]:+.4f}; {b[3]:+.4f}], mejor fija {best}, diferencia {z[0]:+.4f}.')
lines+=['','**A. Congestión persistente:** el pulso produce cola creciente desde la menor duración en este diseño; la persistencia al final del pulso y la pendiente a H se cuantifican arriba. No se debe llamar «persistente» más allá del pulso sin usar el criterio de recuperación explícito.','',
'**B. Duración y recuperación:** el trabajo acumulado al final del pulso crece con d y el periodo restante de tasa normal disminuye. El tiempo medido de recuperación y la fracción que recupera antes de H aparecen en la tabla D1. No interpolar más allá de esos seis puntos.','',
'**C. HLS-B frente a D1:** a 2–12 h las diferencias son negativas; los IC exploratorios excluyen cero entre 4–12 h. A 16 h la diferencia es +0,0286 [0,0116; 0,0456], pero es la única celda positiva y las seis comparaciones no se ajustan por multiplicidad. No se demuestra un umbral a partir del cual la mejora sea consistente.','',
'**D. HLS-B frente a ambas fijas:** solo a 16 h HLS-B supera a la mejor fija media (P1) por +0,0209 [0,0184; 0,0234]; a 2–12 h D1 es la mejor fija y HLS-B queda debajo. El intervalo no ajusta por selección de la mejor fija ni por duración. Una sola celda no establece crossover ni duración crítica.','',
'**E. Retorno del supervisor:** comparar cola/trabajo al retorno con la recuperación D1. Si el retorno ocurre con backlog alto, es compatible con memoria del sistema y evidencia del criterio de carga observada, pero no prueba que mantener P1 fuese mejor.','',
'**F. Conclusión:** estos resultados caracterizan la inercia y un posible beneficio adaptativo en el pulso más largo ensayado, pero no establecen duración crítica. HLS-B vuelve a D1 con backlog residual importante (hasta 136 alertas / 31 h de trabajo en media), evidencia de que el retorno de modo no equivale a recuperación del sistema. P1 fija no domina todas las duraciones: obtiene R/N menor que D1 a 2–12 h y algo mayor a 16 h; HLS-B supera ambas medias solo en esa última celda. El piloto caracteriza límites dinámicos, no justifica modificar el supervisor. Los IC no tienen ajuste multiplicidad y seis duraciones implican selección. Demanda Poisson por tramos, tareas no preemptivas, colas ilimitadas y parámetros operativos hipotéticos. R/N esperado no es precisión empírica; SLA y calidad se informan separadamente. No se reutilizan semillas confirmatorias, contrafactuales individuales, ni se cambia motor/política.','',
'## Controles y reproducción','',
'Se verificaron 120 trazas manifestadas y 360 ternas de políticas: hash exógeno y admitidas comunes por duración/semilla; 720 filas H/H+D con admitidas=completadas+pendientes; D1 de cualificación y brazo D1 comparten el mismo hash y R/N terminal. Todos los cortes H=24 y H+D=48. Una repetición de episodio se puede comprobar regenerando su perfil/semilla.','',
'Ejecutables: run_soc_hls_overload_duration_d1.py, run_soc_hls_overload_duration.py, summarize_soc_hls_overload_duration.py; configuración en config/soc_hls_overload_duration.json; CSV locales en results/soc_hls_overload_duration. No se modificó el motor ni se hizo commit/push.']
(HERE/'SOC_HLS_OVERLOAD_DURATION.md').write_text('\n'.join(lines)+'\n')
# Single figure with paired-effect curves and t intervals.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="430" viewBox="0 0 820 430"><rect width="820" height="430" fill="white"/><text x="25" y="25" font-family="sans-serif" font-size="17">HLS-B − política fija en R/N terminal (media pareada, IC95 %)</text>'];x=lambda d:100+(d-2)*38
for v in (-.02,0,.02,.04,.06):
 y=340-v*4000;svg.append(f'<line x1="75" y1="{y:.1f}" x2="780" y2="{y:.1f}" stroke="{"#777" if v==0 else "#ddd"}" stroke-dasharray="{"4 3" if v==0 else "none"}"/><text x="35" y="{y+4:.1f}" font-family="sans-serif" font-size="11">{v:.2f}</text>')
for label,ctrl,color in [('D1','D1','#2166ac'),('P1','P1','#b2182b')]:
 pts=[]
 for dur in durations:
  q=paired(e,dur,'HLS-B',ctrl);y=340-q[0]*4000;lo=340-q[3]*4000;hi=340-q[2]*4000;svg.append(f'<line x1="{x(dur)}" y1="{lo:.1f}" x2="{x(dur)}" y2="{hi:.1f}" stroke="{color}" stroke-width="2"/>');svg.append(f'<circle cx="{x(dur)}" cy="{y:.1f}" r="4" fill="{color}"/>');pts.append((x(dur),y))
 svg.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="'+' '.join(f'{a},{b:.1f}' for a,b in pts)+'"/>')
for dur in durations:svg.append(f'<text x="{x(dur)-7}" y="365" font-family="sans-serif" font-size="11">{dur}</text>')
svg+=['<text x="325" y="392" font-family="sans-serif" font-size="12">Duración del pulso (h)</text>','<text x="610" y="55" fill="#2166ac" font-family="sans-serif" font-size="12">HLS-B − D1</text>','<text x="610" y="72" fill="#b2182b" font-family="sans-serif" font-size="12">HLS-B − P1</text>','<text x="25" y="418" font-family="sans-serif" font-size="10">IC t pareado exploratorio, n=20; sin corrección por selección ni multiplicidad. Mejor fija analizada en el informe.</text>','</svg>'];(HERE/'figures/soc_hls_overload_duration_effect.svg').write_text('\n'.join(svg));print('report and figure written')

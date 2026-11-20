"""Exploratory paired timing analysis and SVG curves."""
import csv,json,statistics,math
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
PILOT=ROOT/'results/soc_hls_nonstationary'; OUT=ROOT/'results/soc_hls_switching_opportunity'
def read(folder,name): return list(csv.DictReader((folder/name).open()))
pilot=read(PILOT,'episodes.csv'); rows=read(OUT,'episodes.csv'); cohorts=read(OUT,'cohorts.csv'); trans=read(OUT,'transitions.csv'); meta=json.loads((OUT/'metadata.json').read_text()); config=meta['config']
scenarios=[f'{d}h_{o}' for d in (2,4,12) for o in ('moderate_first','overload_first')]
def avg(v):return statistics.mean(v)
def paired(data,sc,a,b):
 x={int(r['seed']):float(r['R_per_admitted']) for r in data if r['scenario']==sc and r['policy']==a}; y={int(r['seed']):float(r['R_per_admitted']) for r in data if r['scenario']==sc and r['policy']==b}; assert x.keys()==y.keys(); v=[x[k]-y[k] for k in sorted(x)]; return avg(v),statistics.stdev(v),sum(q>0 for q in v),len(v)
for sc in scenarios:
 group=[r for r in rows if r['scenario']==sc]; byseed=defaultdict(list)
 for r in group: byseed[r['seed']].append(r)
 assert len(byseed)==20
 for rs in byseed.values(): assert len({r['trace_sha256'] for r in rs})==len({r['admitted'] for r in rs})==1 and all(int(r['admitted'])==int(r['completed'])+int(r['pending']) for r in rs)
names={'D1':'D1','P1':'P1','HLS-B':'HLS-B','NOMINAL-REF':'SHIFT_+0'}
lines=['# Oportunidad temporal de conmutación D1/P1','',
'**Estado:** diagnóstico exploratorio. Se comparan calendarios retrospectivos, sin selección ni validación de un supervisor nuevo. Se mantienen intactas D1, P1, HLS-B y el motor en esta fase.','',
'## Diseño','',
'Se reutilizan las seis configuraciones de alternancia: ρ=1,00/1,25, tramos de 2/4/12 h, ambos órdenes, H=24 h y D=24 h. Cada celda tiene 12 h por régimen, demanda esperada común de '+f'{meta["mu_l1"]*27:.1f} llegadas y colas iniciales vacías. Se usan 20 semillas nuevas 261210000–261210019, emparejadas entre alternativas de cada celda. El resultado es R/N terminal a 48 h; las cohortes se definen por llegada. HLS-B conserva ventana 4 h y umbrales 1,05/1,20.','',
'La referencia programada mantiene D1 durante tramos nominales moderados y P1 durante sobrecarga, con todas las fronteras desplazadas por δ. La primera frontera queda en 0 y las demás deben cumplir 0<t<24, estrictamente crecientes; los trabajos ya iniciados no se interrumpen. δ<0 usa información futura. También δ>0 usa un calendario nominal conocido y no es automáticamente desplegable. δ=0 equivale a la referencia nominal previa, evaluada aquí con otras semillas. La mejor δ se selecciona a posteriori **solo entre calendarios válidos de esta familia**; no es una cota superior.','',
'| Duración | Desplazamientos válidos (h) | Excluidos por frontera en 0 o ≥24 h |','|---:|---|---|']
for d in (2,4,12):
 good=[v for v in config['offsets_h'] if 0<d+v and (24//d-1)*d+v<24]; bad=[v for v in config['offsets_h'] if v not in good]
 lines.append(f'| {d} | {", ".join(f"{v:+g}" for v in good)} | {", ".join(f"{v:+g}" for v in bad) or "ninguno"} |')
lines += ['','## Fase 1: diferencias completas del piloto previo (n=4)','',
'Cada entrada es media pareada ± desviación estándar **entre episodios**, en unidades R/N. La dispersión no es un intervalo concluyente.','',
'| Celda | HLS-B−D1 | HLS-B−P1 | Nominal−D1 | Nominal−P1 | HLS-B−Nominal |','|---|---:|---:|---:|---:|---:|']
comparisons=[('HLS-B','D1'),('HLS-B','P1'),('NOMINAL-REF','D1'),('NOMINAL-REF','P1'),('HLS-B','NOMINAL-REF')]
for sc in scenarios:
 v=[paired(pilot,sc,a,b) for a,b in comparisons]
 lines.append('| '+sc+' | '+' | '.join(f'{m:+.4f} ± {sd:.4f}' for m,sd,_,_ in v)+' |')
lines += ['','Las diferencias de pocas milésimas son pequeñas en la escala de R/N; las de 0,02–0,04 pueden ser materialmente interesantes dentro del modelo, pero el piloto de cuatro semillas no permite fijar un umbral operativo ni inferir una ventaja reproducible.','',
'## Fase 2: curvas temporales con 20 semillas nuevas','',
'Medias R/N por δ. En la columna «mejor fija» se elige D1 o P1 por la media de esta celda; Δ es diferencia pareada media frente a esa fija. DE es la dispersión entre las 20 diferencias pareadas. La selección de δ y de fija es exploratoria, sin ajuste por multiplicidad.','',
'| Celda | δ (h) | R/N programada | Δ vs mejor fija | DE Δ | Episodios Δ>0 |','|---|---:|---:|---:|---:|---:|']
stats={}
for sc in scenarios:
 fixed={p:avg(float(r['R_per_admitted']) for r in rows if r['scenario']==sc and r['policy']==p) for p in ('D1','P1')}; best=max(fixed,key=fixed.get); stats[sc]={'best':best,'fixed':fixed}
 for off in config['offsets_h']:
  label=f'SHIFT_{off:+g}'
  if not any(r['scenario']==sc and r['policy']==label for r in rows):continue
  m=avg(float(r['R_per_admitted']) for r in rows if r['scenario']==sc and r['policy']==label); delta,sd,pos,n=paired(rows,sc,label,best); stats[sc][label]=(m,delta,sd,pos)
  lines.append(f'| {sc} | {off:+g} | {m:.4f} | {delta:+.4f} | {sd:.4f} | {pos}/{n} |')
lines += ['','### Comparadores emparejados de la muestra nueva','',
'| Celda | D1 | P1 | HLS-B | Nominal δ=0 | HLS-B−D1 ± DE | HLS-B−P1 ± DE | Nominal−HLS-B ± DE |','|---|---:|---:|---:|---:|---:|---:|---:|']
for sc in scenarios:
 means={p:avg(float(r['R_per_admitted']) for r in rows if r['scenario']==sc and r['policy']==p) for p in ('D1','P1','HLS-B','SHIFT_+0')}
 v=[paired(rows,sc,a,b) for a,b in [('HLS-B','D1'),('HLS-B','P1'),('SHIFT_+0','HLS-B')]]
 lines.append(f'| {sc} | {means["D1"]:.4f} | {means["P1"]:.4f} | {means["HLS-B"]:.4f} | {means["SHIFT_+0"]:.4f} | '+' | '.join(f'{m:+.4f} ± {sd:.4f}' for m,sd,_,_ in v)+' |')
lines += ['','### Cohortes de llegada','',
'R/N ponderado por alertas admitidas de cada régimen de llegada, agregado sobre las 20 semillas. Las tablas completas por tramo, semilla y política quedan en `cohorts.csv`.','',
'| Celda | Régimen | D1 | P1 | HLS-B | δ=0 | Mejor δ retrospectiva |','|---|---|---:|---:|---:|---:|---:|']
for sc in scenarios:
 candidate=max((k for k in stats[sc] if k.startswith('SHIFT_')),key=lambda k:stats[sc][k][0])
 for mode in ('D1','P1'):
  vals=[]
  for p in ('D1','P1','HLS-B','SHIFT_+0',candidate):
   rs=[r for r in cohorts if r['scenario']==sc and r['policy']==p and r['regime']==mode]; vals.append(sum(float(r['R_per_admitted'])*int(r['admitted']) for r in rs)/sum(int(r['admitted']) for r in rs))
  lines.append(f'| {sc} | {"ρ=1,00" if mode=="D1" else "ρ=1,25"} | '+' | '.join(f'{v:.4f}' for v in vals)+' |')
lines += ['','## Colas, plazos y sensibilidad','',
'La cola L1 al cambio nominal contiene alertas anteriores aún sin iniciar; el trabajo es la suma de servicios L1 nominales de esa cola. «Holgura ≤ servicio» incluye las ya vencidas; es un indicador aproximado de presión de plazos, no una predicción individual con servicio específico de analista ni L2. Se registra también la cola L2 y los recuentos/trabajo por clase en `transitions.csv`. El plazo de cada alerta se conserva al desplazar conmutaciones; las cohortes pueden terminar en otro régimen.','',
'| Celda | Cola L1 al cambio, HLS-B | Trabajo L1, HLS-B (h) | Vencidas en cola | Holgura ≤ servicio nominal | Cola L2 | Mejor δ retrospectiva | Ganancia vs mejor fija | Ganancia vs HLS-B |','|---|---:|---:|---:|---:|---:|---:|---:|']
for sc in scenarios:
 rs=[r for r in trans if r['scenario']==sc and r['policy']=='HLS-B']; q=avg(int(r['queue_l1']) for r in rs); w=avg(sum(json.loads(r['work_l1_h_by_class']).values()) for r in rs); q2=avg(int(r['queue_l2']) for r in rs); overdue=avg(int(r['overdue_l1']) for r in rs); tight=avg(int(r['tight_l1']) for r in rs)
 candidate=max((k for k in stats[sc] if k.startswith('SHIFT_')),key=lambda k:stats[sc][k][0]); m,delta,sd,pos=stats[sc][candidate]; hb=avg(float(r['R_per_admitted']) for r in rows if r['scenario']==sc and r['policy']=='HLS-B')
 lines.append(f'| {sc} | {q:.1f} | {w:.1f} | {overdue:.1f} | {tight:.1f} | {q2:.1f} | {candidate[6:]} h | {delta:+.4f} | {m-hb:+.4f} |')
lines += ['','En estas fronteras HLS-B conserva cola sustancial, pero el diagnóstico nominal contabiliza 0 alertas ya vencidas o con holgura menor que un servicio L1 nominal. Por ello, los snapshots no apoyan explicar el patrón mediante plazos ya perdidos en el instante de cambio. Siguen siendo posibles efectos posteriores de espera, servicio heterogéneo y terminación L2.','',
'El calendario con mejor media se selecciona con estas mismas 20 semillas y su ganancia está sesgada al alza. La tabla permite comparar cola acumulada, longitud del tramo y sensibilidad de R/N al desplazamiento; la asociación no identifica causalmente el papel separado de la cola o los deadlines. Cambiar δ modifica decisiones, servicios, cola posterior y la cohorte afectada.','',
'## Interpretación y límites','']
for sc in scenarios:
 v=stats[sc]; candidate=max((k for k in v if k.startswith('SHIFT_')),key=lambda k:v[k][0]); immediate=v['SHIFT_+0'][0]; later=[(k,z) for k,z in v.items() if k.startswith('SHIFT_+') and k!='SHIFT_+0']; later_best=max(later,key=lambda x:x[1][0]) if later else None
 lines.append(f'- **{sc}:** máximo retrospectivo {candidate[6:]} h (Δ {v[candidate][1]:+.4f} frente a {v["best"]}); δ=0 da {immediate:.4f}'+(f'; mejor retraso {later_best[0][6:]} h da {later_best[1][0]:.4f}.' if later_best else '.'))
lines += ['','La mejor δ es posterior en cuatro celdas y anterior en dos; nunca coincide exactamente con el cambio nominal. Las ganancias de esos máximos frente a la mejor fija van de +0,0004 a +0,0166, con solo 7–13 de 20 diferencias positivas según la celda. No aparece una región temporal que gane de forma consistente a ambas fijas. En las seis celdas HLS-B supera en media incluso al máximo programado, por +0,0006 a +0,0070; esta comparación favorece artificialmente al calendario porque su máximo fue seleccionado con los mismos datos. Las curvas de 12 h muestran una mejora con el retraso, especialmente tras sobrecarga inicial (δ=0: 0,6238; δ=+4: 0,6352), pero la cola L1 media en la frontera es 108,7 alertas y 24,6 h de trabajo en HLS-B. Esta coincidencia es compatible con dependencia de la historia; no demuestra que la cola cause la mejora.','',
'Esta búsqueda múltiple no valida la mejor alternativa. Las desviaciones entre episodios y la consistencia de signos informan la precisión descriptiva; no se hicieron pruebas confirmatorias ni se reajustó HLS-B. No hay coste de información futura, observación ni cambio de modo; el modelo mantiene colas ilimitadas y parámetros humanos/IA hipotéticos. Las referencias adelantadas y las posteriores usan el calendario nominal. Los resultados no miden un SOC real ni validan un nuevo supervisor.','',
'**Conclusión — D, evidencia aún insuficiente para atribuir un mecanismo definitivo.** El calendario temporal restringido ofrece mejoras pequeñas y poco consistentes frente a las fijas (máximo seleccionado +0,0166; 13/20 episodios positivos en esa celda), y no revela margen medio sin explotar respecto a HLS-B en ninguna celda. El máximo se desplaza con duración y orden, por lo que hay indicios descriptivos de dependencia de historia, pero esta matriz no aísla cola, plazos y momento de conmutación. Una futura política tendría que usar estado observable y demostrar ventaja en semillas independientes; aquí no se selecciona ninguna.','',
'## Reproducción','',
'`config/soc_hls_switching_opportunity.json`, `run_soc_hls_switching_opportunity.py` y `summarize_soc_hls_switching_opportunity.py` generan los CSV completos y esta figura. Se verificaron 120 parejas escenario–semilla con la misma traza y número de admitidas en todas las alternativas válidas, además de conservación admitidas=completadas+pendientes. No hubo commit ni push.']
(HERE/'SOC_HLS_SWITCHING_OPPORTUNITY.md').write_text('\n'.join(lines)+'\n')
W,H=1000,590; svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>','<text x="30" y="28" font-family="sans-serif" font-size="18">R/N terminal frente al desplazamiento de todas las fronteras</text>']
colors={'moderate_first':'#2166ac','overload_first':'#b2182b'}
for j,d in enumerate((2,4,12)):
 top=55+j*175; svg.append(f'<text x="30" y="{top+8}" font-family="sans-serif" font-size="15">Tramos de {d} h</text>')
 def X(off):return 160+(off+2)*105
 def Y(v):return top+135-(v-.60)*850
 for val in (.62,.64,.66):
  y=Y(val);svg.append(f'<line x1="145" y1="{y:.1f}" x2="820" y2="{y:.1f}" stroke="#e4e4e4"/><text x="95" y="{y+4:.1f}" font-family="sans-serif" font-size="11">{val:.2f}</text>')
 for order in ('moderate_first','overload_first'):
  sc=f'{d}h_{order}'; pts=[]
  for off in config['offsets_h']:
   label=f'SHIFT_{off:+g}'
   if label in stats[sc]:pts.append((X(off),Y(stats[sc][label][0]),off))
  color=colors[order]; svg.append('<polyline fill="none" stroke="'+color+'" stroke-width="2" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y,_ in pts)+'"/>')
  for x,y,off in pts:svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
 svg.append(f'<line x1="{X(0)}" y1="{top+18}" x2="{X(0)}" y2="{top+145}" stroke="#999" stroke-dasharray="3 3"/>')
 for off in config['offsets_h']:svg.append(f'<text x="{X(off)-9}" y="{top+160}" font-family="sans-serif" font-size="11">{off:+g}</text>')
svg += ['<text x="740" y="72" fill="#2166ac" font-family="sans-serif" font-size="13">Moderada primero</text>','<text x="740" y="91" fill="#b2182b" font-family="sans-serif" font-size="13">Sobrecarga primero</text>','<text x="30" y="578" font-family="sans-serif" font-size="11">Medias exploratorias de 20 semillas; puntos omitidos = calendario inválido. Eje vertical común: R/N.</text>','</svg>']
(HERE/'figures/soc_hls_switching_opportunity.svg').write_text('\n'.join(svg))
print('report and figure saved',len(rows),'episode rows')

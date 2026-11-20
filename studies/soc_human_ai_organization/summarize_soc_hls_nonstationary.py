"""Summarize the fixed development matrix and render a compact figure."""
import csv, json, statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent; OUT=ROOT/'results/soc_hls_nonstationary'
def read(name): return list(csv.DictReader((OUT/name).open()))
e=read('episodes.csv'); c=read('cohorts.csv'); t=read('transitions.csv'); h=read('modes.csv'); meta=json.loads((OUT/'metadata.json').read_text()); cfg=meta['config']
assert len(e)==96 and len({(x['scenario'],x['seed'],x['policy']) for x in e})==96
for sc in {x['scenario'] for x in e}:
 for seed in {x['seed'] for x in e}:
  group=[x for x in e if x['scenario']==sc and x['seed']==seed]
  assert len(group)==4 and len({x['trace_sha256'] for x in group})==1 and len({x['admitted'] for x in group})==1
  assert all(int(x['pending'])==int(x['admitted'])-int(x['completed']) for x in group)
def avg(xs): return statistics.mean(xs) if xs else float('nan')
scenarios=[f'{d}h_{o}' for d in (2,4,12) for o in ('moderate_first','overload_first')]
lookup={(x['scenario'],int(x['seed']),x['policy']):float(x['R_per_admitted']) for x in e}; seeds=range(cfg['seed_base'],cfg['seed_base']+cfg['seed_count'])
lines=['# Adaptación D1/P1 en regímenes variables — piloto de desarrollo','',
'**Estado:** exploratorio, 4 semillas por celda. Ninguna elección ni reajuste posterior de duraciones o umbrales. No es validación confirmatoria.','',
'## Hipótesis y diseño','',
'H1: la conmutación puede superar a ambas políticas fijas si el régimen dura lo suficiente. H2: el retraso de HLS-B y la cola heredada pueden impedirlo. H3: aun con régimen nominal conocido, la conmutación puede perder por efectos de trayectoria y calidad modelada.','',
'Se comparan D1, P1, HLS-B congelada (ventana 4 h; histéresis 1,05/1,20) y NOMINAL-REF. Esta última aplica D1 en ρ=1,00 y P1 en ρ=1,25 al siguiente despacho tras cada frontera conocida retrospectivamente. No es implementable con información disponible ni una cota superior matemática. Los trabajos iniciados continúan, sin preempción. Los cuatro brazos parten de colas vacías y comparten alertas, IA hipotética, clases, dificultad, plazos y semilla de despacho.','',
f'H=24 h de admisión y D=24 h de drenaje, corte terminal 48 h para todas las celdas. Cada escenario tiene 12 h en ρ=1,00 y 12 h en ρ=1,25; capacidad L1 {meta["mu_l1"]:.3f}/h y llegadas esperadas comunes {meta["mu_l1"]*27:.1f}. Hay 4 semillas nuevas {cfg["seed_base"]}–{cfg["seed_base"]+3}, independientes de las campañas confirmatorias. R/N suma la probabilidad modelada de corrección de resoluciones terminales puntuales, dividida por todas las admitidas; una escalada finaliza en L2.','',
'## Matriz prefijada','',
'| Duración por régimen | Orden | Tramos de 24 h | Fronteras de cambio (h) |','|---:|---|---:|---|']
for sc in scenarios:
 d=int(sc.split('h')[0]); order=sc.split('h_')[1]; lines.append(f'| {d} h | {"moderada→sobrecarga" if order=="moderate_first" else "sobrecarga→moderada"} | {24//d} | {", ".join(str(i*d) for i in range(1,24//d))} |')
lines += ['','## Resultados terminales','',
'Medias de cuatro episodios por celda. Δ compara HLS-B con la **mejor política fija de esa celda**, elegida por su media; las diferencias siguen emparejadas por semilla. IC95 % exploratorio t bilateral con 3 grados de libertad; seis comparaciones sin ajuste multiplicidad.','',
'| Duración | Orden | D1 | P1 | HLS-B | Nominal | Mejor fija | Δ HLS-B | IC95 % Δ |','|---:|---|---:|---:|---:|---:|---|---:|---|']
summary=[]
for sc in scenarios:
 vals={p:[lookup[(sc,s,p)] for s in seeds] for p in ('D1','P1','HLS-B','NOMINAL-REF')}; means={p:avg(v) for p,v in vals.items()}; best=max(('D1','P1'),key=lambda p:means[p]); diffs=[a-b for a,b in zip(vals['HLS-B'],vals[best])]; delta=avg(diffs); half=3.182446*statistics.stdev(diffs)/2
 d=int(sc.split('h')[0]); order='moderada primero' if 'moderate_first' in sc else 'sobrecarga primero'
 summary.append((sc,d,order,means,best,delta,delta-half,delta+half))
 lines.append(f'| {d} h | {order} | {means["D1"]:.4f} | {means["P1"]:.4f} | {means["HLS-B"]:.4f} | {means["NOMINAL-REF"]:.4f} | {best} | {delta:+.4f} | [{delta-half:+.4f}; {delta+half:+.4f}] |')
lines += ['','## Cohortes, colas y detección','',
'R/N por cohorte de llegada (cada tramo tiene su propio denominador de admitidas), agregado sobre los cuatro episodios. La cola en una frontera cuenta alertas L1 admitidas antes de esa frontera y aún sin iniciar L1; el trabajo por clase usa horas de servicio L1 nominal. La cola L2 cuenta escaladas que terminaron L1 y aún no iniciaron L2.','',
'| Duración | Orden | Régimen de llegada | D1 | P1 | HLS-B | Nominal |','|---:|---|---|---:|---:|---:|---:|']
for sc in scenarios:
 d=int(sc.split('h')[0]); order='moderada' if 'moderate_first' in sc else 'sobrecarga';
 for mode in ('D1','P1'):
  z={p:[x for x in c if x['scenario']==sc and x['policy']==p and x['regime']==mode] for p in ('D1','P1','HLS-B','NOMINAL-REF')}
  v={p:sum(float(x['R_per_admitted'])*int(x['admitted']) for x in zz)/sum(int(x['admitted']) for x in zz) for p,zz in z.items()}
  lines.append(f'| {d} h | {order} primero | {"ρ=1,00" if mode=="D1" else "ρ=1,25"} | {v["D1"]:.4f} | {v["P1"]:.4f} | {v["HLS-B"]:.4f} | {v["NOMINAL-REF"]:.4f} |')
lines += ['','| Duración | Orden | Cola L1 en cambios, HLS-B | Trabajo L1 pendiente | Cola L2 | Retraso hasta decisión concordante HLS-B | Referencia |','|---:|---|---:|---:|---:|---:|---:|']
for sc in scenarios:
 d=int(sc.split('h')[0]); order='moderada' if 'moderate_first' in sc else 'sobrecarga'; z=[x for x in t if x['scenario']==sc and x['policy']=='HLS-B']; q=avg([int(x['queue_l1']) for x in z]); w=avg([sum(json.loads(x['work_l1_h_by_class']).values()) for x in z]); q2=avg([int(x['queue_l2']) for x in z]); delays=[float(x['delay_h']) for x in z if x['delay_h']!='']; r=[float(x['delay_h']) for x in t if x['scenario']==sc and x['policy']=='NOMINAL-REF' and x['delay_h']!='']; lines.append(f'| {d} h | {order} primero | {q:.1f} | {w:.1f} h | {q2:.1f} | {avg(delays):.2f} h ({len(delays)}/{len(z)}) | {avg(r):.2f} h |')
lines += ['','Las marcas de cambio de demanda, decisiones de HLS-B y referencia, y estados de cola por frontera y clase están en `transitions.csv` y `modes.csv`. El retraso tabulado mide la primera **decisión** del modo concordante después de la frontera, no una detección continua; cuando el modo ya concordaba al cambiar la tasa, puede ser próximo a cero. Los casos sin decisión concordante quedan fuera de esa media y aparecen en el denominador. La referencia cambia en el primer despacho posterior, que puede no coincidir exactamente con la frontera.','',
'## Interpretación','']
positive=[x for x in summary if x[5]>0]; clear=[x for x in summary if x[6]>0]
lines.append(f'HLS-B supera descriptivamente a la mejor fija en {len(positive)}/6 celdas; ningún IC exploratorio de una **ventaja positiva** excluye cero. En las dos celdas de 2 h, el IC de la diferencia negativa sí excluye cero, sin ajuste multiplicidad. Los seis resultados figuran arriba, incluidos los negativos. Las diferencias de orden son descriptivas y están entrelazadas con la cola y la realización exógena. NOMINAL-REF supera a la mejor fija en {sum(x[3]["NOMINAL-REF"]>x[3][x[4]] for x in summary)}/6 celdas: conocer el régimen no garantiza mejorar el episodio.')
for d in (2,4,12):
 a,b=[x for x in summary if x[1]==d]
 lines.append(f'Con tramos de {d} h, la diferencia HLS-B−mejor fija cambia {b[5]-a[5]:+.4f} al situar primero la sobrecarga ({a[5]:+.4f}→{b[5]:+.4f}); este contraste de orden no aísla un mecanismo causal.')
lines += ['','La asociación entre duración, retraso y rendimiento se observa conjuntamente, pero no identifica un efecto causal del retraso: también cambian número de transiciones, estado de cola, orden y composición de cohortes. Los registros permiten examinar cada frontera; este piloto no interviene de forma aislada sobre cola o latencia.','',
'## Limitaciones y conclusión','',
'Cuatro semillas por celda y seis comparaciones exploratorias dan poca precisión; la mejor fija se selecciona con las mismas cuatro observaciones y sus IC no corrigen esa selección ni multiplicidad. Las colas son ilimitadas; roster, servicio, calidad, IA, plazos y escalado son sintéticos. El drenaje de 24 h es común y las pendientes se conservan en `episodes.csv`. La simulación separa L1 y L2 según el motor existente. No se extrapola a GMV-CERT ni se usa para reajustar HLS-B.','',
'**Conclusión:** el piloto ofrece indicios positivos limitados de adaptación en algunas duraciones, pero no respalda una regla monótona «cuanto más largo, mejor». La referencia nominal tampoco establece una oportunidad universal. Con estas cuatro semillas, las explicaciones 1–3 no se distinguen de manera robusta; corresponde la explicación **4**. No se ha ejecutado validación confirmatoria.','',
'## Reproducción','',
'`config/soc_hls_nonstationary.json`, `run_soc_hls_nonstationary.py` y `summarize_soc_hls_nonstationary.py` fijan el diseño y el análisis. Los CSV completos y `metadata.json` están en `results/soc_hls_nonstationary/` (ignorado por Git); la figura versionada está en `figures/soc_hls_nonstationary_effect.svg`. Se verificaron 24 parejas escenario–semilla con el mismo hash, admitidas y conservación de completadas+pendientes entre cuatro políticas.']
(HERE/'SOC_HLS_NONSTATIONARY_REGIMES.md').write_text('\n'.join(lines)+'\n')
# SVG with one panel per order; points are paired effects vs the cell's best fixed policy.
colors={'moderate_first':'#2166ac','overload_first':'#b2182b'}; svg=['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="340" viewBox="0 0 850 340">','<rect width="850" height="340" fill="white"/>','<text x="30" y="28" font-family="sans-serif" font-size="18">HLS-B − mejor política fija: R/N terminal</text>']
def xx(v): return 400+v*5000
svg.append(f'<line x1="{xx(0)}" y1="55" x2="{xx(0)}" y2="285" stroke="#777" stroke-dasharray="4 3"/>')
for i,(sc,d,order,means,best,delta,lo,hi) in enumerate(summary):
 y=75+i*38; col=colors['moderate_first' if 'moderate_first' in sc else 'overload_first']; svg += [f'<text x="30" y="{y+5}" font-family="sans-serif" font-size="13">{d} h, {order}</text>',f'<line x1="{xx(lo):.1f}" y1="{y}" x2="{xx(hi):.1f}" y2="{y}" stroke="{col}" stroke-width="2"/>',f'<circle cx="{xx(delta):.1f}" cy="{y}" r="5" fill="{col}"/>',f'<text x="720" y="{y+5}" font-family="sans-serif" font-size="12">{delta:+.4f}</text>']
svg += ['<text x="30" y="322" font-family="sans-serif" font-size="12">IC95 % exploratorio pareado; n=4 por celda. Mejor fija según media de la celda.</text>','</svg>']
(HERE/'figures/soc_hls_nonstationary_effect.svg').write_text('\n'.join(svg))
print('report and figure saved; clear cells',len(clear))

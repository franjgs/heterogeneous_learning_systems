import csv,json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;O=R/'results/soc_hls_realistic_dynamics'
def rd(n):return list(csv.DictReader((O/n).open()))
d=rd('d1_diagnostic.csv'); ds=rd('d1_timeseries.csv');e=rd('episodes.csv');c=rd('cohorts.csv');ts=rd('timeseries.csv');m=rd('modes.csv');meta=json.loads((O/'metadata.json').read_text());cfg=meta['config'];profiles=[x['name'] for x in cfg['profiles']];pols=('D1','P1','HLS-B');mean=statistics.mean
assert len(d)==24 and len(e)==144 and len(ts)==5256
for p in profiles:
 for s in {x['seed'] for x in e if x['profile']==p}:
  z=[x for x in e if x['profile']==p and x['seed']==s];assert len(z)==6 and len({x['trace_sha256'] for x in z})==len({x['admitted'] for x in z})==1
  assert all(int(x['admitted'])==int(x['completed'])+int(x['pending']) for x in z)
  a=next(x for x in d if x['profile']==p and x['seed']==s);b=next(x for x in z if x['policy']=='D1' and float(x['cutoff_h'])==72);assert abs(float(a['rn'])-float(b['rn']))<1e-12
lines=['# Dinámica realista de demanda y respuesta del SOC','',
'Estado: piloto de desarrollo, ocho semillas por escenario. Estadísticas de demanda tomadas de la documentación agregada autorizada; el CSV restringido no estuvo disponible en la ruta de trabajo y no se leyó ni reprodujo. Resultados sintéticos, no medición de operación real.','',
'## Dinámica representada','',
'El motor ya modela llegadas temporizadas, colas L1/L2, asignación no preemptiva, elegibilidad, servicio por clase/analista, escalado L1→L2, deadlines y drenaje H+D. Una tasa temporal superior a la capacidad genera cola; al bajar la tasa, el trabajo heredado puede descargarse. No añadimos turnos, pausas, reprocesamiento, abandono ni límite de cola. D1, P1 y HLS-B no se modificaron.','',
'## Demanda y supuestos','',
'El snapshot SOCTRA documentado contiene 214.739 IDs y 993 fechas: media 216,3 registros/día, p95 379, máximo 574, CV diario 0,414, Fano 37,05, autocorrelación diaria lag-1 0,525 y CV de interllegadas 1,604. Esto apoya variabilidad y picos; no mide trabajo activo ni horas de ráfaga. El timestamp es timezone-naive y su semántica no está validada; no inferimos ciclos diarios ni duración de ráfagas.','',
'Se toma 574/216,3=2,654 como multiplicador observado de pico diario, no como perfil horario observado. ρ normal=0,50 y recuperación recurrente=0,85 son supuestos. ρ pico=1,327 conserva el multiplicador respecto a 0,50. La media SOCTRA equivale a 9,01 registros/h; la capacidad fluida sintética L1 es 28,42/h (ρ≈0,317), por lo que mantener la tasa absoluta observada no produciría sobrecarga en este roster. La elevación a ρ=0,50 es un estrés de desarrollo, no calibración realista absoluta. Roster 6 L1/3 L2, servicios, competencias, elegibilidad y routing se heredan de la configuración confirmatoria HLS-B y siguen siendo hipotéticos.','',
'## Escenarios prefijados','',
'En todos: H=36 h, D=36 h, semillas 261220000–261220007; inicia con seis horas normales para calentar la cola. Las llegadas esperadas integran tasa × duración, y son iguales entre políticas dentro de cada escenario/semilla, aunque Poisson produce realizaciones distintas.','',
'| Escenario | Perfil temporal (horas desde inicio) | Llegadas esperadas | Justificación |','|---|---|---:|---|']
for x in cfg['profiles']:
 total=sum((b-a)*rho for a,b,rho in x['segments'])*meta['mu_l1'];desc='; '.join(f'{a:g}–{b:g} h: ρ={rho:g}' for a,b,rho in x['segments'])
 why={'brief_overload_recovery':'pulso de 4 h y 26 h de recuperación asumida','sustained_overload_recovery':'pulso de 12 h y 18 h de recuperación asumida','recurrent_incomplete_recovery':'tres pulsos de 2 h; intervalos a ρ=0,85 asumidos incompletos'}[x['name']]
 lines.append(f'| {x["name"]} | {desc} | {total:.1f} | {why} |')
lines+=['','Las duraciones son contrastes experimentales; no se calibran de timestamps SOCTRA.','',
'## Diagnóstico D1 previo a la comparación','',
'Medias de ocho trayectorias. Cola al fin del pulso cuenta alertas aún sin iniciar L1; ocupación es la fracción de analistas L1 ocupados en ese instante.','',
'| Escenario | Fin pulso (h) | Cola L1 | Trabajo pendiente L1 (h) | Ocupación L1 | Máximo cola L1 en H | Pendientes H | Pendientes H+D | R/N terminal | SLA |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
ends={'brief_overload_recovery':10,'sustained_overload_recovery':18,'recurrent_incomplete_recovery':24}
for p in profiles:
 z=[x for x in d if x['profile']==p];at=[x for x in ds if x['profile']==p and int(x['time_h'])==ends[p]];maxq=[max(int(x['queue_l1']) for x in ds if x['profile']==p and x['seed']==s) for s in {x['seed'] for x in z}]
 lines.append(f'| {p} | {ends[p]} | {mean(int(x["queue_l1"]) for x in at):.1f} | {mean(float(x["pending_work_l1_h"]) for x in at):.1f} | {mean(float(x["l1_occupancy"]) for x in at):.3f} | {mean(maxq):.1f} | {mean(int(x["pending_H"]) for x in z):.1f} | {mean(int(x["backlog_HD"]) for x in z):.1f} | {mean(float(x["rn"]) for x in z):.4f} | {mean(float(x["sla"]) for x in z):.4f} |')
lines+=['','A y B permiten observar descarga durante H. C termina el último pulso al cerrar admisión; su recuperación solo se observa en el drenaje.','',
'## Comparación D1/P1/HLS-B','',
'Ocho semillas emparejadas por perfil; R/N y SLA terminales en H+D=72 h.','',
'| Escenario | D1 R/N | P1 R/N | HLS-B R/N | HLS-B−D1 | HLS-B−P1 | SLA D1/P1/HLS-B |','|---|---:|---:|---:|---:|---:|---|']
for p in profiles:
 v={q:[x for x in e if x['profile']==p and x['policy']==q and float(x['cutoff_h'])==72] for q in pols};r={q:mean(float(x['rn']) for x in a) for q,a in v.items()};s={q:mean(float(x['sla']) for x in a) for q,a in v.items()}
 lines.append(f'| {p} | {r["D1"]:.4f} | {r["P1"]:.4f} | {r["HLS-B"]:.4f} | {r["HLS-B"]-r["D1"]:+.4f} | {r["HLS-B"]-r["P1"]:+.4f} | {s["D1"]:.3f}/{s["P1"]:.3f}/{s["HLS-B"]:.3f} |')
lines+=['','### Cohortes de llegada','',
'R/N terminal por cohorte definida por llegada, ponderado por admitidas; cada segmento conserva denominador y CSV incluye conteos.','',
'| Perfil | Segmento | ρ | D1 | P1 | HLS-B |','|---|---:|---:|---:|---:|---:|']
for p in profiles:
 for i in sorted({int(x['segment']) for x in c if x['profile']==p}):
  z={q:[x for x in c if x['profile']==p and int(x['segment'])==i and x['policy']==q] for q in pols};rho=float(z['D1'][0]['rho']);val={q:sum(float(x['rn'])*int(x['admitted']) for x in a)/sum(int(x['admitted']) for x in a) for q,a in z.items()}
  lines.append(f'| {p} | {i} | {rho:.2f} | {val["D1"]:.4f} | {val["P1"]:.4f} | {val["HLS-B"]:.4f} |')
lines+=['','## Recuperación y conmutación','',
'HLS-B activa con estimación de llegadas en ventana causal de 4 h y umbrales congelados 1,05/1,20. La conmutación no marca por sí misma recuperación de cola. `timeseries.csv` da cola L1/L2, trabajo L1, ocupación, recuperables/vencidas y modo cada hora y semilla. `modes.csv` conserva tiempos de conmutación. `episodes.csv` conserva completadas, pendientes, calidad entre completadas y tiempo medio de finalización.','',
'| Escenario | Fin pulso (h) | Primera P1 HLS-B | Retorno D1 tras pulso | Recuperación D1 cola+trabajo | Prestaciones |','|---|---:|---:|---:|---:|---|']
for p in profiles:
 end=ends[p]; starts=[float(x['time_h']) for x in m if x['profile']==p and x['policy']=='HLS-B' and x['mode']=='P1' and x['switched']=='True']; returns=[]; rec=[]
 for seed in {int(x['seed']) for x in d if x['profile']==p}:
  z=sorted([x for x in m if x['profile']==p and int(x['seed'])==seed and x['policy']=='HLS-B'],key=lambda x:float(x['time_h']))
  r=next((float(x['time_h']) for x in z if float(x['time_h'])>=end and x['mode']=='D1' and x['switched']=='True'),None)
  if r is not None:returns.append(r-end)
  q=sorted([x for x in ds if x['profile']==p and int(x['seed'])==seed],key=lambda x:int(x['time_h']));base=next(x for x in q if int(x['time_h'])==6)
  hit=next((int(x['time_h'])-end for x in q if int(x['time_h'])>=end and int(x['queue_l1'])<=int(base['queue_l1']) and float(x['pending_work_l1_h'])<=float(base['pending_work_l1_h'])),None)
  if hit is not None:rec.append(hit)
 lines.append(f'| {p} | {end} | {mean(starts):.2f} h ({len(starts)}/8) | {mean(returns):.2f} h ({len(returns)}/8) | {mean(rec):.2f} h ({len(rec)}/8) | R/N de cohortes terminal arriba |')
lines+=['','Recuperación de cola significa cola y trabajo L1 ambos al nivel de las 6 h, antes del primer pulso. No implica recuperar mezcla de tareas ni cumplimiento de plazos. La prestación se describe por R/N terminal de cohorte porque no hay una medida observada de calidad por hora.','',
'![Evolución de cola y trabajo pendiente L1 bajo D1](figures/soc_hls_realistic_dynamics.svg)','',
'## Interpretación y límites','',
'Comparar tiempos de pulso, máximos de cola D1 y R/N por perfil separa sobrecarga breve, sostenida y recurrente con memoria. El corte C mide congestión residual a H y descarga en D. Ocho semillas son un piloto exploratorio; diferencias de R/N no prueban una ventaja causal general. La carga normal absoluta y todas las duraciones son supuestos. Estadísticas diarias de timestamps no indican duración de trabajo humano, periodo intradía ni servicio. Los resultados no extrapolan a GMV-CERT.','',
'La conclusión sobre respuesta de HLS-B debe distinguir cuándo activa/retorna del estado efectivo de cola y prestaciones. R/N puede mejorar o empeorar por calidad esperada y puntualidad; SLA, calidad entre completadas, espera y pendientes se reportan separadamente en datos completos. No se modifica ni reajusta HLS-B. No se ejecutó confirmación ni commit/push.','',
'## Reproducción','',
'Configuración: config/soc_hls_realistic_dynamics.json. Ejecutar primero run_soc_hls_realistic_d1_diagnostic.py; luego run_soc_hls_realistic_dynamics.py y summarize_soc_hls_realistic_dynamics.py. CSV agregados por episodio/hora en results/soc_hls_realistic_dynamics (local ignorado). Se verifican hashes y admitidas compartidas, conservación completadas+pendientes y coincidencia exacta del D1 de diagnóstico con el brazo D1 del piloto.']
(H/'SOC_HLS_REALISTIC_DYNAMICS.md').write_text('\n'.join(lines)+'\n')
colors={'brief_overload_recovery':'#2166ac','sustained_overload_recovery':'#b2182b','recurrent_incomplete_recovery':'#1b7837'};svg=['<svg xmlns="http://www.w3.org/2000/svg" width="850" height="440" viewBox="0 0 850 440"><rect width="850" height="440" fill="white"/><text x="25" y="25" font-family="sans-serif" font-size="17">D1: cola L1 y trabajo pendiente a lo largo del episodio</text>']
for i,p in enumerate(profiles):
 top=45+i*125;z=[x for x in ds if x['profile']==p];maxq=max(1,max(float(x['queue_l1']) for x in z));maxw=max(1,max(float(x['pending_work_l1_h']) for x in z));svg.append(f'<text x="15" y="{top+9}" font-family="sans-serif" font-size="12">{p}</text>')
 for a,b,rho in next(x['segments'] for x in cfg['profiles'] if x['name']==p):svg.append(f'<rect x="{95+a*18}" y="{top+10}" width="{(b-a)*18}" height="95" fill="{"#f5d5cf" if rho>1 else "#edf1f5"}"/>')
 q=[];w=[]
 for t in range(37):
  a=[x for x in z if int(x['time_h'])==t];q.append((95+t*18,top+95-mean(float(x['queue_l1']) for x in a)/maxq*75));w.append((95+t*18,top+95-mean(float(x['pending_work_l1_h']) for x in a)/maxw*75))
 svg.append(f'<polyline fill="none" stroke="{colors[p]}" stroke-width="2" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in q)+'"/>');svg.append(f'<polyline fill="none" stroke="{colors[p]}" stroke-width="2" stroke-dasharray="5 3" points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in w)+'"/>')
svg+=['<text x="97" y="432" font-family="sans-serif" font-size="11">Línea sólida: cola normalizada dentro del perfil; discontinua: trabajo normalizado. Fondo rosado: sobrecarga. Tiempo (h).</text>','</svg>'];(H/'figures/soc_hls_realistic_dynamics.svg').write_text('\n'.join(svg));print('wrote report and figure')

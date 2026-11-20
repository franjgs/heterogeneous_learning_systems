import csv,json,statistics,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;CORE=ROOT/'results/soc_hls_operating_regions';SENS=ROOT/'results/soc_hls_operating_sensitivity'
def rd(path,n):return list(csv.DictReader((path/n).open()))
e=rd(CORE,'episodes.csv');co=rd(CORE,'cohorts.csv');pr=rd(CORE,'priority.csv');ts=rd(CORE,'timeseries.csv');mo=rd(CORE,'modes.csv');man=json.loads((CORE/'manifest.json').read_text());meta=json.loads((CORE/'metadata.json').read_text());cfg=meta['config']
se=rd(SENS,'episodes.csv');sp=rd(SENS,'priority.csv');sman=json.loads((SENS/'manifest.json').read_text());scfg=json.loads((SENS/'metadata.json').read_text())['config'];mean=statistics.mean;sd=statistics.stdev
def ci(rows,profile,a,b,cut=48.):
 x={int(r['seed']):float(r['RN']) for r in rows if r.get('profile')==profile and r['policy']==a and float(r['cutoff_h'])==cut}
 y={int(r['seed']):float(r['RN']) for r in rows if r.get('profile')==profile and r['policy']==b and float(r['cutoff_h'])==cut}
 if not x:
  x={int(r['seed']):float(r['RN']) for r in rows if r.get('duration_h')==profile and r['policy']==a and float(r.get('cutoff_h',48))==cut}
  y={int(r['seed']):float(r['RN']) for r in rows if r.get('duration_h')==profile and r['policy']==b and float(r.get('cutoff_h',48))==cut}
 assert x.keys()==y.keys();v=[x[k]-y[k] for k in sorted(x)];m=mean(v);s=sd(v);h=2.093*s/math.sqrt(len(v));return (m,s,m-h,m+h,sum(q>0 for q in v))
profiles=[p['name'] for p in cfg['profiles']]
assert len(man)==240 and len(e)==1440 and len(se)==1200
for p in profiles:
 for seed in {int(x['seed']) for x in man if x['profile']==p}:
  g=[x for x in man if x['profile']==p and int(x['seed'])==seed];assert len(g)==1
  rows=[x for x in e if x['profile']==p and int(x['seed'])==seed]
  assert len(rows)==6 and len({x['trace_sha256'] for x in rows})==1 and len({x['admitted'] for x in rows})==1
  assert all(int(x['admitted'])==int(x['completed'])+int(x['pending']) for x in rows)
lines=['# Dominio operativo de D1, P1 y HLS-B','',
'**Estado de evidencia:** síntesis de confirmatorios previos y exploración nueva. El barrido operativo, SLA y dimensionamiento son exploratorios; no son validación independiente de HLS-B. Los CSV completos están en results locales. No se modificaron las estrategias.','',
'## Pregunta e hipótesis','',
'H1: la ventaja D1/P1 depende de carga y plazos. H2: las colas conservan memoria después de reducirse la tasa. H3: HLS-B puede superar políticas fijas en algunas perturbaciones y no en otras. H4: el orden relativo cambia con escala y separación de SLA. H5: capacidad y heterogeneidad L1/L2 cambian el cuello de botella. Son hipótesis, no resultados presupuestos.','',
'## Evidencia anterior y separación','',
'El contraste confirmatorio D1/P1 a ρ=1,25 encontró R/N 0,5180/0,6162, diferencia P1−D1 +0,0982 [0,0891;0,1073], n=100. En cargas menores P1 puede perder. La validación independiente HLS-B sobre cuatro escenarios equiponderados encontró HLS-B−D1 +0,02820 [0,02526;0,03115], impulsada por sobrecarga estacionaria; las dos transiciones individuales no mostraron ventaja concluyente frente a D1. Estos resultados conservan sus estimandos confirmatorios originales.','',
'Estudios dinámicos de desarrollo previos: un pulso ρ=1,25 de 16 h en H=24 mostró HLS-B−D1 +0,0286 [0,0116;0,0456] y HLS-B−mejor fija +0,0209 [0,0184;0,0234] en 20 semillas exploratorias, como única de seis duraciones favorable; al retorno a D1 persistían unas 136 alertas/31 h de trabajo. Ello motivó acotar la cuadrícula actual alrededor de carga × duración, B/Γ y recuperación. No se combinan semillas ni IC entre esos análisis.','',
'## Diseño central: 12 escenarios completos','',
'H=24 h de admisión; D=24 h sin llegadas. Tasa base ρ=0,85 en [0,4) y después del pulso; comienza siempre en t=4. Sobrecarga única a rho_high y duración indicadas. Roster base 6 L1/3 L2, elegibilidad 2,5 proyectos/analista, competencias, velocidad, mezcla y escalado del modelo de referencia. SLA terminal hipotético crítica/alta/baja = 1/4/12 h. HLS-B congelada (w=4 h, low=1,05, high=1,20). Veinte semillas nuevas 261240000–261240019 por perfil. Las mismas trazas se comparten entre políticas dentro del perfil/semilla.','',
'B=(rho_high−1)T_high y Γ=B/[(1−rho_low)T_low], con T_low=24−4−T_high. B/Γ son indicadores fluidos del exceso y capacidad de recuperación disponibles, no predictores exactos del sistema heterogéneo.','',
'| Perfil | ρ alta | T alta | T baja postpulso | B | Γ | Llegadas esperadas H |','|---|---:|---:|---:|---:|---:|---:|']
for p in cfg['profiles']:
    tl=24-4-p['duration_h'];B=(p['rho_high']-1)*p['duration_h'];G=B/((1-p['rho_recovery'])*tl);exp=meta['mu_l1']*(.85*24+(p['rho_high']-.85)*p['duration_h'])
    lines.append(f'| {p["name"]} | {p["rho_high"]:.2f} | {p["duration_h"]} h | {tl} h @ ρ={p["rho_recovery"]:.2f} | {B:.2f} | {G:.3f} | {exp:.1f} |')
lines+=['','Se incluyen tres pares aproximadamente B=0,8 y tres pares B=1,6 con amplitud/duración distintas; cinco duraciones con rho_high=1,25; y un control de recuperación postpulso a ρ=0,70. El control cambia capacidad de recuperación, no pulso. El horizonte fijo iguala tiempo potencial total, aunque duración cambia volumen de pulso y tiempo normal restante; esto se conserva explícito en cada perfil. Tasa base física es 0,85×capacidad fluida base; rho por definición respecto a roster base.','',
'## Dinámica física y mapas de resultados','',
'Cola vacía no equivale a SLA. La recuperación de trabajo se mide con serie de media hora hasta t=48. Cola pendiente es alertas sin inicio en cada pool; trabajo pendiente suma servicio nominal por clase; los plazos se clasifican en métricas por prioridad.','',
'| Perfil | Cola L1+L2 máxima D1 | Trabajo pendiente máximo (h) | Backlog H D1 | Backlog H+D D1 | Recuperación física D1 |','|---|---:|---:|---:|---:|---|']
for p in cfg['profiles']:
 z=[x for x in ts if x['profile']==p['name'] and x['policy']=='D1'];maxq=[];maxw=[];rec=[]
 for seed in {int(x['seed']) for x in z}:
  a=sorted([x for x in z if int(x['seed'])==seed],key=lambda x:float(x['time_h']));maxq.append(max(int(x['queue_l1'])+int(x['queue_l2']) for x in a));maxw.append(max(float(x['work_l1_h'])+float(x['work_l2_h']) for x in a));base=next(x for x in a if float(x['time_h'])==4);end=4+p['duration_h'];post=[x for x in a if float(x['time_h'])>=end];hit=None
  for i in range(len(post)-2):
   tri=post[i:i+3]
   if all(int(x['queue_l1'])+int(x['queue_l2'])<=int(base['queue_l1'])+int(base['queue_l2']) and float(x['work_l1_h'])+float(x['work_l2_h'])<=float(base['work_l1_h'])+float(base['work_l2_h']) for x in tri):hit=float(tri[0]['time_h'])-end;break
  if hit is not None:rec.append(hit)
 ep=[x for x in e if x['profile']==p['name'] and x['policy']=='D1'];h=mean(int(x['pending']) for x in ep if float(x['cutoff_h'])==24);hd=mean(int(x['pending']) for x in ep if float(x['cutoff_h'])==48)
 rec_text=f'{mean(rec):.2f} h ({len(rec)}/20)' if rec else 'NR antes de 48 h (0/20)'
 lines.append(f'| {p["name"]} | {mean(maxq):.1f} | {mean(maxw):.1f} | {h:.1f} | {hd:.1f} | {rec_text} |')
lines+=['','Recuperación física = primera ventana de tres puntos consecutivos (0,5 h) cuando backlog L1+L2 y trabajo pendiente son ambos ≤ sus valores justo antes del pulso (t=4). Las realizaciones que no recuperan antes de 48 h se cuentan como no recuperadas. No equivale a cumplimiento de SLA ni calidad.','',
'| Perfil | D1 R/N | P1 R/N | HLS-B R/N | Δ HLS-B−D1 [IC95] | Δ HLS-B−P1 [IC95] | Mejor fija | Δ HLS-B−mejor fija [IC95] |','|---|---:|---:|---:|---|---|---|---|']
core={}
for p in cfg['profiles']:
 means={pol:mean(float(x['RN']) for x in e if x['profile']==p['name'] and x['policy']==pol and float(x['cutoff_h'])==48) for pol in ('D1','P1','HLS-B')};best=max(('D1','P1'),key=lambda q:means[q]);core[p['name']]=means
 a=ci(e,p['name'],'HLS-B','D1');b=ci(e,p['name'],'HLS-B','P1');z=ci(e,p['name'],'HLS-B',best)
 lines.append(f'| {p["name"]} | {means["D1"]:.4f} | {means["P1"]:.4f} | {means["HLS-B"]:.4f} | {a[0]:+.4f} [{a[2]:+.4f};{a[3]:+.4f}] | {b[0]:+.4f} [{b[2]:+.4f};{b[3]:+.4f}] | {best} | {z[0]:+.4f} [{z[2]:+.4f};{z[3]:+.4f}] |')
lines+=['','IC95 % t pareados por perfil (19 gl), exploratorios, sin multiplicidad ni ajuste por selección de mejor fija. Una convención solo visual para el mapa: diferencia media ≥+0,005 y límite inferior >0 = ventaja observable; ≤−0,005 y límite superior <0 = inferioridad; |media|<0,005 con IC que incluye 0 = casi empate descriptivo; resto incierto. 0,005 no es umbral económico validado.','',
'### Cohortes terminales y prioridades','',
'R/N de cohortes pre [0,4), durante pulso y recuperación [fin pulso,24), evaluado hasta H+D y ponderado por admitidas. Se muestran celdas de duración/intensidad nominal a continuación; el CSV contiene las 36 cohortes.','',
'| Perfil | Cohorte | D1 | P1 | HLS-B |','|---|---|---:|---:|---:|']
for p in cfg['profiles']:
 if p['name'] in ('nom_r125_d8','nom_r125_d16','B16_rho140_d4','nom_r125_d8_fastrec'):
  for name in ('pre','pulse','post'):
   vals={pol:[x for x in co if x['profile']==p['name'] and x['policy']==pol and x['cohort']==name] for pol in ('D1','P1','HLS-B')};v={pol:sum(float(x['RN'])*int(x['n']) for x in z)/sum(int(x['n']) for x in z) for pol,z in vals.items()};lines.append(f'| {p["name"]} | {name} | {v["D1"]:.4f} | {v["P1"]:.4f} | {v["HLS-B"]:.4f} |')
lines+=['','Prioridades (high=crítica, medium=alta, low=baja) se conservan por política y perfil en priority.csv, con RN, SLA, tamaño y calidad entre completadas. No se agregan alertas como réplicas; las unidades de incertidumbre son episodios pareados (semillas).','',
'| Perfil | Política | SLA global | Calidad completadas |','|---|---|---:|---:|']
for pn in ('nom_r125_d2','nom_r125_d8','nom_r125_d16'):
 for pol in ('D1','P1','HLS-B'):
  z=[x for x in e if x['profile']==pn and x['policy']==pol and float(x['cutoff_h'])==48];lines.append(f'| {pn} | {pol} | {mean(float(x["SLA"]) for x in z):.4f} | {mean(float(x["quality_completed"]) for x in z):.4f} |')
lines+=['','Métricas por prioridad (medias ponderadas por n de alertas del estrato, no IC por alerta):','',
'| Perfil | Prioridad | Política | R/N | SLA | Calidad completadas |','|---|---|---|---:|---:|---:|']
for pn in ('nom_r125_d2','nom_r125_d8','nom_r125_d16'):
 for priority in ('high','medium','low'):
  for pol in ('D1','P1','HLS-B'):
   z=[x for x in pr if x['profile']==pn and x['policy']==pol and x['priority']==priority];n=sum(int(x['n']) for x in z);vals=[sum(float(x[k])*int(x['n']) for x in z)/n for k in ('RN','SLA','quality_completed')];lines.append(f'| {pn} | {priority} | {pol} | {vals[0]:.4f} | {vals[1]:.4f} | {vals[2]:.4f} |')
lines+=['','El SLA global es proporción puntual bajo deadline terminal; la calidad es la probabilidad modelada media entre completadas. Los estratos low/medium/high corresponden a baja/alta/crítica.','',
'### Resumen de conmutación','',
'La transición de modo se compara con backlog observado en la muestra temporal más próxima; no se interpreta como causa.','',
'| Perfil | Primera P1 media | Retorno D1 tras pulso | Cola L1+L2 al retorno | Trabajo al retorno (h) |','|---|---:|---:|---:|---:|']
for p in cfg['profiles']:
 first=[];ret=[];qret=[];wret=[];end=4+p['duration_h']
 for seed in {int(x['seed']) for x in mo if x['profile']==p['name'] and x['policy']=='HLS-B'}:
  z=sorted([x for x in mo if x['profile']==p['name'] and int(x['seed'])==seed and x['policy']=='HLS-B'],key=lambda x:float(x['time_h']));v=next((float(x['time_h']) for x in z if x['mode']=='P1' and x['switched']=='True'),None)
  if v is not None:first.append(v)
  u=next((float(x['time_h']) for x in z if float(x['time_h'])>=end and x['mode']=='D1' and x['switched']=='True'),None)
  if u is not None:
   ret.append(u-end);near=min([x for x in ts if x['profile']==p['name'] and int(x['seed'])==seed and x['policy']=='HLS-B'],key=lambda x:abs(float(x['time_h'])-u));qret.append(int(near['queue_l1'])+int(near['queue_l2']));wret.append(float(near['work_l1_h'])+float(near['work_l2_h']))
 lines.append(f'| {p["name"]} | {mean(first):.2f} h ({len(first)}/20) | {mean(ret):.2f} h ({len(ret)}/20) | {mean(qret):.1f} | {mean(wret):.1f} |')
lines+=['','La serie fina de modos/colas permite valorar si el umbral de baja devuelve HLS-B a D1 mientras permanece backlog. No se presume que mantener P1 mejore entonces R/N; P1 fija y sus cohortes son referencias observadas.','',
'## Sensibilidad SLA — configuraciones fijadas tras el barrido central','',
'Se eligieron nom_r125_d8 (sin ventaja adaptativa en centro) y nom_r125_d16 (único pulso central con mejora HLS-B). Misma tasa/traza exógena por semilla y perfil entre cinco calendarios de deadlines; el hash excluye deadlines y conserva las otras variables. Hipótesis terminales: high/crítica T0, medium/alta f_high×T0, low/baja f_low×T0.','',
'| Perfil | SLA config | T0 | f alta/baja | Tpulso/Tcrit | D1 | P1 | HLS-B | Δ HB−D1 | Δ HB−P1 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for profile in ('nom_r125_d8','nom_r125_d16'):
 for case in scfg['sla_sets']:
  z={pol:mean(float(x['RN']) for x in se if x['kind']=='sla' and x['case']==case['name'] and int(x['duration_h'])==int(profile.split('_d')[-1]) and x['policy']==pol) for pol in ('D1','P1','HLS-B')};ratio=int(profile.split('_d')[-1])/case['T0'];lines.append(f'| {profile} | {case["name"]} | {case["T0"]:.2f} | {case["f_high"]}/{case["f_low"]} | {ratio:.2f} | {z["D1"]:.4f} | {z["P1"]:.4f} | {z["HLS-B"]:.4f} | {z["HLS-B"]-z["D1"]:+.4f} | {z["HLS-B"]-z["P1"]:+.4f} |')
lines+=['','En la escala, T0 cambia a 0,75/1,00/1,25 h manteniendo razones 1:4:12. En la separación, T0=1 h y razones 1:2:8 o 1:8:16. Se mantienen mismos IDs, tiempos, clases, dificultades, recomendaciones y semillas en cada traza. Estas diferencias siguen siendo exploratorias; no elegir SLA por mejor política. Cocientes d/T0 se infieren de tabla y perfil.','',
'IC95 pareados de las dos diferencias de HLS-B, calculados sobre las 20 semillas comunes de cada configuración (t, 19 gl):','',
'| Perfil | SLA config | Δ HB−D1 [IC95] | Δ HB−P1 [IC95] |','|---|---|---|---|']
for profile in ('nom_r125_d8','nom_r125_d16'):
 for case in scfg['sla_sets']:
  dur=int(profile.split('_d')[-1]);g=[x for x in se if x['kind']=='sla' and x['case']==case['name'] and int(x['duration_h'])==dur];by={pol:{int(x['seed']):float(x['RN']) for x in g if x['policy']==pol} for pol in ('D1','P1','HLS-B')};
  vals=[]
  for pol in ('D1','P1'):
   d=[by['HLS-B'][k]-by[pol][k] for k in sorted(by['HLS-B'])];m=mean(d);h=2.093*sd(d)/math.sqrt(len(d));vals.append(f'{m:+.4f} [{m-h:+.4f};{m+h:+.4f}]')
  lines.append(f'| {profile} | {case["name"]} | {vals[0]} | {vals[1]} |')
lines+=['','Los intervalos describen incertidumbre Monte Carlo dentro de celda; los cinco contrastes SLA no son independientes porque comparten la traza base.','',
'## Sensibilidad al dimensionamiento','',
'Escenarios nom_r125_d8 y d16; misma tasa física λ(t) que equipo base 6×3. Se recalculó capacidad LP efectiva L1/L2 para cada roster y rho(t)=λ(t)/μ_team, sin conservar artificialmente los rhos nominales. Elegibilidad 2,5 y perfiles deterministas existentes; capacidad continua, sin turnos.','',
'| Perfil | Equipo L1×L2 | μL1 | μL2 | ρ normal/pulso real | D1 | P1 | HLS-B | Δ HB−D1 | Δ HB−P1 |','|---|---|---:|---:|---|---:|---:|---:|---:|---:|']
for profile in ('nom_r125_d8','nom_r125_d16'):
 for team in scfg['teams']:
  z={pol:[x for x in se if x['kind']=='staff' and x['case']==team['name'] and int(x['duration_h'])==int(profile.split('_d')[-1]) and x['policy']==pol] for pol in ('D1','P1','HLS-B')};v={pol:mean(float(x['RN']) for x in a) for pol,a in z.items()};row=z['D1'][0]
  lines.append(f'| {profile} | {team["n_l1"]}×{team["n_l2"]} | {float(row["mu_l1"]):.2f} | {float(row["mu_l2"]):.2f} | {float(row["rho_normal"]):.2f}/{float(row["rho_pulse"]):.2f} | {v["D1"]:.4f} | {v["P1"]:.4f} | {v["HLS-B"]:.4f} | {v["HLS-B"]-v["D1"]:+.4f} | {v["HLS-B"]-v["P1"]:+.4f} |')
lines+=['','Este diseño separa cambio en demanda física de cambio de recursos. Bajar L2 altera μL2, no tasa de entrada L1; se reporta el efecto completo de cuello/routing sintético, no se asume que L1 determine por sí solo el resultado. No se cambió composición de elegibilidad en este primer contraste porque no hay roster operativo validado para motivar otra ablation.','',
'Diferencias pareadas HB−fijas con IC95 % exploratorio (20 episodios por roster y duración):','',
'| Perfil | Equipo L1×L2 | Δ HB−D1 [IC95] | Δ HB−P1 [IC95] |','|---|---|---|---|']
for profile in ('nom_r125_d8','nom_r125_d16'):
 for team in scfg['teams']:
  dur=int(profile.split('_d')[-1]);g=[x for x in se if x['kind']=='staff' and x['case']==team['name'] and int(x['duration_h'])==dur];by={pol:{int(x['seed']):float(x['RN']) for x in g if x['policy']==pol} for pol in ('D1','P1','HLS-B')};vals=[]
  for pol in ('D1','P1'):
   d=[by['HLS-B'][k]-by[pol][k] for k in sorted(by['HLS-B'])];m=mean(d);h=2.093*sd(d)/math.sqrt(len(d));vals.append(f'{m:+.4f} [{m-h:+.4f};{m+h:+.4f}]')
  lines.append(f'| {profile} | {team["n_l1"]}×{team["n_l2"]} | {vals[0]} | {vals[1]} |')
lines+=['','Los rosters comparten la misma secuencia exógena semilla a semilla; cambiar roster cambia rho efectiva y es una comparación de entorno, no una asignación aleatoria de personal.','',
'## Sensibilidad de HLS-B','',
'No se hizo ajuste de umbral ni ventana. El barrido central muestra una oportunidad exploratoria concentrada en un solo perfil de pulso largo; como la selección ocurrió mirando ese mismo barrido, probar variantes aquí optimizaría sobre el dato. Se reserva una eventual comparación de ventanas/umbrales para un protocolo fijado y semillas nuevas si la futura réplica independiente confirma una región.','',
'## Mapa e interpretación','',
'![Mapa de perfiles según la diferencia pareada HLS-B menos la mejor fija, con incertidumbre](figures/soc_hls_operating_regions.svg)','',
'La clasificación del mapa usa la convención explícita anterior, no una frontera económica. Γ complementa B al expresar exceso frente al tiempo/capacidad de recuperación; pares de B semejante no siempre producen resultados equivalentes porque cambia deadline mix, composición, servicio discreto, escalado y la fracción de H consumida por el pulso. La recuperación a ρ=0,70 en el caso nominal de 8 h se contrasta con ρ=0,85, pero una diferencia entre dos perfiles no aísla solo la memoria si llegada y servicio también cambian trayectorias.','',
'## Limitaciones y conclusión para artículo','',
'La demanda es Poisson por tramos; el perfil por hora no está calibrado por datos timestamp restringidos. Volumen SOCTRA es registros, no trabajo activo. Servicios, equipos, competencias, escalado y SLA son hipótesis. Sin turnos/cobertura/pausas, se asume capacidad continua. Colas ilimitadas y no preemptivas. R/N es esperanza de calidad y cumplimiento puntual, no verdad de resolución observada; SLA terminal usa el final L2 para escaladas.','',
'Conclusión defendible: las políticas fijas y HLS-B ocupan regiones condicionadas a intensidad, duración, recuperación y deadline; la matriz encuentra variación de efecto y una ventaja adaptativa exploratoria localizada, no un umbral general. La sensibilidad SLA y roster muestra cómo someter esa región a cambios controlados. Los 20 episodios por celda y múltiples perfiles/configuraciones no constituyen confirmación; no se combina el universo de escenarios como si fueran semillas independientes. Si se considera robusta una región de interés tras revisión, el siguiente paso es una sola validación preespecificada en semillas nuevas, no más búsqueda adaptativa.','',
'## Reproducción y controles','',
'Matriz/config: config/soc_hls_operating_regions.json; sensibilidad: config/soc_hls_operating_sensitivity.json. Runners run_soc_hls_operating_regions.py y run_soc_hls_operating_sensitivity.py; tablas episodes/cohorts/priority/timeseries/modes y manifest en results/soc_hls_operating_regions, y SLA/staffing en results/soc_hls_operating_sensitivity (local ignorado). Se verifican hashes por política, admitidas comunes, conservación completadas+pendientes y uso de 20 semillas por escenario. Las mismas IDs de semilla aparecen entre perfiles; los análisis se hacen dentro de cada perfil y no se agrupan como observaciones independientes.']
(HERE/'SOC_HLS_OPERATING_REGIONS.md').write_text('\n'.join(lines)+'\n')
# categorical operating map: each profile has CI and mean; center = paired delta vs best fixed.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="620" viewBox="0 0 1050 620"><rect width="1050" height="620" fill="white"/><text x="25" y="25" font-family="sans-serif" font-size="18">Mapa de perfiles: Δ R/N terminal HLS-B − mejor política fija</text>'];colors={'adv':'#1a9850','infer':'#d73027','tie':'#91bfdb','uncertain':'#fdae61'}
for i,p in enumerate(cfg['profiles']):
 best=max(('D1','P1'),key=lambda q:core[p['name']][q]);z=ci(e,p['name'],'HLS-B',best);m,lo,hi=z[0],z[2],z[3]
 cls='adv' if m>=.005 and lo>0 else ('infer' if m<=-.005 and hi<0 else ('tie' if abs(m)<.005 and lo<=0<=hi else 'uncertain'));x=260+m*4200;y=65+i*39
 svg.append(f'<text x="20" y="{y+4}" font-family="sans-serif" font-size="12">{p["name"]} | ρ={p["rho_high"]:.2f}, d={p["duration_h"]}h, B={(p["rho_high"]-1)*p["duration_h"]:.1f}, Γ={(p["rho_high"]-1)*p["duration_h"]/((1-.85)*(24-4-p["duration_h"])):.2f}</text>')
 svg.append(f'<line x1="{260+lo*4200:.1f}" y1="{y}" x2="{260+hi*4200:.1f}" y2="{y}" stroke="{colors[cls]}" stroke-width="3"/><circle cx="{x:.1f}" cy="{y}" r="6" fill="{colors[cls]}"/><text x="{780}" y="{y+4}" font-family="sans-serif" font-size="11">{best}; {m:+.3f} [{lo:+.3f},{hi:+.3f}]</text>')
svg+=['<line x1="260" y1="52" x2="260" y2="535" stroke="#777" stroke-dasharray="4 3"/>','<text x="25" y="570" fill="#1a9850" font-family="sans-serif" font-size="12">ventaja descriptiva</text>','<text x="180" y="570" fill="#d73027" font-family="sans-serif" font-size="12">inferioridad</text>','<text x="300" y="570" fill="#91bfdb" font-family="sans-serif" font-size="12">casi empate</text>','<text x="430" y="570" fill="#fdae61" font-family="sans-serif" font-size="12">incierto</text>','<text x="25" y="600" font-family="sans-serif" font-size="11">IC95 % t pareado exploratorio, n=20; mejor fija seleccionada por media; sin ajuste multiplicidad.</text>','</svg>'];(HERE/'figures/soc_hls_operating_regions.svg').write_text('\n'.join(svg));print('report and operating map saved')

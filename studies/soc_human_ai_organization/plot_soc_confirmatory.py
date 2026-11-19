"""Render predeclared confirmatory figures from saved CSV; no simulations."""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/soc_confirmatory_d1_p1'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=list(csv.DictReader((OUT/'summary.csv').open()))
sc=['rho_0.85_secondary','rho_1.00_secondary','rho_1.10_secondary','rho_1.15_secondary','rho_125_primary']
rhos=[.85,1.,1.10,1.15,1.25]
def get(s,p,metric,cut=48.):
 return next(x for x in rows if x['scenario']==s and x['policy']==p and x['metric']==metric and x['cutoff_h']==str(cut))
fig,ax=plt.subplots(figsize=(7,4.3))
for p,marker in [('D1','o'),('P1','s')]:
 y=[float(get(s,p,'R_per_admitted')['mean']) for s in sc]
 lo=[float(get(s,p,'R_per_admitted')['mean_ci_low']) for s in sc]
 hi=[float(get(s,p,'R_per_admitted')['mean_ci_high']) for s in sc]
 ax.errorbar(rhos,y,yerr=[[a-b for a,b in zip(y,lo)],[a-b for a,b in zip(hi,y)]],marker=marker,capsize=3,label=p)
ax.set(xlabel='Carga relativa L1 (ρ)',ylabel='R/N terminal esperado',title='Rendimiento frente a carga (100 semillas emparejadas)');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(OUT/'rn_by_load.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.3))
y=[float(get(s,'P1','R_per_admitted')['delta_p1_d1']) for s in sc]
lo=[float(get(s,'P1','R_per_admitted')['delta_ci_low']) for s in sc]
hi=[float(get(s,'P1','R_per_admitted')['delta_ci_high']) for s in sc]
ax.errorbar(rhos,y,yerr=[[a-b for a,b in zip(y,lo)],[a-b for a,b in zip(hi,y)]],fmt='o-',capsize=4)
ax.axhline(0,color='black',lw=1);ax.set(xlabel='Carga relativa L1 (ρ)',ylabel='Diferencia P1−D1 en R/N',title='Efecto pareado e IC95 % bilateral');ax.grid(alpha=.25);fig.tight_layout();fig.savefig(OUT/'paired_effect_by_load.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.3))
for p,marker in [('D1','o'),('P1','s')]:
 x=[float(get(s,p,'sla')['mean']) for s in sc]
 y=[float(get(s,p,'quality_completed')['mean']) for s in sc]
 ax.plot(x,y,marker=marker,label=p)
 for xx,yy,rho in zip(x,y,rhos):ax.annotate(f'{rho:.2f}',(xx,yy),xytext=(4,3),textcoords='offset points',fontsize=8)
ax.set(xlabel='SLA terminal por admitida',ylabel='Calidad esperada entre completadas',title='Compromiso puntualidad–calidad');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(OUT/'sla_quality_tradeoff.svg');plt.close(fig)
print('three figures created')

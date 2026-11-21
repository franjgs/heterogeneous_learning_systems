from __future__ import annotations
import csv,sys
from pathlib import Path
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results'/'soc_triage_hls_q1_integration_evidence'
def read(p):
 with (OUT/p).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
summary=read('summary_by_condition.csv'); contr=read('paired_policy_contrasts.csv'); ana=read('analytic_workload_by_alpha.csv')
points=[('standardized_lightgbm_apc_symmetric','LightGBM A+C'),('standardized_lsensemble_apc_symmetric','LSEnsemble A+C'),('standardized_bayesian_mlp_apc_symmetric','Bayesian MLP A+C')]
colors={'D1':'#4C78A8','P1':'#F58518','HLS-B':'#54A24B'}
markers={'D1':'o','P1':'s','HLS-B':'^'}
# S+ with seed-cluster intervals: each panel is a classifier × L2 roster.
fig,axs=plt.subplots(3,3,figsize=(13,10),sharex=True,sharey=True,constrained_layout=True)
for i,(cid,label) in enumerate(points):
 for j,n in enumerate((2,3,4)):
  ax=axs[i,j]
  for pol in ('D1','P1','HLS-B'):
   rs=sorted([r for r in summary if r['classifier_id']==cid and int(r['n_L2'])==n and r['policy']==pol],key=lambda x:float(x['alpha']))
   x=[float(r['alpha']) for r in rs]; y=[float(r['S_plus_pooled']) for r in rs]
   lo=[v-float(r['S_plus_CI95_low']) for v,r in zip(y,rs)];hi=[float(r['S_plus_CI95_high'])-v for v,r in zip(y,rs)]
   ax.errorbar(x,y,yerr=[lo,hi],color=colors[pol],marker=markers[pol],lw=1.6,capsize=2,label=pol)
  ax.set_title(f'{label}; L2={n}',fontsize=9)
  ax.grid(alpha=.25);ax.set_xticks([.25,.5,.75,1.0]);
  if i==2:ax.set_xlabel(r'FP service fraction $\alpha$')
  if j==0:ax.set_ylabel(r'Pooled $S_+$ (95% paired-seed bootstrap CI)')
  if i==0 and j==2:ax.legend(frameon=False,fontsize=8)
fig.suptitle('Need-specific timely resolution across false-positive work assumptions',fontsize=14)
fig.savefig(OUT/'figures'/'splus_alpha_capacity.png',dpi=180);plt.close(fig)
# Expected offered L2 load; analytical capacity-adjusted marker, not observed utilization.
fig,axs=plt.subplots(1,3,figsize=(13,4),sharey=True,constrained_layout=True)
for ax,(cid,label) in zip(axs,points):
 for n,style in zip((2,3,4),('-','--',':')):
  rs=sorted([r for r in ana if r['id']==cid and int(r['n_L2'])==n],key=lambda x:float(x['alpha']))
  ax.plot([float(r['alpha']) for r in rs],[float(r['rho_L2_offered']) for r in rs],style,marker='o',label=f'L2={n}')
 ax.axhline(1,color='black',lw=1,alpha=.65)
 ax.set_title(label);ax.set_xlabel(r'FP service fraction $\alpha$');ax.grid(alpha=.25);ax.set_xticks([.25,.5,.75,1.0])
axs[0].set_ylabel(r'Offered $\rho_{L2}$ (fluid capacity LP)')
axs[-1].legend(frameon=False)
fig.suptitle('Analytical L2 offered load as false-positive service changes',fontsize=13)
fig.savefig(OUT/'figures'/'rho_l2_alpha.png',dpi=180);plt.close(fig)
# Paired organizational contrasts in S+.
fig,axs=plt.subplots(3,3,figsize=(13,10),sharex=True,sharey=True,constrained_layout=True)
for i,(cid,label) in enumerate(points):
 for j,n in enumerate((2,3,4)):
  ax=axs[i,j]
  for name,clr,mark in [('WAPS-D1','#54A24B','^'),('P1-D1','#F58518','s')]:
   rs=sorted([r for r in contr if r['classifier_id']==cid and int(r['n_L2'])==n and r['contrast']==name],key=lambda x:float(x['alpha']))
   x=[float(r['alpha']) for r in rs];y=[float(r['S_plus_difference']) for r in rs]
   lo=[v-float(r['bootstrap_CI95_low']) for v,r in zip(y,rs)];hi=[float(r['bootstrap_CI95_high'])-v for v,r in zip(y,rs)]
   ax.errorbar(x,y,yerr=[lo,hi],color=clr,marker=mark,lw=1.5,capsize=2,label=name)
  ax.axhline(0,color='black',lw=.9);ax.grid(alpha=.25);ax.set_title(f'{label}; L2={n}',fontsize=9);ax.set_xticks([.25,.5,.75,1.0])
  if i==2:ax.set_xlabel(r'FP service fraction $\alpha$')
  if j==0:ax.set_ylabel('Paired difference in pooled S+')
  if i==0 and j==2:ax.legend(frameon=False,fontsize=8)
fig.suptitle('Policy contrasts vary with classifier, capacity and FP workload',fontsize=14)
fig.savefig(OUT/'figures'/'policy_contrasts_alpha.png',dpi=180);plt.close(fig)
print('saved figures')

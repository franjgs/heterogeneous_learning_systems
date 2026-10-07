"""Small frozen-physics CONFIGURATION x ENVIRONMENT campaign."""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/"src"))
from hls.discover_develop_v0 import DISCOVER_DEVELOP,MODES,run_sequence
from hls.discover_v0 import THETA_1,THETA_2,enumerate_canonical_states,evaluate_state
OUT=ROOT/"results/foundations/discover_develop_campaign"
IDS=(0,1,2,3,7,14,16,30); STATES=enumerate_canonical_states(); CONFIG={f"S{i:03d}":STATES[i] for i in IDS}
ENV={"persistent":(THETA_1,)*3,"change":(THETA_1,THETA_1,THETA_2),"alternating":(THETA_1,THETA_2,THETA_1),"mixed":(THETA_2,THETA_1,THETA_1)}
def tx(x):return json.dumps(x,separators=(",",":"))
def wr(rows,path):
 with path.open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
def desc(s):
 vals=[v for row in s for v in row]; cols=[sum(row[k] for row in s) for k in range(2)]; rows=[sum(row) for row in s]
 vk=evaluate_state(s).known_value
 return {"budget":sum(vals),"concentration":sum(v*v for v in vals),"agent_heterogeneity":sum((v-sum(rows)/len(rows))**2 for v in rows),"coverage_capability1":cols[0],"coverage_capability2":cols[1],"balance":abs(cols[0]-cols[1]),"redundancy":sum(v>0 for v in vals),"V_K_initial":vk,"state":tx(s)}
def main():
 tr=[];mp=[]; conf=[]
 for cid,s in CONFIG.items():conf.append({"configuration_id":cid}|desc(s))
 for cid,s in CONFIG.items():
  for env,ths in ENV.items():
   rows=run_sequence(s,ths,mode=DISCOVER_DEVELOP,seed=20261006)
   mp.append({"configuration_id":cid,"environment":env,"mode":DISCOVER_DEVELOP,"performance":rows[-1].cumulative_expected_reward,"early_performance":sum(x.expected_reward_true for x in rows[:3]),"late_performance":sum(x.expected_reward_true for x in rows[-3:]),"final_S":tx(rows[-1].state_after),"assignment_changes":len({tx(x.action) for x in rows})-1,"development":rows[-1].state_after!=s})
   for x in rows:tr.append({"configuration_id":cid,"environment":env,"mode":x.mode,"problem_id":x.problem_id,"step_id":x.step_id,"theta":x.true_theta,"belief_pre":x.belief_before,"belief_post":x.belief_after,"S_pre":tx(x.state_before),"S_post":tx(x.state_after),"X":tx(x.action),"exercised":tx(x.action),"reward":x.expected_reward_true,"cumulative":x.cumulative_expected_reward})
 # full controls only representative prototype states
 for cid in ("S001","S002","S003"):
  s=CONFIG[cid]
  for env,ths in ENV.items():
   for mode in MODES:
    rows=run_sequence(s,ths,mode=mode,seed=20261006);mp.append({"configuration_id":cid,"environment":env,"mode":mode,"performance":rows[-1].cumulative_expected_reward,"early_performance":sum(x.expected_reward_true for x in rows[:3]),"late_performance":sum(x.expected_reward_true for x in rows[-3:]),"final_S":tx(rows[-1].state_after),"assignment_changes":len({tx(x.action) for x in rows})-1,"development":rows[-1].state_after!=s})
 pairs=[]
 for i,a in enumerate(conf):
  for b in conf[i+1:]:pairs.append({"a":a["configuration_id"],"b":b["configuration_id"],"Delta_VK":abs(a["V_K_initial"]-b["V_K_initial"]),"Delta_concentration":abs(a["concentration"]-b["concentration"]),"Delta_heterogeneity":abs(a["agent_heterogeneity"]-b["agent_heterogeneity"])})
 analysis=[]
 for env in ENV:
  cells=[x for x in mp if x["environment"]==env and x["mode"]==DISCOVER_DEVELOP]
  for c in conf:
   cell=next(x for x in cells if x["configuration_id"]==c["configuration_id"])
   analysis.append({"environment":env,"configuration_id":c["configuration_id"],"performance":cell["performance"],**{k:c[k] for k in ("concentration","agent_heterogeneity","balance","redundancy","V_K_initial")}})
 cases=[x for x in mp if x["mode"]==DISCOVER_DEVELOP and (x["configuration_id"],x["environment"]) in {("S030","persistent"),("S030","alternating"),("S001","change"),("S002","change"),("S003","change")}]
 OUT.mkdir(parents=True,exist_ok=True);wr(conf,OUT/"configurations.csv");wr([{"environment":k,"theta_sequence":"|".join("theta1" if x==THETA_1 else "theta2" for x in v)} for k,v in ENV.items()],OUT/"environments.csv");wr(mp,OUT/"configuration_environment_map.csv");wr(tr,OUT/"trajectories.csv");wr(pairs,OUT/"matched_pairs.csv");wr(analysis,OUT/"structural_analysis.csv");wr(cases,OUT/"representative_cases.csv")
 (OUT/"manifest.json").write_text(json.dumps({"frozen_head":"7eb7530","configs":list(CONFIG),"environments":list(ENV),"main_cells":32,"controls":"S001-S003 x 4 environments x A/B/C/D","seed":20261006,"physics":"unchanged DISCOVER x DEVELOP prototype"},indent=2)+"\n")
if __name__=="__main__":main()

"""Small reproducible DISCOVER x DEVELOP demonstration, not a campaign."""
from __future__ import annotations
import csv, json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT/"src"))
from hls.discover_develop_v0 import MODES, run_sequence
from hls.discover_v0 import THETA_1, THETA_2, enumerate_canonical_states

OUT=ROOT/"results/foundations/discover_develop_v0"
ENV={"persistent":(THETA_1,THETA_1,THETA_1),"change":(THETA_1,THETA_1,THETA_2),"alternating":(THETA_1,THETA_2,THETA_1)}
CONFIG={f"S{i:03d}": enumerate_canonical_states()[i] for i in (1,2,3)}
def text(value): return json.dumps(value, separators=(",",":"))
def write(rows,path):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n"); w.writeheader();w.writerows(rows)
def main():
    trajectory=[]; summary=[]
    for cid,state in CONFIG.items():
      for env,thetas in ENV.items():
       for mode in MODES:
        rows=run_sequence(state,thetas,mode=mode,seed=20261006)
        for r in rows:
         trajectory.append({"configuration_id":cid,"environment":env,"problem_id":r.problem_id,"step_id":r.step_id,"mode":mode,"true_theta":r.true_theta,"belief_before":r.belief_before,"belief_after":r.belief_after,"S_before":text(r.state_before),"S_after":text(r.state_after),"X":text(r.action),"exercised_capabilities":text(r.action),"expected_reward_true":r.expected_reward_true,"observed_reward":r.observed_reward,"MIS_active":mode in ("discover_develop","develop_known"),"cumulative_expected_reward":r.cumulative_expected_reward})
        summary.append({"configuration_id":cid,"environment":env,"mode":mode,"cumulative_expected_reward":rows[-1].cumulative_expected_reward,"final_S":text(rows[-1].state_after),"final_belief":rows[-1].belief_after,"state_changed":rows[-1].state_after!=state,"action_changed":len({text(r.action) for r in rows})>1})
    OUT.mkdir(parents=True,exist_ok=True); write(trajectory,OUT/"trajectories.csv");write(summary,OUT/"episode_problem_summaries.csv");write(summary,OUT/"configuration_environment_summaries.csv")
    (OUT/"manifest.json").write_text(json.dumps({"scope":"small controlled functional prototype", "MIS_learning_scale":1.5,"horizon_per_problem":3,"problem_count":3,"configurations":list(CONFIG),"environments":list(ENV),"modes":list(MODES),"seed":20261006,"dynamic_planning":"two-step receding-horizon Bellman look-ahead"},indent=2)+"\n")
if __name__=="__main__": main()

"""Counterfactual engine, imported on demand; NEVER runs on import.

Uses frozen Campaign 3 simulator functions without changing their code.
The caller must supply audited latent problem sequences, model, and thresholds.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from typing import Literal
import numpy as np

from experiments.synthetic.campaign3_fast_deep_meta.run import choose_fast_action, choose_deep_action
from experiments.synthetic.campaign3_meta_voc import run as voc
from experiments.synthetic.campaign3_c33 import c33
from hls import campaign2_theory as theory
from hls import finite_problem_belief as planner
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR

Horizon = Literal["H0", "H1", "H2"]
Continuation = Literal["Q11", "META_VOC_50"]


def horizon_end(start_clock: int, remaining: int, horizon: Horizon) -> int:
    """Inclusive final global clock for the three frozen evaluation horizons.

    H0 is exactly two real decisions; H1 ends at the current problem boundary;
    H2 ends at global clock 36. H0 is not the C3.2 ell=11 label horizon.
    """
    if type(start_clock) is not int or not 1 <= start_clock <= 36:
        raise ValueError("start_clock must be an integer in [1, 36]")
    expected_remaining = 3 - (start_clock - 1) % 3
    if remaining != expected_remaining or remaining not in (2, 3):
        raise ValueError("C4 counterfactuals require a nonterminal state with matching remaining clock")
    if horizon == "H0":
        end = start_clock + 1
    elif horizon == "H1":
        end = start_clock + remaining - 1
    elif horizon == "H2":
        end = 36
    else:
        raise ValueError(f"invalid horizon: {horizon}")
    if end > 36:
        raise ValueError("horizon exceeds the frozen 36-decision history")
    return end


def stable_seed(*parts: object) -> int:
    payload = json.dumps(parts, separators=(",", ":"), ensure_ascii=True).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**63 - 1)


def innovations(state_id: str, replicate: int, clocks: range) -> dict[int, float]:
    """Branch-independent, clock-indexed Gaussian innovations."""
    return {clock: float(np.random.default_rng(stable_seed("HLS-C4-NOISE-v1", state_id, replicate, clock)).standard_normal())
            for clock in clocks}


def state_from_record(record: dict):
    state = tuple(tuple(float(v) for v in row) for row in json.loads(record["state_before"]))
    belief = tuple(float(v) for v in json.loads(record["belief_before"]))
    if len(state) != 3 or any(len(row) != 2 for row in state) or len(belief) != 3:
        raise ValueError("invalid state/belief shape")
    if not np.isfinite(np.array(state)).all() or not np.isfinite(np.array(belief)).all():
        raise ValueError("nonfinite state/belief")
    planner.validate_belief(belief, 3)
    clock, remaining, tau = (int(record[k]) for k in ("clock", "remaining", "tau"))
    if not (1 <= clock <= 36 and remaining in (2, 3) and remaining == 3-(clock-1)%3 and tau == 37-clock):
        raise ValueError("clock/remaining/tau mismatch")
    return state, belief, clock, remaining


def frozen_selector(state, belief, clock, model, costs, thresholds):
    tau = 37-clock
    score, predicted, cost = voc.ex_ante_score(state, belief, tau, model, costs)
    key = voc.feature_tie_key(c33.feature_vector(state, belief, tau))
    route = voc.threshold_route(score, key, thresholds["50"])
    return {"prediction": predicted, "score": score, "predicted_cost": cost, "invoke": bool(route)}


def choose_continuation(state, belief, clock, continuation, model, costs, thresholds):
    remaining = 3-(clock-1)%3
    if remaining == 1:
        return choose_fast_action(state, belief, remaining)[0], False
    if continuation == "Q11":
        return choose_deep_action(state, belief, remaining)[0], True
    if continuation == "META_VOC_50":
        invoke = frozen_selector(state, belief, clock, model, costs, thresholds)["invoke"]
        fn = choose_deep_action if invoke else choose_fast_action
        return fn(state, belief, remaining)[0], invoke
    raise ValueError(f"invalid continuation: {continuation}")


def rollout(record, *, branch, horizon, continuation, problems, eps, model, costs, thresholds):
    """One branch, with current and future physical problems supplied externally.

    problems is a 12-element sequence of latent p values indexed by problem number.
    eps is a dict of Gaussian innovations indexed by global clock.
    """
    if branch not in ("FAST", "DEEP") or horizon not in ("H0", "H1", "H2"):
        raise ValueError("invalid branch/horizon")
    state, belief, start, remaining = state_from_record(record)
    end = horizon_end(start, remaining, horizon)
    if len(problems) != 12 or not all(clock in eps for clock in range(start,end+1)):
        raise ValueError("missing physical problems or innovations")
    hypotheses, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    initial_action = (choose_fast_action if branch == "FAST" else choose_deep_action)(state,belief,remaining)[0]
    reward = current = later = 0.0
    deep_future = 0
    trace = []
    for clock in range(start,end+1):
        if clock > start and (clock-1)%3 == 0:
            belief = prior
        if clock == start:
            action = initial_action
            invoked = branch == "DEEP"
        else:
            action, invoked = choose_continuation(state,belief,clock,continuation,model,costs,thresholds)
            deep_future += int(invoked)
        p = float(problems[(clock-1)//3])
        real = theory._real_decision(state,belief,action,(p,1.0-p),float(eps[clock]),hypotheses)
        reward += real.mu_true
        if (clock-1)//3 == (start-1)//3: current += real.mu_true
        else: later += real.mu_true
        trace.append({"clock":clock,"action_id":c33.ACTION_IDS[action],"mu_true":real.mu_true,"invoked_deep":bool(invoked)})
        state, belief = real.state_after, real.belief_after
    return {"reward":reward,"reward_current":current,"reward_later":later,
            "state_final":state,"belief_final":belief,"deep_future":deep_future,"trace":trace}


def evaluate_pair(record, *, horizon, continuation, replicate, problems, model, costs, thresholds):
    """Explicit entry point; no execution unless called by an authorized driver."""
    state, belief, clock, remaining = state_from_record(record)
    end = horizon_end(clock, remaining, horizon)
    eps = innovations(str(record["state_id"]),replicate,range(clock,end+1))
    a_f = choose_fast_action(state,belief,remaining)[0]
    a_d = choose_deep_action(state,belief,remaining)[0]
    selector = frozen_selector(state,belief,clock,model,costs,thresholds)
    fast = rollout(record,branch="FAST",horizon=horizon,continuation=continuation,
                   problems=problems,eps=eps,model=model,costs=costs,thresholds=thresholds)
    deep = rollout(record,branch="DEEP",horizon=horizon,continuation=continuation,
                   problems=problems,eps=eps,model=model,costs=costs,thresholds=thresholds)
    equal = a_f == a_d
    if equal and (fast["trace"] != deep["trace"] or fast["state_final"] != deep["state_final"]
                  or fast["belief_final"] != deep["belief_final"]):
        raise AssertionError("identical initial actions diverged under paired innovations")
    p = float(problems[(clock-1)//3])
    # Immediate reward is the first recorded real physical production.
    delta0 = deep["trace"][0]["mu_true"] - fast["trace"][0]["mu_true"]
    return {"state_id":record["state_id"],"history_id":record["history_id"],"domain":record["domain"],
            "source_policy":record["policy"],"clock":clock,"remaining":remaining,
            "horizon":horizon,"continuation":continuation,"replicate":replicate,
            "latent_p":p,"actions_equal":equal,"fast_action_id":c33.ACTION_IDS[a_f],
            "deep_action_id":c33.ACTION_IDS[a_d],"delta0":delta0,
            "delta_reward":deep["reward"]-fast["reward"],
            "delta_current":deep["reward_current"]-fast["reward_current"],
            "delta_later":deep["reward_later"]-fast["reward_later"],
            "fast":fast,"deep":deep,**selector}

"""Controlled IA–L1/L2 simulation and a minimal discrete-action interface.

SOCTRA records are not used as the simulated world state. They inform scenario
parameters only. The RQ1 allocation and L1/L2 event engines remain the sole
queue/dispatch implementations.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random
from typing import Mapping, Sequence

from .rq1_allocation import Alert, Analyst, B3Config
from .rq1_l1_l2 import RoutedAlert, L1L2Result, simulate_l1_l2


@dataclass(frozen=True)
class SimulatedAlert:
    routed: RoutedAlert
    severity: str
    difficulty: float
    true_escalation_need: bool  # evaluator-only; never returned in observation


@dataclass(frozen=True)
class ScenarioConfig:
    horizon: float = 1.0
    arrival_rate: float = 80.0
    l1_availability_fraction: float = 1.0
    l2_availability_fraction: float = 1.0
    classes: tuple[str, ...] = ("class_0", "class_1", "class_2")
    class_probabilities: tuple[float, ...] = (0.5, 0.3, 0.2)
    severity_probabilities: tuple[float, float, float] = (1 / 3, 1 / 3, 1 / 3)
    severity_categories: tuple[str, str, str] = ("low", "medium", "high")
    escalation_probability_by_class: tuple[float, ...] = (0.08, 0.16, 0.28)
    escalation_probability_by_class_severity: tuple[tuple[float, float, float], ...] | None = None
    deadline_by_severity: tuple[tuple[str, float], ...] = (("low", 0.12), ("medium", 0.07), ("high", 0.035))
    burst_window: tuple[float, float, float] | None = None  # start, end, rate multiplier
    arrival_rate_shift_after: float | None = None
    arrival_rate_after: float | None = None
    shift_after: float | None = None
    shift_class_probabilities: tuple[float, ...] | None = None
    ai_sensitivity: float = 0.85
    ai_false_positive_rate: float = 0.10
    ai_shift_sensitivity_delta: float = -0.15
    ai_shift_false_positive_delta: float = 0.10
    ai_sensitivity_by_severity: tuple[float, float, float] | None = None
    ai_false_positive_by_severity: tuple[float, float, float] | None = None
    difficulty_beta: tuple[float, float] = (2.0, 2.0)
    reference_escalation_difficulty_threshold: float | None = None


@dataclass(frozen=True)
class EpisodeResult:
    policy: str
    simulation: L1L2Result
    alert_count: int
    ai_true_positive_rate: float
    ai_false_positive_rate: float
    ai_recommendation_rate: float
    resolution_accuracy: float
    reward: float
    coordination_person_time: float


def generate_alerts(config: ScenarioConfig, seed: int) -> tuple[SimulatedAlert, ...]:
    """Generate a seeded non-homogeneous Poisson trace and hidden references."""
    _validate_config(config)
    rng = random.Random(seed)
    t = 0.0
    rows: list[SimulatedAlert] = []
    rates = dict(config.deadline_by_severity)
    while True:
        base_rate = (config.arrival_rate_after if config.arrival_rate_shift_after is not None
                     and t >= config.arrival_rate_shift_after else config.arrival_rate)
        multiplier = (config.burst_window[2]
                      if config.burst_window and config.burst_window[0] <= t < config.burst_window[1]
                      else 1.0)
        boundaries = [config.horizon]
        if config.burst_window:
            boundaries.extend(x for x in config.burst_window[:2] if x > t)
        if config.shift_after is not None and config.shift_after > t:
            boundaries.append(config.shift_after)
        if config.arrival_rate_shift_after is not None and config.arrival_rate_shift_after > t:
            boundaries.append(config.arrival_rate_shift_after)
        boundary = min(boundaries)
        proposal = t + rng.expovariate(base_rate * multiplier)
        if proposal >= boundary:
            t = boundary
            if t >= config.horizon:
                break
            continue
        if config.shift_after is not None and t >= config.shift_after:
            probs = config.shift_class_probabilities or config.class_probabilities
        else:
            probs = config.class_probabilities
        t = proposal
        ix = _categorical(rng, probs)
        class_name = config.classes[ix]
        severity_ix = _categorical(rng, config.severity_probabilities)
        severity = config.severity_categories[severity_ix]
        difficulty = rng.betavariate(*config.difficulty_beta)
        p_need = (config.escalation_probability_by_class_severity[ix][severity_ix]
                  if config.escalation_probability_by_class_severity is not None
                  else config.escalation_probability_by_class[ix])
        need_draw = rng.random()
        need = (difficulty >= config.reference_escalation_difficulty_threshold
                if config.reference_escalation_difficulty_threshold is not None
                else need_draw < p_need)
        shifted = config.shift_after is not None and t >= config.shift_after
        base_sensitivity = config.ai_sensitivity_by_severity[severity_ix] if config.ai_sensitivity_by_severity else config.ai_sensitivity
        base_fpr = config.ai_false_positive_by_severity[severity_ix] if config.ai_false_positive_by_severity else config.ai_false_positive_rate
        sensitivity = min(1.0, max(0.0, base_sensitivity + (config.ai_shift_sensitivity_delta if shifted else 0.0)))
        fpr = min(1.0, max(0.0, base_fpr + (config.ai_shift_false_positive_delta if shifted else 0.0)))
        recommendation = rng.random() < (sensitivity if need else fpr)
        alert_id = f"sim-{len(rows):08d}"
        alert = Alert(alert_id, t, class_name, t + rates[severity])
        rows.append(SimulatedAlert(
            RoutedAlert(alert, historical_escalation_label=need, soctra_recommendation=recommendation),
            severity, difficulty, need,
        ))
    return tuple(rows)


def run_episode(
    config: ScenarioConfig,
    seed: int,
    *,
    policy: str,
    l1_analysts: Sequence[Analyst],
    l2_analysts: Sequence[Analyst],
    l1_service_by_class: Mapping[object, float],
    l2_service_by_class: Mapping[object, float],
    coordination_latency: float = 0.0,
    drain_period: float = 0.5,
    b3_config: B3Config = B3Config(),
    reward_weights: tuple[float, float, float, float, float] = (1.0, 0.25, 0.10, 0.01, 0.10),
    l1_service_by_analyst_class: Mapping[str, Mapping[object, float]] | None = None,
    l2_service_by_analyst_class: Mapping[str, Mapping[object, float]] | None = None,
) -> EpisodeResult:
    """Run one hidden-truth episode with fixed AI-recommendation acceptance.

    Reward is assigned once at episode end: SLA fraction + weighted modeled
    assignment quality - coordination and triage-error costs. Each terminal
    outcome is accounted for once; intermediate decisions receive no reward.
    """
    alerts = generate_alerts(config, seed)
    l1_roster = _available_roster(l1_analysts, config.l1_availability_fraction, seed ^ 0x1A11)
    l2_roster = _available_roster(l2_analysts, config.l2_availability_fraction, seed ^ 0x2B22)
    result = simulate_l1_l2(
        tuple(row.routed for row in alerts), l1_roster, l2_roster,
        l1_service_by_class, l2_service_by_class, policy=policy,
        admission_horizon=config.horizon, drain_period=drain_period,
        coordination_latency=coordination_latency,
        decision_mode="hypothetical_recommendation_acceptance",
        b3_config=b3_config, random_seed=seed,
        l1_service_by_analyst_class=_restrict_service_map(l1_service_by_analyst_class, l1_roster),
        l2_service_by_analyst_class=_restrict_service_map(l2_service_by_analyst_class, l2_roster),
    )
    tp = sum(a.true_escalation_need and bool(a.routed.soctra_recommendation) for a in alerts)
    fn = sum(a.true_escalation_need and not a.routed.soctra_recommendation for a in alerts)
    fp = sum(not a.true_escalation_need and bool(a.routed.soctra_recommendation) for a in alerts)
    tn = len(alerts) - tp - fn - fp
    final_assignments = {j.alert_id: j for j in result.l2_simulation.assignments}
    final_assignments.update({
        j.alert_id: j for j in result.l1_simulation.assignments
        if not bool(next(a.routed.soctra_recommendation for a in alerts if a.routed.alert.alert_id == j.alert_id))
    })
    outcome_rng = random.Random(seed ^ 0x5A17)
    correct = 0
    for row in alerts:
        job = final_assignments.get(row.routed.alert.alert_id)
        if job is not None:
            p_correct = min(1.0, max(0.0, job.competence * (1.0 - 0.35 * row.difficulty)))
            correct += outcome_rng.random() < p_correct
    n = len(alerts)
    m = result.after_drain
    if len(reward_weights) != 5:
        raise ValueError("reward_weights must be (SLA, resolution, assignment, coordination, triage_error)")
    w_sla, w_resolution, w_quality, w_coord, w_triage = reward_weights
    triage_error_rate = (fp + fn) / n if n else 0.0
    reward = (w_sla * m.fraction_within_sla + w_resolution * (correct / n if n else 0.0)
              + w_quality * m.modeled_quality_per_admitted
              - w_coord * result.coordination_person_time - w_triage * triage_error_rate)
    return EpisodeResult(
        policy, result, n, tp / (tp + fn) if tp + fn else 0.0,
        fp / (fp + tn) if fp + tn else 0.0,
        sum(bool(a.routed.soctra_recommendation) for a in alerts) / n if n else 0.0,
        correct / n if n else 0.0, reward, result.coordination_person_time,
    )


class B4EpisodeEnv:
    """Sequential event-driven interface over resumable RQ1 allocation sessions."""
    actions = ("B0", "B1", "B2")
    organizational_actions = ("C0P0", "C0P1", "C1P0", "C1P1", "C2P0", "C2P1")
    OBSERVATION_ARRIVAL_SCALE = 200.0  # fixed arrivals per admission-horizon unit

    def __init__(self, config: ScenarioConfig, l1_analysts: Sequence[Analyst], l2_analysts: Sequence[Analyst],
                 l1_service_by_class: Mapping[object, float], l2_service_by_class: Mapping[object, float], **kwargs):
        self.config = config
        self.l1_analysts = tuple(l1_analysts)
        self.l2_analysts = tuple(l2_analysts)
        self.l1_services = dict(l1_service_by_class)
        self.l2_services = dict(l2_service_by_class)
        self.kwargs = kwargs
        self._weights = kwargs.get("sequential_reward_weights", (1.0, 0.25, 0.01, 0.10))
        if len(self._weights) != 4:
            raise ValueError("sequential_reward_weights must be (SLA, resolution, coordination, triage_error)")
        self.seed = 0
        self._done = False
        self._decisions = 0
        self._action_counts = {name: 0 for name in ("B0", "B1", "B2", "B3", "D1", "D1-L", "D1-S")}
        self._organization_action_counts = {name: 0 for name in self.organizational_actions}
        self._last_action_time = 0.0
        self._reward_since_action = 0.0
        self._recommendations_seen = 0
        self._recommendation_yes = 0
        self._triage_errors = 0
        self._observed_arrival_times: list[float] = []
        self._resolved: set[str] = set()
        self._resolution_correct: dict[str, bool] = {}
        self._evaluation: dict[str, SimulatedAlert] = {}
        self._l1 = None
        self._l2 = None
        self._admitted: tuple[SimulatedAlert, ...] = ()
        self._routing: dict[str, bool] = {}
        self._all_alerts: dict[str, Alert] = {}

    def reset(self, seed: int = 0):
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed must be an integer")
        from .rq1_allocation import AllocationSession
        self.seed = seed
        self._done = False
        self._decisions = 0
        self._action_counts = {name: 0 for name in ("B0", "B1", "B2", "B3", "D1", "D1-L", "D1-S")}
        self._organization_action_counts = {name: 0 for name in self.organizational_actions}
        self._last_action_time = 0.0
        self._reward_since_action = 0.0
        self._recommendations_seen = self._recommendation_yes = self._triage_errors = 0
        self._resolved = set()
        self._resolution_correct = {}
        self._routing = {}
        self._admitted = generate_alerts(self.config, seed)
        self._evaluation = {row.routed.alert.alert_id: row for row in self._admitted}
        self._all_alerts = {row.routed.alert.alert_id: row.routed.alert for row in self._admitted}
        l1_roster = _available_roster(self.l1_analysts, self.config.l1_availability_fraction, seed ^ 0x1A11)
        l2_roster = _available_roster(self.l2_analysts, self.config.l2_availability_fraction, seed ^ 0x2B22)
        self._l1 = AllocationSession(
            tuple(row.routed.alert for row in self._admitted), l1_roster,
            self.l1_services, admission_horizon=self.config.horizon,
            drain_period=self.kwargs.get("drain_period", 0.5), random_seed=seed,
            coordination_latency=self.kwargs.get("coordination_latency", 0.0),
            coordination_edge_cost=self.kwargs.get("coordination_edge_cost", 0.0),
            coordination_screen_cost=self.kwargs.get("coordination_screen_cost", 0.0),
            diagnostic_d1=self.kwargs.get("diagnostic_d1", False),
            b3_config=self.kwargs.get("b3_config", B3Config()),
            service_by_analyst_class=_restrict_service_map(self.kwargs.get("l1_service_by_analyst_class"), l1_roster),
            roster_schedule=self.kwargs.get("l1_roster_schedule", ()),
        )
        self._l2 = AllocationSession(
            (), l2_roster, self.l2_services,
            admission_horizon=self.config.horizon + self.kwargs.get("drain_period", 0.5),
            drain_period=0.0, random_seed=seed,
            coordination_latency=self.kwargs.get("coordination_latency", 0.0),
            coordination_edge_cost=self.kwargs.get("coordination_edge_cost", 0.0),
            coordination_screen_cost=self.kwargs.get("coordination_screen_cost", 0.0),
            diagnostic_d1=self.kwargs.get("diagnostic_d1", False),
            b3_config=self.kwargs.get("b3_config", B3Config()),
            service_by_analyst_class=_restrict_service_map(self.kwargs.get("l2_service_by_analyst_class"), l2_roster),
            roster_schedule=self.kwargs.get("l2_roster_schedule", ()),
        )
        self._advance_until_decision()
        return self._observation(), {"seed": seed, "decision_index": 0, "terminated": self._done}

    def step(self, action: int):
        if self._done:
            return self._observation(), 0.0, True, False, {"terminated": True, "decision_index": self._decisions}
        if not isinstance(action, int) or isinstance(action, bool) or action not in range(3):
            raise ValueError("action must be integer 0, 1 or 2 for B0, B1 or B2")
        return self._step_policy(self.actions[action])

    def step_fixed(self, policy: str):
        """Advance one decision using a fixed B0/B1/B2/B3 controller."""
        if policy not in {"B0", "B1", "B2", "B3", "D1", "D1-L", "D1-S"}:
            raise ValueError("fixed policy must be B0, B1, B2, B3, D1, D1-L or D1-S")
        return self._step_policy(policy)

    def step_fixed_organization(self, action: str):
        """Advance one event decision using one of the six fixed C/P actions."""
        if action not in self.organizational_actions:
            raise ValueError(f"organizational action must be one of {self.organizational_actions}")
        return self._step_organization(
            action, latency_override=self.kwargs.get("organization_latency_override")
        )

    def step_adaptive_organization(self):
        """Apply the preregistered observable rule and advance one decision."""
        action = adaptive_organizational_action(self._observation())
        return self._step_organization(action, adaptive=True,
                                       latency_override=self.kwargs.get("organization_latency_override"))

    def _step_policy(self, policy: str):
        prior_coordination = self._l1.coordination_person_time + self._l2.coordination_person_time
        prior_resource = self._l1.coordination_resource + self._l2.coordination_resource
        acted_pools = 0
        if self._l1.can_dispatch():
            self._l1.dispatch(policy)
            acted_pools += 1
        if self._l2.can_dispatch():
            self._l2.dispatch(policy)
            acted_pools += 1
        new_coordination = self._l1.coordination_person_time + self._l2.coordination_person_time - prior_coordination
        new_resource = self._l1.coordination_resource + self._l2.coordination_resource - prior_resource
        coordination_scale = max(1e-12, self.config.horizon * max(1, len(self._l1.analysts) + len(self._l2.analysts)))
        self._reward_since_action -= self._weights[2] * (new_coordination + new_resource) / coordination_scale
        self._decisions += 1
        self._action_counts[policy] += acted_pools
        self._advance_until_decision()
        reward = self._reward_since_action
        self._reward_since_action = 0.0
        elapsed = self._l1.now - self._last_action_time
        self._last_action_time = self._l1.now
        info = {"action": policy, "decision_index": self._decisions,
                "elapsed_time": elapsed, "completed_cumulative": len(self._resolved)}
        if self._done:
            info.update(self._terminal_info())
        return self._observation(), reward, self._done, False, info

    def _step_organization(self, action: str, *, adaptive: bool = False,
                            latency_override: float | None = None):
        prior_person_time = self._l1.coordination_person_time + self._l2.coordination_person_time
        prior_resource = self._l1.coordination_resource + self._l2.coordination_resource
        acted_pools = 0
        if self._l1.can_dispatch():
            self._l1.dispatch_organization(action, coordination_latency_override=latency_override)
            acted_pools += 1
        if self._l2.can_dispatch():
            self._l2.dispatch_organization(action, coordination_latency_override=latency_override)
            acted_pools += 1
        new_person_time = self._l1.coordination_person_time + self._l2.coordination_person_time - prior_person_time
        new_resource = self._l1.coordination_resource + self._l2.coordination_resource - prior_resource
        coordination_scale = max(1e-12, self.config.horizon * max(1, len(self._l1.analysts) + len(self._l2.analysts)))
        # Latency changes actual availability/SLA through event timing. The
        # reward cost separately charges coordination effort and analyst time
        # blocked during dispatch; no latency-only duplicate penalty is added.
        self._reward_since_action -= self._weights[2] * (new_person_time + new_resource) / coordination_scale
        self._decisions += 1
        self._organization_action_counts[action] += acted_pools
        self._advance_until_decision()
        reward = self._reward_since_action
        self._reward_since_action = 0.0
        elapsed = self._l1.now - self._last_action_time
        self._last_action_time = self._l1.now
        info = {"action": action, "adaptive": adaptive, "decision_index": self._decisions,
                "elapsed_time": elapsed, "completed_cumulative": len(self._resolved)}
        if self._done:
            info.update(self._terminal_info())
        return self._observation(), reward, self._done, False, info

    def _advance_until_decision(self) -> None:
        """Advance both existing pool sessions to the next joint event epoch."""
        while not self._done:
            event_times = [time for time in (self._l1.next_event_time(), self._l2.next_event_time())
                           if time is not None]
            if not event_times:
                self._done = True
                break
            now = min(event_times)
            self._l1.advance_to(now)
            self._l2.advance_to(now)
            # All L1 arrivals at this timestamp become observable before the action.
            for alert in self._l1.arrived_at_now:
                self._observed_arrival_times.append(alert.arrival)
                row = self._evaluation[alert.alert_id]
                recommendation = bool(row.routed.soctra_recommendation)
                self._recommendations_seen += 1
                self._recommendation_yes += int(recommendation)
                error = recommendation != row.true_escalation_need
                self._triage_errors += int(error)
                self._reward_since_action -= self._weights[3] * int(error)
                self._routing[alert.alert_id] = recommendation
            # L1 completion either resolves locally or injects one L2 arrival.
            for job in self._l1._finished_at_now:
                if self._routing.get(job.alert_id, False):
                    source = self._all_alerts[job.alert_id]
                    if job.completion < self._l2.drain_end:
                        self._l2.add_alert(Alert(job.alert_id, job.completion, source.task_class, source.deadline))
                else:
                    self._record_resolution(job)
            # Process L2 arrivals injected by same-instant L1 completions before dispatch.
            if self._l2.arrivals.get(now):
                self._l2.advance_to(now)
            for job in self._l2._finished_at_now:
                self._record_resolution(job)
            if self._l1.can_dispatch() or self._l2.can_dispatch():
                return
            if self._l1._finalized and self._l2._finalized:
                self._done = True

    def _record_resolution(self, job) -> None:
        if job.alert_id in self._resolved:
            raise RuntimeError("alert received more than one final resolution")
        row = self._evaluation[job.alert_id]
        rng_seed = int.from_bytes(sha256(f"{self.seed}:{job.alert_id}:{job.analyst_id}".encode()).digest()[:8], "big")
        rng = random.Random(rng_seed)
        probability = min(1.0, max(0.0, job.competence * (1.0 - 0.35 * row.difficulty)))
        correct = rng.random() < probability
        self._resolved.add(job.alert_id)
        self._resolution_correct[job.alert_id] = correct
        self._reward_since_action += self._weights[1] * int(correct)
        self._reward_since_action += self._weights[0] * int(job.completion <= row.routed.alert.deadline)

    def _observation(self) -> dict[str, float]:
        classes = tuple(self.config.classes)
        arrival_recent, arrival_previous, arrival_trend = self._arrival_trend()
        observed_count_scale = max(1.0, self.OBSERVATION_ARRIVAL_SCALE * self.config.horizon)
        result: dict[str, float] = {
            "time_fraction": min(1.0, self._l1.now / self.config.horizon),
            "l1_backlog_norm": min(1.0, len(self._l1.pending) / observed_count_scale),
            "l2_backlog_norm": min(1.0, len(self._l2.pending) / observed_count_scale),
            "l1_available_fraction": len(self._l1.available_analysts()) / max(1, len(self._l1.analysts)),
            "l2_available_fraction": len(self._l2.available_analysts()) / max(1, len(self._l2.analysts)),
            "l1_busy_fraction": len(self._l1.running) / max(1, len(self._l1.analysts)),
            "l2_busy_fraction": len(self._l2.running) / max(1, len(self._l2.analysts)),
            "coordination_cost_norm": min(1.0, (self._l1.coordination_person_time + self._l2.coordination_person_time) / max(1e-12, self.config.horizon * max(1, len(self._l1.analysts) + len(self._l2.analysts)))),
            "ai_recommendation_rate_so_far": self._recommendation_yes / self._recommendations_seen if self._recommendations_seen else 0.0,
            "ai_observations_norm": min(1.0, self._recommendations_seen / observed_count_scale),
            "deadline_pressure_l1": self._deadline_pressure(self._l1),
            "deadline_pressure_l2": self._deadline_pressure(self._l2),
            "arrival_rate_recent_norm": arrival_recent,
            "arrival_rate_previous_norm": arrival_previous,
            "arrival_rate_trend_norm": arrival_trend,
        }
        for stage, session in (("l1", self._l1), ("l2", self._l2)):
            counts = {k: sum(a.task_class == k for a in session.pending.values()) for k in classes}
            total = sum(counts.values())
            for k in classes:
                result[f"{stage}_queue_class_{k}"] = counts[k] / total if total else 0.0
        for stage, session in (("l1", self._l1), ("l2", self._l2)):
            class_dispersion = []
            measured_classes = 0
            available = session.available_analysts()
            for k in classes:
                eligible = [a.competence[k] for a in available if k in a.eligible_classes]
                result[f"{stage}_competence_{k}"] = sum(eligible) / len(eligible) if eligible else 0.0
                if len(eligible) >= 2:
                    mean = sum(eligible) / len(eligible)
                    sd = (sum((value - mean) ** 2 for value in eligible) / len(eligible)) ** 0.5
                    dispersion = min(1.0, sd / 0.5)
                    measured_classes += 1
                    class_dispersion.append(dispersion)
                else:
                    dispersion = 0.0
                result[f"{stage}_competence_dispersion_{k}"] = dispersion
            result[f"{stage}_competence_dispersion"] = (
                sum(class_dispersion) / len(class_dispersion) if class_dispersion else 0.0
            )
            result[f"{stage}_competence_dispersion_coverage"] = measured_classes / len(classes) if classes else 0.0
        return result

    def _arrival_trend(self) -> tuple[float, float, float]:
        """Two trailing causal rates and a normalized signed trend.

        Each window spans 0.15 of the admission horizon. Rates are normalized
        by the fixed scale 200 arrivals per horizon unit and clipped to [0,1].
        Only timestamps already incorporated at the current event are counted.
        The trend is 0.5 + 0.5*(recent-previous)/(recent+previous+epsilon).
        """
        now = self._l1.now
        width = 0.15 * self.config.horizon
        recent_start = max(0.0, now - width)
        previous_start = max(0.0, now - 2 * width)
        recent_exposure = max(0.0, now - recent_start)
        previous_exposure = max(0.0, recent_start - previous_start)
        recent_count = sum(recent_start < t <= now for t in self._observed_arrival_times)
        previous_count = sum(previous_start < t <= recent_start for t in self._observed_arrival_times)
        rate_scale = 200.0 / self.config.horizon
        recent_rate = recent_count / recent_exposure if recent_exposure else 0.0
        previous_rate = previous_count / previous_exposure if previous_exposure else 0.0
        recent_norm = min(1.0, recent_rate / rate_scale)
        previous_norm = min(1.0, previous_rate / rate_scale)
        trend_norm = 0.5 + 0.5 * (recent_rate - previous_rate) / (recent_rate + previous_rate + 1e-12)
        return recent_norm, previous_norm, min(1.0, max(0.0, trend_norm))

    def _deadline_pressure(self, session) -> float:
        if not session.pending:
            return 0.0
        service = session.services
        urgent = 0
        for alert in session.pending.values():
            fastest = min((session.individual_services.get(a.analyst_id, {}).get(alert.task_class, service[alert.task_class])
                           for a in session.available_analysts() if alert.task_class in a.eligible_classes),
                          default=service[alert.task_class])
            urgent += int(alert.deadline - session.now <= fastest)
        return urgent / len(session.pending)

    def _terminal_info(self) -> dict[str, object]:
        n = len(self._admitted)
        # SLA belongs to the final resolution stage. Escalated alerts have an
        # L1 assignment and an L2 assignment; counting the first matching job
        # would incorrectly credit the earlier L1 completion.
        final_jobs = {}
        for aid in self._resolved:
            final_session = self._l2 if self._routing.get(aid, False) else self._l1
            final_jobs[aid] = next(j for j in final_session.assignments if j.alert_id == aid)
        on_time = sum(
            self._evaluation[aid].routed.alert.deadline >= job.completion
            for aid, job in final_jobs.items()
        )
        l1_done = {j.alert_id for j in self._l1.assignments if j.completion <= self._l1.drain_end}
        l2_done = {j.alert_id for j in self._l2.assignments if j.completion <= self._l2.drain_end}
        routed_after_l1 = {aid for aid in l1_done if self._routing.get(aid, False)}
        return {"admitted": n, "completed": len(self._resolved), "completed_within_sla": on_time,
                "sla_fraction": on_time / n if n else 0.0, "pending": n - len(self._resolved),
                "l1_assignments": len(self._l1.assignments), "l2_assignments": len(self._l2.assignments),
                "l1_backlog": n - len(l1_done), "l2_backlog": len(routed_after_l1 - l2_done),
                "coordination_person_time": self._l1.coordination_person_time + self._l2.coordination_person_time,
                "coordination_blocked_person_time": self._l1.coordination_person_time + self._l2.coordination_person_time,
                "coordination_latency_total": self._l1.coordination_latency_total + self._l2.coordination_latency_total,
                "coordination_resource": self._l1.coordination_resource + self._l2.coordination_resource,
                "mean_resolution_accuracy": sum(self._resolution_correct.values()) / len(self._resolution_correct) if self._resolution_correct else 0.0,
                "resolution_success_per_admitted": sum(self._resolution_correct.values()) / n if n else 0.0,
                "triage_error_fraction": self._triage_errors / n if n else 0.0,
                "action_counts": dict(self._action_counts),
                "d1l_review_count": self._l1.d1l_review_count + self._l2.d1l_review_count,
                "d1s_review_count": self._l1.d1s_review_count + self._l2.d1s_review_count,
                "organization_action_counts": dict(self._organization_action_counts),
                "organization_switches": (
                    sum(a != b for a, b in zip(self._l1.organization_action_history, self._l1.organization_action_history[1:]))
                    + sum(a != b for a, b in zip(self._l2.organization_action_history, self._l2.organization_action_history[1:]))
                ),
                "b3_strategy_counts": {name: self._l1.strategy_counts[name] + self._l2.strategy_counts[name]
                                        for name in ("B0", "B1", "B2")}}


def adaptive_organizational_action(observation: Mapping[str, float]) -> str:
    """Frozen state-only rule: urgency, then queue stress and skill spread.

    Thresholds were specified before the episode comparison: deadline pressure
    >= .25 selects targeted deadline coordination; otherwise a normalized queue
    stress >= .04 selects global matching, with P1 only when visible competence
    dispersion is >= .20. Remaining states use local EDF.
    """
    required = {
        "l1_backlog_norm", "l2_backlog_norm", "l1_available_fraction",
        "l2_available_fraction", "deadline_pressure_l1", "deadline_pressure_l2",
        "l1_competence_dispersion", "l2_competence_dispersion",
    }
    missing = required - observation.keys()
    if missing:
        raise ValueError(f"adaptive rule missing observable fields: {sorted(missing)}")
    pressure = max(observation["deadline_pressure_l1"], observation["deadline_pressure_l2"])
    if pressure >= 0.25:
        return "C1P0"
    stress = max(
        observation["l1_backlog_norm"] / max(0.25, observation["l1_available_fraction"]),
        observation["l2_backlog_norm"] / max(0.25, observation["l2_available_fraction"]),
    )
    if stress >= 0.04:
        dispersion = max(observation["l1_competence_dispersion"], observation["l2_competence_dispersion"])
        return "C2P1" if dispersion >= 0.20 else "C2P0"
    return "C0P0"


def _categorical(rng: random.Random, probabilities: Sequence[float]) -> int:
    draw = rng.random()
    total = 0.0
    for i, p in enumerate(probabilities):
        total += p
        if draw < total:
            return i
    return len(probabilities) - 1


def _validate_config(config: ScenarioConfig) -> None:
    if config.horizon <= 0 or config.arrival_rate <= 0 or not config.classes:
        raise ValueError("horizon, arrival rate and classes must be positive/nonempty")
    if any(not 0 <= x <= 1 for x in (config.l1_availability_fraction, config.l2_availability_fraction)):
        raise ValueError("pool availability fractions must be within [0,1]")
    if len(config.class_probabilities) != len(config.classes) or len(config.escalation_probability_by_class) != len(config.classes):
        raise ValueError("class probability vectors must match classes")
    if any(p < 0 for p in config.class_probabilities) or abs(sum(config.class_probabilities) - 1) > 1e-9:
        raise ValueError("class probabilities must sum to one")
    if len(config.severity_probabilities) != 3 or any(p < 0 for p in config.severity_probabilities) or abs(sum(config.severity_probabilities) - 1) > 1e-9:
        raise ValueError("three nonnegative severity probabilities must sum to one")
    if len(config.severity_categories) != 3 or len(set(config.severity_categories)) != 3 or any(
            not isinstance(category, str) or not category for category in config.severity_categories):
        raise ValueError("severity_categories must contain three distinct nonempty names")
    if config.shift_class_probabilities is not None and (
        len(config.shift_class_probabilities) != len(config.classes)
        or any(p < 0 for p in config.shift_class_probabilities)
        or abs(sum(config.shift_class_probabilities) - 1) > 1e-9
    ):
        raise ValueError("shift class probabilities must match classes and sum to one")
    if any(not 0 <= p <= 1 for p in config.escalation_probability_by_class):
        raise ValueError("escalation probabilities must be within [0,1]")
    matrix = config.escalation_probability_by_class_severity
    if matrix is not None and (len(matrix) != len(config.classes) or any(len(row) != 3 for row in matrix) or any(not 0 <= p <= 1 for row in matrix for p in row)):
        raise ValueError("class-by-severity escalation matrix must be n_classes x 3 in [0,1]")
    for rates in (config.ai_sensitivity_by_severity, config.ai_false_positive_by_severity):
        if rates is not None and (len(rates) != 3 or any(not 0 <= p <= 1 for p in rates)):
            raise ValueError("severity-specific AI rates must have three values in [0,1]")
    if any(not 0 <= p <= 1 for p in (config.ai_sensitivity, config.ai_false_positive_rate)):
        raise ValueError("AI error rates must be within [0,1]")
    if set(dict(config.deadline_by_severity)) != set(config.severity_categories) or any(v <= 0 for _, v in config.deadline_by_severity):
        raise ValueError("positive deadlines are required for every configured severity")
    if config.burst_window and (config.burst_window[0] < 0 or config.burst_window[1] <= config.burst_window[0] or config.burst_window[2] <= 0):
        raise ValueError("invalid burst window")
    if config.shift_after is not None and not 0 <= config.shift_after < config.horizon:
        raise ValueError("shift_after must lie in [0, horizon)")
    if (config.arrival_rate_shift_after is None) != (config.arrival_rate_after is None):
        raise ValueError("arrival_rate_shift_after and arrival_rate_after must be configured together")
    if config.arrival_rate_shift_after is not None and not 0 <= config.arrival_rate_shift_after < config.horizon:
        raise ValueError("arrival_rate_shift_after must lie in [0, horizon)")
    if config.arrival_rate_after is not None and config.arrival_rate_after <= 0:
        raise ValueError("arrival_rate_after must be positive")
    if len(config.difficulty_beta) != 2 or any(x <= 0 for x in config.difficulty_beta):
        raise ValueError("difficulty beta shape parameters must be positive")
    if (config.reference_escalation_difficulty_threshold is not None and
            not 0 <= config.reference_escalation_difficulty_threshold <= 1):
        raise ValueError("reference escalation difficulty threshold must be within [0,1]")


def _available_roster(roster: Sequence[Analyst], fraction: float, seed: int) -> tuple[Analyst, ...]:
    if fraction >= 1:
        return tuple(roster)
    count = int(round(len(roster) * fraction))
    rng = random.Random(seed)
    chosen = set(rng.sample(range(len(roster)), count)) if count else set()
    return tuple(agent for index, agent in enumerate(roster) if index in chosen)


def _restrict_service_map(service_map, roster):
    if service_map is None:
        return None
    available = {agent.analyst_id for agent in roster}
    return {agent_id: values for agent_id, values in service_map.items() if agent_id in available}

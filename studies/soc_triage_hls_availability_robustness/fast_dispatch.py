"""Semantics-preserving D1 dispatch acceleration for long synthetic horizons.

This mirrors frozen ``hls.rq1_allocation._dispatch_d1``. It only replaces the
per-candidate linear lookup with an ID-indexed lookup; analyst shuffle, keys,
candidate order, review logic and RNG consumption remain identical.
"""
from hls.rq1_allocation import D1Candidate, D1Decision


def dispatch_d1_fast(free, pending, now, service_time, order_rng, trace=None,
                     *, queue_ids=(), occupied_specialists=(), local_correction=False,
                     selective_correction=False, review_counter=None):
    remaining = dict(pending)
    order = list(free)
    order_rng.shuffle(order)
    result = []
    for analyst in order:
        candidates = [alert for alert in remaining.values()
                      if alert.task_class in analyst.eligible_classes]
        if not candidates:
            continue

        def candidate_row(alert):
            duration = service_time(analyst, alert)
            slack = alert.deadline - now
            risk = min(1.0, max(0.0, (duration - slack) / duration))
            peer_count = sum(alert.task_class in peer.eligible_classes
                             for peer in free if peer.analyst_id != analyst.analyst_id)
            return D1Candidate(alert.alert_id, duration, alert.deadline, slack,
                               risk, analyst.competence[alert.task_class], peer_count,
                               now + duration <= alert.deadline)

        candidate_rows = tuple(candidate_row(alert) for alert in candidates)
        candidate_by_id = {row.alert_id: row for row in candidate_rows}

        def choice_key(alert):
            row = candidate_by_id[alert.alert_id]
            return (-row.deadline_risk, -row.own_competence, row.eligible_peers,
                    alert.deadline, alert.arrival, alert.alert_id)

        baseline_choice = min(candidates, key=choice_key)
        chosen = baseline_choice
        baseline_row = candidate_by_id[baseline_choice.alert_id]
        viable_alternatives = [alert for alert in candidates
                               if alert.alert_id != baseline_choice.alert_id
                               and candidate_by_id[alert.alert_id].projected_on_time]
        reviewed = bool(local_correction and not baseline_row.projected_on_time and viable_alternatives)
        if reviewed:
            chosen = min(viable_alternatives, key=lambda alert: (
                alert.deadline - now - service_time(analyst, alert),
                -analyst.competence[alert.task_class], alert.deadline,
                alert.arrival, alert.alert_id,
            ))
            if selective_correction:
                alternative_row = candidate_by_id[chosen.alert_id]
                reviewed = (alternative_row.own_competence >= baseline_row.own_competence
                            and alternative_row.service_duration <= baseline_row.service_duration)
                if not reviewed:
                    chosen = baseline_choice
            if reviewed and review_counter is not None:
                if selective_correction:
                    review_counter.d1s_review_count += 1
                else:
                    review_counter.d1l_review_count += 1
        duration = service_time(analyst, chosen)
        risk = min(1.0, max(0.0, (duration - (chosen.deadline - now)) / duration))
        peers = sum(chosen.task_class in peer.eligible_classes
                    for peer in free if peer.analyst_id != analyst.analyst_id)
        result.append((analyst, chosen))
        if trace is not None:
            trace.append(D1Decision(now, analyst.analyst_id, chosen.alert_id,
                                    risk, analyst.competence[chosen.task_class], peers,
                                    tuple(queue_ids), tuple(a.analyst_id for a in free),
                                    candidate_rows, tuple(occupied_specialists),
                                    baseline_choice.alert_id, reviewed))
        del remaining[chosen.alert_id]
    return result

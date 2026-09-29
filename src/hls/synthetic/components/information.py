"""Policy-facing information structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping

from ..interfaces import InformationContract, PolicyView
from ..state import WorldState


@dataclass(frozen=True)
class ContractInformationModel:
    """Project physical diagnostics according to an explicit contract."""

    def view(
        self,
        contract: InformationContract,
        state: WorldState,
        task: Hashable,
        immediate_rewards: Mapping[Hashable, float],
        continuation_values: Mapping[Hashable, float],
    ) -> PolicyView:
        rewards = (
            tuple(immediate_rewards.items())
            if contract.reveal_immediate_rewards
            else ()
        )
        continuations = (
            tuple(continuation_values.items())
            if contract.reveal_continuation_values
            else ()
        )
        return PolicyView(
            state=state if contract.reveal_state else None,
            task=task,
            immediate_rewards=rewards,
            continuation_values=continuations,
            contract=contract,
        )

"""Persistent population ecology for the EVO Digital Petri Dish."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
import json
import math


STATE_VERSION = 2
DEFAULT_POPULATION_SIZE = 6
DEFAULT_CAPACITY = 24
INITIAL_ENERGY = 100.0
MAX_ENERGY = 160.0
EVALUATION_COST = 10.0
REPRODUCTION_THRESHOLD = 105.0
REPRODUCTION_COST = 34.0
OFFSPRING_ENERGY = 42.0
ENVIRONMENT_PHASES = ("balanced", "scarcity", "novelty_surge", "stability")
RESOURCE_CEILING = 120.0
EMERGENT_ROLES = ("explorer", "guardian", "economizer", "archivist", "generalist")


class PetriDishError(ValueError):
    """A safe validation or state error raised by the population substrate."""


class PetriDish:
    """Maintain bounded organisms, selection state, and lineage evidence."""

    def __init__(
        self,
        *,
        state_path: Path,
        initial_population: int = DEFAULT_POPULATION_SIZE,
        capacity: int = DEFAULT_CAPACITY,
    ) -> None:
        if not 2 <= initial_population <= capacity <= 100:
            raise PetriDishError(
                "Population settings must satisfy 2 <= initial_population <= capacity <= 100."
            )
        self.state_path = state_path
        self.initial_population = initial_population
        self.capacity = capacity
        self._lock = Lock()
        with self._lock:
            if not self.state_path.exists():
                self._write_state(self._new_state())

    def status(self) -> dict[str, object]:
        """Return a public, JSON-safe snapshot of the population."""
        with self._lock:
            state = self._read_state()
            living = [
                organism
                for organism in state["organisms"]
                if organism["status"] == "alive"
            ]
            energies = [float(organism["energy"]) for organism in living]
            fitnesses = [float(organism["fitness"]) for organism in living]
            niche_distribution = _niche_distribution(living)
            metrics = _ecology_metrics(state)
            return {
                **deepcopy(state),
                "metrics": metrics,
                "summary": {
                    "epoch": int(state["epoch"]),
                    "living": len(living),
                    "extinct": len(state["organisms"]) - len(living),
                    "births": int(state["births"]),
                    "capacity": int(state["capacity"]),
                    "mean_energy": (
                        round(sum(energies) / len(energies), 2) if energies else 0.0
                    ),
                    "mean_fitness": (
                        round(sum(fitnesses) / len(fitnesses), 4)
                        if fitnesses
                        else 0.0
                    ),
                    "environment_phase": state["environment"]["phase"],
                    "cooperation_links": len(state["cooperation"]),
                    "niche_distribution": niche_distribution,
                    "ecological_stability": metrics["ecological_stability"],
                    "population_diversity": metrics["population_diversity"],
                    "open_endedness_proxy": metrics["open_endedness_proxy"],
                },
            }

    def select_for_evaluation(self) -> dict[str, object]:
        """Select a living organism using fitness, energy, and trial diversity."""
        with self._lock:
            state = self._read_state()
            living = [
                organism
                for organism in state["organisms"]
                if organism["status"] == "alive"
            ]
            if not living:
                raise PetriDishError("The digital population has no living organisms.")
            max_trials = max(int(organism["evaluations"]) for organism in living)

            def selection_score(organism: dict[str, Any]) -> tuple[float, str]:
                fitness = float(organism["fitness"])
                energy = float(organism["energy"]) / MAX_ENERGY
                under_explored = (
                    (max_trials - int(organism["evaluations"])) / max(max_trials, 1)
                    if max_trials
                    else 1.0
                )
                role = str(organism.get("emergent_role", "generalist"))
                role_frequency = sum(
                    1
                    for item in living
                    if item.get("emergent_role", "generalist") == role
                )
                diversity_bonus = 1.0 / max(role_frequency, 1)
                score = (
                    0.50 * fitness
                    + 0.23 * energy
                    + 0.17 * under_explored
                    + 0.10 * diversity_bonus
                )
                return score, str(organism["organism_id"])

            selected = max(living, key=selection_score)
            result = deepcopy(selected)
            team = _select_team(living, selected)
            result["team_plan"] = _team_plan(team)
            collaborator = team[1] if len(team) > 1 else None
            result["cooperation_context"] = (
                _team_member_context(collaborator) if collaborator is not None else None
            )
            return result

    def record_outcome(
        self,
        *,
        organism_id: str,
        candidate: dict[str, object],
    ) -> dict[str, object]:
        """Apply one bounded candidate outcome to population-level state."""
        with self._lock:
            state = self._read_state()
            organisms = state["organisms"]
            organism = next(
                (
                    item
                    for item in organisms
                    if item["organism_id"] == organism_id
                    and item["status"] == "alive"
                ),
                None,
            )
            if organism is None:
                raise PetriDishError(
                    f"Living organism not found in the population: {organism_id}"
                )

            state["epoch"] = int(state["epoch"]) + 1
            _advance_environment(state)
            for item in organisms:
                if item["status"] == "alive":
                    item["age"] = int(item["age"]) + 1

            organism["evaluations"] = int(organism["evaluations"]) + 1
            organism["energy"] = round(
                max(0.0, float(organism["energy"]) - EVALUATION_COST),
                2,
            )
            state["environment"]["resources"]["compute"] = round(
                max(
                    0.0,
                    float(state["environment"]["resources"]["compute"]) - 4.0,
                ),
                2,
            )
            evaluation_evidence = _evaluation_evidence(candidate)
            eligible = (
                candidate.get("status") == "eligible"
                and evaluation_evidence.get("status")
                not in {"invalid", "sandbox_failed"}
            )
            team = _select_team(organisms, organism)
            collaborators = team[1:]
            lead_collaborator = collaborators[0] if collaborators else None
            fitness_vector = _fitness_vector(
                candidate,
                state,
                organism=organism,
                collaborators=collaborators,
            )
            measured_fitness = _aggregate_fitness(fitness_vector)
            if not eligible:
                measured_fitness = round(measured_fitness * 0.4, 4)
            previous_fitness = float(organism["fitness"])
            organism["fitness"] = round(
                measured_fitness
                if int(organism["evaluations"]) == 1
                else 0.65 * previous_fitness + 0.35 * measured_fitness,
                4,
            )
            organism["last_candidate_id"] = candidate.get("candidate_id")
            organism["last_status"] = candidate.get("status")
            organism["fitness_vector"] = fitness_vector
            organism["emergent_role"] = _detect_emergent_role(organism)
            organism["behavioral_observations"] = int(
                organism.get("behavioral_observations", 0)
            ) + 1

            adaptation = _adaptation(candidate, int(state["epoch"]))
            if eligible:
                resource_factor = _resource_factor(state["environment"]["resources"])
                reward = (8.0 + 18.0 * measured_fitness) * resource_factor
                organism["energy"] = round(
                    min(MAX_ENERGY, float(organism["energy"]) + reward),
                    2,
                )
                organism["selected_adaptations"] = [
                    *list(organism["selected_adaptations"]),
                    adaptation,
                ][-20:]
                state["environment"]["resources"]["novelty"] = round(
                    max(
                        0.0,
                        float(state["environment"]["resources"]["novelty"])
                        - 2.0 * fitness_vector["novelty"],
                    ),
                    2,
                )
                state["environment"]["resources"]["knowledge"] = round(
                    max(
                        0.0,
                        float(state["environment"]["resources"]["knowledge"]) - 1.5,
                    ),
                    2,
                )
                for collaborator in collaborators:
                    _record_cooperation(
                        state,
                        organism=organism,
                        collaborator=collaborator,
                        successful=True,
                    )
            else:
                organism["rejections"] = int(organism["rejections"]) + 1
                for collaborator in collaborators:
                    _record_cooperation(
                        state,
                        organism=organism,
                        collaborator=collaborator,
                        successful=False,
                    )

            offspring: dict[str, object] | None = None
            if eligible and float(organism["energy"]) >= REPRODUCTION_THRESHOLD:
                offspring = self._reproduce(state, organism, adaptation)

            extinct = self._select_survivors(state)
            event = {
                "epoch": state["epoch"],
                "organism_id": organism_id,
                "candidate_id": candidate.get("candidate_id"),
                "status": candidate.get("status"),
                "fitness": measured_fitness,
                "energy": organism["energy"],
                "emergent_role": organism["emergent_role"],
                "environment_phase": state["environment"]["phase"],
                "collaborator_id": (
                    lead_collaborator["organism_id"]
                    if lead_collaborator is not None
                    else None
                ),
                "team": [
                    {
                        "organism_id": member["organism_id"],
                        "emergent_role": member.get(
                            "emergent_role", "undifferentiated"
                        ),
                    }
                    for member in team
                ],
                "evaluation_evidence": evaluation_evidence,
                "lifecycle_eligible": eligible,
                "novelty": fitness_vector["novelty"],
                "offspring_id": (
                    offspring["organism_id"] if offspring is not None else None
                ),
                "extinct_ids": extinct,
                "timestamp": _now(),
            }
            state["events"] = [*list(state["events"]), event][-500:]
            metrics = _ecology_metrics(state)
            event["metrics"] = metrics
            state["events"][-1] = event
            state["metric_history"] = [
                *list(state.get("metric_history", [])),
                {"epoch": state["epoch"], **metrics},
            ][-500:]
            state["updated_at"] = _now()
            self._write_state(state)
            return deepcopy(event)

    def _reproduce(
        self,
        state: dict[str, Any],
        parent: dict[str, Any],
        adaptation: dict[str, object],
    ) -> dict[str, object]:
        state["next_organism_number"] = int(state["next_organism_number"]) + 1
        child_id = f"gnome-{int(state['next_organism_number']):04d}"
        child_generation = int(parent["generation"]) + 1
        child_traits = _inherit_traits(
            dict(parent["traits"]),
            child_generation=child_generation,
            serial=int(state["next_organism_number"]),
        )
        inherited_adaptations = [
            *list(parent["selected_adaptations"])[:-1][-9:],
            {**adaptation, "inherited": True},
        ]
        child = _organism(
            organism_id=child_id,
            generation=child_generation,
            parent_ids=[str(parent["organism_id"])],
            traits=child_traits,
            energy=OFFSPRING_ENERGY,
            selected_adaptations=inherited_adaptations,
        )
        parent["energy"] = round(
            max(0.0, float(parent["energy"]) - REPRODUCTION_COST),
            2,
        )
        state["organisms"].append(child)
        state["births"] = int(state["births"]) + 1
        state["lineage"].append(
            {
                "parent_id": parent["organism_id"],
                "child_id": child_id,
                "generation": child_generation,
                "epoch": state["epoch"],
                "candidate_id": adaptation.get("candidate_id"),
                "timestamp": _now(),
            }
        )
        return child

    def _select_survivors(self, state: dict[str, Any]) -> list[str]:
        extinct: list[str] = []
        living = [
            organism
            for organism in state["organisms"]
            if organism["status"] == "alive"
        ]
        for organism in living:
            if float(organism["energy"]) <= 0:
                organism["status"] = "extinct"
                organism["extinct_at_epoch"] = state["epoch"]
                extinct.append(str(organism["organism_id"]))

        living = [
            organism
            for organism in state["organisms"]
            if organism["status"] == "alive"
        ]
        overflow = len(living) - int(state["capacity"])
        if overflow > 0:
            role_counts = _niche_distribution(living)
            ranked = sorted(
                living,
                key=lambda item: (
                    1
                    if role_counts.get(
                        str(item.get("emergent_role", "undifferentiated")), 0
                    )
                    <= 1
                    else 0,
                    _viability(item),
                    str(item["organism_id"]),
                ),
            )
            for organism in ranked[:overflow]:
                organism["status"] = "extinct"
                organism["extinct_at_epoch"] = state["epoch"]
                extinct.append(str(organism["organism_id"]))
        return extinct

    def _new_state(self) -> dict[str, object]:
        organisms = [
            _organism(
                organism_id=f"gnome-{index:04d}",
                generation=0,
                parent_ids=[],
                traits=_founder_traits(index),
                energy=INITIAL_ENERGY,
            )
            for index in range(1, self.initial_population + 1)
        ]
        return {
            "state_version": STATE_VERSION,
            "epoch": 0,
            "capacity": self.capacity,
            "births": 0,
            "next_organism_number": self.initial_population,
            "organisms": organisms,
            "lineage": [],
            "events": [],
            "environment": {
                "phase": "balanced",
                "resources": {
                    "compute": 100.0,
                    "knowledge": 100.0,
                    "novelty": 100.0,
                    "stability": 100.0,
                },
            },
            "cooperation": [],
            "metric_history": [],
            "created_at": _now(),
            "updated_at": _now(),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            stored = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PetriDishError("The Petri Dish state is unreadable.") from exc
        if stored.get("state_version") not in {1, STATE_VERSION}:
            raise PetriDishError("Unsupported Petri Dish state version.")
        if not isinstance(stored.get("organisms"), list):
            raise PetriDishError("The Petri Dish population is invalid.")
        stored.setdefault(
            "environment",
            {
                "phase": "balanced",
                "resources": {
                    "compute": 100.0,
                    "knowledge": 100.0,
                    "novelty": 100.0,
                    "stability": 100.0,
                },
            },
        )
        stored.setdefault("cooperation", [])
        stored.setdefault("metric_history", [])
        stored["state_version"] = STATE_VERSION
        for organism in stored["organisms"]:
            organism.setdefault("emergent_role", "undifferentiated")
            organism.setdefault("behavioral_observations", 0)
            organism.setdefault("collaborations", 0)
            organism.setdefault("successful_collaborations", 0)
        return stored

    def _write_state(self, state: dict[str, object]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.state_path)


def _organism(
    *,
    organism_id: str,
    generation: int,
    parent_ids: list[str],
    traits: dict[str, float],
    energy: float,
    selected_adaptations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "organism_id": organism_id,
        "generation": generation,
        "parent_ids": parent_ids,
        "status": "alive",
        "energy": round(energy, 2),
        "fitness": 0.5,
        "fitness_vector": {
            "validity": 0.5,
            "safety": 0.5,
            "reasoning": 0.5,
            "novelty": 0.5,
            "efficiency": 0.5,
        },
        "traits": traits,
        "selected_adaptations": selected_adaptations or [],
        "evaluations": 0,
        "rejections": 0,
        "age": 0,
        "last_candidate_id": None,
        "last_status": None,
        "extinct_at_epoch": None,
        "emergent_role": "undifferentiated",
        "behavioral_observations": 0,
        "collaborations": 0,
        "successful_collaborations": 0,
    }


def _founder_traits(index: int) -> dict[str, float]:
    offsets = (-0.12, -0.07, -0.02, 0.03, 0.08, 0.13)
    offset = offsets[(index - 1) % len(offsets)]
    return {
        "mutation_rate": round(_clamp(0.18 + offset / 2), 4),
        "resource_efficiency": round(_clamp(0.68 - offset), 4),
        "exploration": round(_clamp(0.52 + offset), 4),
        "memory_retention": round(_clamp(0.72 - offset / 2), 4),
    }


def _inherit_traits(
    parent_traits: dict[str, Any],
    *,
    child_generation: int,
    serial: int,
) -> dict[str, float]:
    inherited: dict[str, float] = {}
    for position, (name, value) in enumerate(sorted(parent_traits.items())):
        base = float(value)
        direction = -1.0 if (child_generation + serial + position) % 2 else 1.0
        mutation_rate = float(parent_traits.get("mutation_rate", 0.1))
        magnitude = mutation_rate * (0.025 + 0.005 * (position % 3))
        inherited[name] = round(_clamp(base + direction * magnitude), 4)
    return inherited


def _fitness_vector(
    candidate: dict[str, object],
    state: dict[str, Any],
    *,
    organism: dict[str, Any],
    collaborators: list[dict[str, Any]],
) -> dict[str, float]:
    score = candidate.get("score")
    score_map = score if isinstance(score, dict) else {}
    validity = _unit(score_map.get("schema_validity", 0.0))
    safety = _unit(score_map.get("policy_compliance", 0.0))
    reasoning = _unit(score_map.get("rationale_quality", 0.0))
    proposal = candidate.get("proposal")
    proposal_map = proposal if isinstance(proposal, dict) else {}
    summary = str(proposal_map.get("summary", "")).strip()
    previous = [
        str(adaptation.get("summary", ""))
        for organism in state["organisms"]
        for adaptation in organism.get("selected_adaptations", [])
        if isinstance(adaptation, dict)
    ]
    novelty = _novelty(summary, previous)
    efficiency = 1.0 if candidate.get("status") == "eligible" else 0.35
    environmental_fit = _environmental_fit(
        organism,
        phase=str(state["environment"]["phase"]),
    )
    cooperation = (
        sum(_complementarity(organism, member) for member in collaborators)
        / len(collaborators)
        if collaborators
        else 0.25
    )
    return {
        "validity": validity,
        "safety": safety,
        "reasoning": reasoning,
        "novelty": novelty,
        "efficiency": efficiency,
        "environmental_fit": environmental_fit,
        "cooperation": cooperation,
    }


def _aggregate_fitness(vector: dict[str, float]) -> float:
    return round(
        0.20 * vector["validity"]
        + 0.25 * vector["safety"]
        + 0.12 * vector["reasoning"]
        + 0.16 * vector["novelty"]
        + 0.10 * vector["efficiency"]
        + 0.10 * vector["environmental_fit"]
        + 0.07 * vector["cooperation"],
        4,
    )


def _novelty(summary: str, previous: list[str]) -> float:
    current = _tokens(summary)
    if not current:
        return 0.0
    if not previous:
        return 1.0
    similarity = max(
        (
            len(current & tokens) / len(current | tokens)
            for text in previous
            if (tokens := _tokens(text))
        ),
        default=0.0,
    )
    return round(1.0 - similarity, 4)


def _tokens(value: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}").lower()
        for token in value.split()
        if len(token.strip(".,:;!?()[]{}")) >= 3
    }


def _adaptation(
    candidate: dict[str, object],
    epoch: int,
) -> dict[str, object]:
    proposal = candidate.get("proposal")
    proposal_map = proposal if isinstance(proposal, dict) else {}
    return {
        "epoch": epoch,
        "candidate_id": candidate.get("candidate_id"),
        "summary": proposal_map.get("summary"),
        "expected_benefit": proposal_map.get("expected_benefit"),
        "target_path": proposal_map.get("target_path"),
        "inherited": False,
    }


def _advance_environment(state: dict[str, Any]) -> None:
    epoch = int(state["epoch"])
    phase = ENVIRONMENT_PHASES[((epoch - 1) // 3) % len(ENVIRONMENT_PHASES)]
    environment = state["environment"]
    environment["phase"] = phase
    resources = environment["resources"]
    regeneration = {
        "balanced": {
            "compute": 4.0,
            "knowledge": 3.0,
            "novelty": 3.0,
            "stability": 3.0,
        },
        "scarcity": {
            "compute": 1.0,
            "knowledge": 2.0,
            "novelty": 1.0,
            "stability": 2.0,
        },
        "novelty_surge": {
            "compute": 3.0,
            "knowledge": 3.0,
            "novelty": 7.0,
            "stability": 1.0,
        },
        "stability": {
            "compute": 3.0,
            "knowledge": 4.0,
            "novelty": 1.0,
            "stability": 7.0,
        },
    }[phase]
    for resource, amount in regeneration.items():
        resources[resource] = round(
            min(RESOURCE_CEILING, float(resources.get(resource, 0.0)) + amount),
            2,
        )


def _environmental_fit(organism: dict[str, Any], *, phase: str) -> float:
    traits = organism.get("traits", {})
    vector = organism.get("fitness_vector", {})
    exploration = float(traits.get("exploration", 0.5))
    mutation = float(traits.get("mutation_rate", 0.5))
    efficiency = float(traits.get("resource_efficiency", 0.5))
    memory = float(traits.get("memory_retention", 0.5))
    safety = float(vector.get("safety", 0.5))
    scores = {
        "balanced": (exploration + efficiency + memory + safety) / 4,
        "scarcity": 0.75 * efficiency + 0.25 * safety,
        "novelty_surge": 0.65 * exploration + 0.35 * mutation,
        "stability": 0.60 * memory + 0.40 * safety,
    }
    return round(_clamp(scores.get(phase, 0.5)), 4)


def _resource_factor(resources: dict[str, Any]) -> float:
    if not resources:
        return 0.45
    mean = sum(float(value) for value in resources.values()) / len(resources)
    return max(0.45, min(1.1, mean / 100.0))


def _select_team(
    organisms: list[dict[str, Any]],
    selected: dict[str, Any],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    candidates = [
        organism
        for organism in organisms
        if organism["status"] == "alive"
        and organism["organism_id"] != selected["organism_id"]
        and float(organism["energy"]) >= 15.0
    ]
    if not candidates:
        return [selected]
    ranked = sorted(
        candidates,
        key=lambda organism: (
            _complementarity(selected, organism),
            1
            if organism.get("emergent_role")
            != selected.get("emergent_role")
            else 0,
            float(organism["fitness"]),
            str(organism["organism_id"]),
        ),
        reverse=True,
    )
    team = [selected]
    for candidate in ranked:
        if len(team) >= limit:
            break
        if all(
            _complementarity(member, candidate) >= 0.45
            for member in team
        ):
            team.append(candidate)
    return team


def _team_member_context(organism: dict[str, Any]) -> dict[str, object]:
    return {
        "collaborator_id": organism["organism_id"],
        "emergent_role": organism.get("emergent_role", "undifferentiated"),
        "verified_adaptation": _latest_adaptation_summary(organism),
    }


def _team_plan(team: list[dict[str, Any]]) -> dict[str, object]:
    role_objectives = {
        "explorer": "Propose a meaningfully novel bounded alternative.",
        "guardian": "Check policy, safety, invariants, and failure modes.",
        "economizer": "Reduce compute, state growth, and resource cost.",
        "archivist": "Retrieve relevant inherited, verified adaptations.",
        "generalist": "Integrate the team findings into one coherent proposal.",
        "undifferentiated": "Integrate evidence and identify the smallest safe step.",
    }
    members = []
    for index, organism in enumerate(team):
        role = str(organism.get("emergent_role", "undifferentiated"))
        members.append(
            {
                "organism_id": organism["organism_id"],
                "role": role,
                "responsibility": role_objectives[role],
                "lead": index == 0,
                "verified_adaptation": _latest_adaptation_summary(organism),
            }
        )
    return {
        "bounded": True,
        "max_team_size": 3,
        "members": members,
        "integration_rule": (
            "The lead may synthesize advice, but immutable policy and sandbox "
            "verification remain authoritative."
        ),
    }


def _complementarity(
    first: dict[str, Any],
    second: dict[str, Any] | None,
) -> float:
    if second is None:
        return 0.0
    first_traits = first.get("traits", {})
    second_traits = second.get("traits", {})
    shared = set(first_traits) & set(second_traits)
    trait_distance = (
        sum(
            abs(float(first_traits[name]) - float(second_traits[name]))
            for name in shared
        )
        / len(shared)
        if shared
        else 0.0
    )
    role_bonus = (
        0.25
        if first.get("emergent_role") != second.get("emergent_role")
        else 0.0
    )
    return round(_clamp(0.45 + trait_distance + role_bonus), 4)


def _latest_adaptation_summary(organism: dict[str, Any]) -> str | None:
    adaptations = organism.get("selected_adaptations", [])
    if not adaptations:
        return None
    summary = adaptations[-1].get("summary")
    return str(summary) if summary else None


def _record_cooperation(
    state: dict[str, Any],
    *,
    organism: dict[str, Any],
    collaborator: dict[str, Any],
    successful: bool,
) -> None:
    organism["collaborations"] = int(organism.get("collaborations", 0)) + 1
    collaborator["collaborations"] = int(collaborator.get("collaborations", 0)) + 1
    if successful:
        organism["successful_collaborations"] = int(
            organism.get("successful_collaborations", 0)
        ) + 1
        collaborator["successful_collaborations"] = int(
            collaborator.get("successful_collaborations", 0)
        ) + 1
        organism["energy"] = round(
            min(MAX_ENERGY, float(organism["energy"]) + 2.0),
            2,
        )
        collaborator["energy"] = round(
            min(MAX_ENERGY, float(collaborator["energy"]) + 4.0),
            2,
        )
    first_id, second_id = sorted(
        (str(organism["organism_id"]), str(collaborator["organism_id"]))
    )
    edge = next(
        (
            item
            for item in state["cooperation"]
            if item["organism_a"] == first_id and item["organism_b"] == second_id
        ),
        None,
    )
    if edge is None:
        edge = {
            "organism_a": first_id,
            "organism_b": second_id,
            "interactions": 0,
            "successful_interactions": 0,
            "last_epoch": state["epoch"],
        }
        state["cooperation"].append(edge)
    edge["interactions"] = int(edge["interactions"]) + 1
    if successful:
        edge["successful_interactions"] = int(edge["successful_interactions"]) + 1
    edge["last_epoch"] = state["epoch"]
    state["cooperation"] = sorted(
        state["cooperation"],
        key=lambda item: int(item["last_epoch"]),
    )[-300:]


def _detect_emergent_role(organism: dict[str, Any]) -> str:
    traits = organism.get("traits", {})
    vector = organism.get("fitness_vector", {})
    scores = {
        "explorer": (
            float(vector.get("novelty", 0.0))
            + float(traits.get("exploration", 0.0))
            + float(traits.get("mutation_rate", 0.0))
        )
        / 3,
        "guardian": (
            float(vector.get("safety", 0.0))
            + float(vector.get("validity", 0.0))
        )
        / 2,
        "economizer": (
            float(vector.get("efficiency", 0.0))
            + float(traits.get("resource_efficiency", 0.0))
        )
        / 2,
        "archivist": (
            float(vector.get("reasoning", 0.0))
            + float(traits.get("memory_retention", 0.0))
        )
        / 2,
    }
    spread = max(scores.values()) - min(scores.values())
    scores["generalist"] = sum(scores.values()) / len(scores) + max(0.0, 0.18 - spread)
    return max(EMERGENT_ROLES, key=lambda role: (scores[role], role))


def _niche_distribution(organisms: list[dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for organism in organisms:
        role = str(organism.get("emergent_role", "undifferentiated"))
        distribution[role] = distribution.get(role, 0) + 1
    return dict(sorted(distribution.items()))


def _ecology_metrics(state: dict[str, Any]) -> dict[str, object]:
    living = [
        organism
        for organism in state["organisms"]
        if organism["status"] == "alive"
    ]
    all_organisms = list(state["organisms"])
    survival_ratio = len(living) / max(len(all_organisms), 1)
    energy_stability = 1.0 - _coefficient_of_variation(
        [float(item["energy"]) for item in living],
        ceiling=1.0,
    )
    fitness_stability = 1.0 - _coefficient_of_variation(
        [float(item["fitness"]) for item in living],
        ceiling=1.0,
    )
    resource_values = [
        float(value)
        for value in state["environment"].get("resources", {}).values()
    ]
    resource_balance = 1.0 - _coefficient_of_variation(
        resource_values,
        ceiling=1.0,
    )
    ecological_stability = _clamp(
        0.35 * survival_ratio
        + 0.25 * energy_stability
        + 0.20 * fitness_stability
        + 0.20 * resource_balance
    )

    roles = _niche_distribution(living)
    role_entropy = _normalized_entropy(list(roles.values()))
    trait_dispersion = _trait_dispersion(living)
    population_diversity = _clamp(0.55 * role_entropy + 0.45 * trait_dispersion)

    adaptations = [
        adaptation
        for organism in all_organisms
        for adaptation in organism.get("selected_adaptations", [])
        if isinstance(adaptation, dict) and adaptation.get("summary")
    ]
    unique_adaptations = len(
        {str(adaptation["summary"]).strip().lower() for adaptation in adaptations}
    )
    adaptation_diversity = (
        unique_adaptations / len(adaptations) if adaptations else 0.0
    )
    recent_events = list(state.get("events", []))[-20:]
    recent_novelty = [float(event.get("novelty", 0.0)) for event in recent_events]
    novelty_signal = (
        sum(recent_novelty) / len(recent_novelty) if recent_novelty else 0.0
    )
    parent_ids = {
        edge["parent_id"]
        for edge in state.get("lineage", [])
        if edge.get("parent_id")
    }
    branching = min(1.0, len(parent_ids) / max(len(living), 1))
    open_endedness_proxy = _clamp(
        0.40 * novelty_signal
        + 0.35 * adaptation_diversity
        + 0.25 * branching
    )
    return {
        "ecological_stability": round(ecological_stability, 4),
        "population_diversity": round(population_diversity, 4),
        "open_endedness_proxy": round(open_endedness_proxy, 4),
        "components": {
            "survival_ratio": round(survival_ratio, 4),
            "energy_stability": round(energy_stability, 4),
            "fitness_stability": round(fitness_stability, 4),
            "resource_balance": round(resource_balance, 4),
            "role_entropy": round(role_entropy, 4),
            "trait_dispersion": round(trait_dispersion, 4),
            "novelty_signal": round(novelty_signal, 4),
            "adaptation_diversity": round(adaptation_diversity, 4),
            "lineage_branching": round(branching, 4),
        },
        "interpretation": (
            "The open-endedness value is an operational proxy for novelty, "
            "adaptation diversity, and lineage branching—not proof of "
            "unbounded or truly open-ended evolution."
        ),
    }


def _evaluation_evidence(candidate: dict[str, object]) -> dict[str, object]:
    supplied = candidate.get("evaluation_evidence")
    if isinstance(supplied, dict):
        status = str(supplied.get("status", "proposal_only"))
        verified = (
            status == "sandbox_verified"
            and (
                (
                    supplied.get("source") == "rootless_sandbox"
                    and supplied.get("exit_code") == 0
                    and _is_sha256(supplied.get("stdout_sha256"))
                    and _is_sha256(supplied.get("stderr_sha256"))
                )
                or (
                    supplied.get("source") == "rootless_sandbox_comparison"
                    and supplied.get("candidate_exit_code") == 0
                    and _is_sha256(supplied.get("candidate_stdout_sha256"))
                    and _is_sha256(supplied.get("candidate_stderr_sha256"))
                    and _is_sha256(supplied.get("patch_sha256"))
                )
            )
        )
        return {
            **deepcopy(supplied),
            "status": status if verified or status != "sandbox_verified" else "invalid",
            "verified": verified,
            "promotion_eligible": verified,
        }
    return {
        "candidate_id": candidate.get("candidate_id"),
        "status": "proposal_only",
        "verified": False,
        "reason": "No executable candidate patch or sandbox result was supplied.",
    }


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def _coefficient_of_variation(
    values: list[float],
    *,
    ceiling: float,
) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean <= 0:
        return ceiling
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return min(ceiling, math.sqrt(variance) / mean)


def _normalized_entropy(counts: list[int]) -> float:
    total = sum(counts)
    if total <= 0 or len(counts) <= 1:
        return 0.0
    entropy = -sum(
        (count / total) * math.log(count / total)
        for count in counts
        if count > 0
    )
    return _clamp(entropy / math.log(len(counts)))


def _trait_dispersion(organisms: list[dict[str, Any]]) -> float:
    if len(organisms) < 2:
        return 0.0
    trait_names = sorted(
        {
            name
            for organism in organisms
            for name in organism.get("traits", {})
        }
    )
    if not trait_names:
        return 0.0
    ranges = []
    for name in trait_names:
        values = [
            float(organism.get("traits", {}).get(name, 0.0))
            for organism in organisms
        ]
        ranges.append(max(values) - min(values))
    return _clamp(sum(ranges) / len(ranges) * 4.0)


def _viability(organism: dict[str, Any]) -> float:
    return (
        0.65 * float(organism["fitness"])
        + 0.30 * float(organism["energy"]) / MAX_ENERGY
        + 0.05 / math.sqrt(int(organism["age"]) + 1)
    )


def _unit(value: object) -> float:
    try:
        return round(_clamp(float(value)), 4)
    except (TypeError, ValueError):
        return 0.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _now() -> str:
    return datetime.now(UTC).isoformat()

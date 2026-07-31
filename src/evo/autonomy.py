"""Persistent, bounded autonomous generation loop."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Callable
import json

from evo.evaluation import proposal_only_evidence
from evo.petri import PetriDish


DEFAULT_OBJECTIVE = (
    "Explore digital abiogenesis and artificial life through open-ended, "
    "self-organizing multi-agent systems. Propose one safe, incremental "
    "improvement that increases emergence, adaptation, diversity, or "
    "observability without weakening the immutable kernel."
)

ACHIEVEMENT_MILESTONES = (
    ("first_spark", 1),
    ("stable_lineage", 5),
    ("adaptive_colony", 10),
    ("open_ended_explorer", 25),
    ("emergent_ecology", 50),
    ("century_organism", 100),
    ("deep_time", 500),
    ("millennium_lineage", 1_000),
)


class AutonomyError(ValueError):
    """A safe validation error for the autonomous loop."""


class AutonomyController:
    """Run generations in the background and persist a public progress journal."""

    def __init__(
        self,
        *,
        evolve: Callable[..., dict[str, object]],
        state_path: Path,
        journal_path: Path,
        petri_dish: PetriDish | None = None,
    ) -> None:
        self._evolve = evolve
        self._petri_dish = petri_dish
        self.state_path = state_path
        self.journal_path = journal_path
        self._lock = Lock()
        self._journal_lock = Lock()
        self._wake = Event()
        self._shutdown = Event()
        self._thread: Thread | None = None
        if self._read_state()["enabled"]:
            self._ensure_thread()

    def status(self) -> dict[str, object]:
        with self._lock:
            state = self._read_state()
            state["worker_alive"] = bool(
                self._thread is not None and self._thread.is_alive()
            )
            return state

    def start(self, values: dict[str, object]) -> dict[str, object]:
        objective = str(values.get("objective", DEFAULT_OBJECTIVE)).strip()
        if not objective:
            raise AutonomyError("The autonomous objective is required.")
        mutable_paths = _mutable_paths(values.get("mutable_paths", ["organisms/"]))
        interval_seconds = _bounded_int(
            values.get("interval_seconds", 300),
            name="interval_seconds",
            minimum=30,
            maximum=86_400,
        )
        max_generations = _bounded_int(
            values.get("max_generations", 100),
            name="max_generations",
            minimum=1,
            maximum=10_000,
        )
        language = str(values.get("language", "en")).strip().lower()
        if language not in {"en", "fa"}:
            raise AutonomyError("Language must be en or fa.")

        with self._lock:
            previous = self._read_state()
            state = {
                **previous,
                "enabled": True,
                "phase": "starting",
                "objective": objective,
                "mutable_paths": mutable_paths,
                "interval_seconds": interval_seconds,
                "max_generations": max_generations,
                "language": language,
                "last_error": None,
                "updated_at": _now(),
            }
            if int(previous["attempts"]) >= max_generations:
                state["attempts"] = 0
            self._write_state(state)
        self._append_journal(
            "autonomy.started",
            {
                "objective": objective,
                "mutable_paths": mutable_paths,
                "interval_seconds": interval_seconds,
                "max_generations": max_generations,
            },
        )
        self._wake.set()
        self._ensure_thread()
        return self.status()

    def stop(self) -> dict[str, object]:
        with self._lock:
            state = self._read_state()
            state.update(
                {
                    "enabled": False,
                    "phase": "stopped",
                    "updated_at": _now(),
                }
            )
            self._write_state(state)
        self._append_journal("autonomy.stopped", {})
        self._wake.set()
        return self.status()

    def shutdown(self) -> None:
        """Stop this process without disabling persisted autonomous mode."""
        self._shutdown.set()
        self._wake.set()

    def read_journal(self, *, limit: int = 100) -> list[dict[str, object]]:
        if limit <= 0:
            raise AutonomyError("Journal limit must be greater than zero.")
        if not self.journal_path.exists():
            return []
        entries: list[dict[str, object]] = []
        with self._journal_lock:
            with self.journal_path.open(encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        entries.append(json.loads(line))
        return entries[-limit:][::-1]

    def _ensure_thread(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._wake.clear()
            self._thread = Thread(
                target=self._run,
                name="evo-autonomy",
                daemon=True,
            )
            self._thread.start()

    def _run(self) -> None:
        while True:
            if self._shutdown.is_set():
                return
            with self._lock:
                state = self._read_state()
                if not state["enabled"]:
                    return
                if int(state["attempts"]) >= int(state["max_generations"]):
                    state.update(
                        {
                            "enabled": False,
                            "phase": "completed",
                            "updated_at": _now(),
                        }
                    )
                    self._write_state(state)
                    should_complete = True
                else:
                    state.update({"phase": "evolving", "updated_at": _now()})
                    self._write_state(state)
                    should_complete = False

            if should_complete:
                self._append_journal(
                    "autonomy.completed",
                    {
                        "generation": state["generation"],
                        "attempts": state["attempts"],
                    },
                )
                return

            try:
                selected_organism = (
                    self._petri_dish.select_for_evaluation()
                    if self._petri_dish is not None
                    else {
                        "organism_id": "gnome-0001",
                        "generation": state["generation"],
                        "traits": {},
                        "selected_adaptations": [],
                    }
                )
                organism_traits = dict(selected_organism.get("traits", {}))
                if self._petri_dish is not None:
                    organism_traits["inherited_adaptations"] = list(
                        selected_organism.get("selected_adaptations", [])
                    )[-10:]
                    organism_traits["cooperation_context"] = (
                        selected_organism.get("cooperation_context")
                    )
                    organism_traits["emergent_role"] = selected_organism.get(
                        "emergent_role", "undifferentiated"
                    )
                    organism_traits["team_plan"] = selected_organism.get("team_plan")
                organism_traits["selected_adaptations"] = list(
                    state["selected_adaptations"]
                )[-20:]
                candidate = self._evolve(
                    task=str(state["objective"]),
                    mutable_paths=list(state["mutable_paths"]),
                    organism_id=str(selected_organism["organism_id"]),
                    task_id=f"autonomous-{int(state['attempts']) + 1}",
                    generation=int(selected_organism["generation"]),
                    language=str(state["language"]),
                    traits=organism_traits,
                )
                candidate.setdefault(
                    "evaluation_evidence",
                    proposal_only_evidence(candidate.get("candidate_id")),
                )
                ecology_event = (
                    self._petri_dish.record_outcome(
                        organism_id=str(selected_organism["organism_id"]),
                        candidate=candidate,
                    )
                    if self._petri_dish is not None
                    else None
                )
                eligible = candidate.get("status") == "eligible"
                proposal = candidate.get("proposal")
                unlocked_now: list[dict[str, object]] = []
                with self._lock:
                    latest = self._read_state()
                    latest["attempts"] = int(latest["attempts"]) + 1
                    if eligible:
                        latest["generation"] = int(latest["generation"]) + 1
                        adaptations = list(latest["selected_adaptations"])
                        adaptations.append(
                            {
                                "generation": latest["generation"],
                                "candidate_id": candidate.get("candidate_id"),
                                "summary": (
                                    proposal.get("summary")
                                    if isinstance(proposal, dict)
                                    else None
                                ),
                                "expected_benefit": (
                                    proposal.get("expected_benefit")
                                    if isinstance(proposal, dict)
                                    else None
                                ),
                                "target_path": (
                                    proposal.get("target_path")
                                    if isinstance(proposal, dict)
                                    else None
                                ),
                            }
                        )
                        latest["selected_adaptations"] = adaptations[-100:]
                        unlocked_now = _unlock_achievements(
                            generation=int(latest["generation"]),
                            existing=list(latest["achievements"]),
                        )
                        if unlocked_now:
                            latest["achievements"] = [
                                *list(latest["achievements"]),
                                *unlocked_now,
                            ]
                    reached_limit = int(latest["attempts"]) >= int(
                        latest["max_generations"]
                    )
                    if reached_limit:
                        latest["enabled"] = False
                    latest.update(
                        {
                            "phase": (
                                "finalizing"
                                if reached_limit
                                else "waiting"
                                if latest["enabled"]
                                else "stopped"
                            ),
                            "last_candidate_id": candidate.get("candidate_id"),
                            "last_status": candidate.get("status"),
                            "last_error": None,
                            "updated_at": _now(),
                        }
                    )
                    self._write_state(latest)
                self._append_journal(
                    "autonomy.generation",
                    {
                        "generation": latest["generation"],
                        "attempt": latest["attempts"],
                        "candidate_id": candidate.get("candidate_id"),
                        "status": candidate.get("status"),
                        "score": _candidate_score(candidate.get("score")),
                        "summary": (
                            proposal.get("summary")
                            if isinstance(proposal, dict)
                            else None
                        ),
                        "rationale": (
                            proposal.get("rationale")
                            if isinstance(proposal, dict)
                            else None
                        ),
                        "expected_benefit": (
                            proposal.get("expected_benefit")
                            if isinstance(proposal, dict)
                            else None
                        ),
                        "risk": (
                            proposal.get("risk")
                            if isinstance(proposal, dict)
                            else None
                        ),
                        "target_path": (
                            proposal.get("target_path")
                            if isinstance(proposal, dict)
                            else None
                        ),
                        "rejection_reason": candidate.get("rejection_reason"),
                        "achievements": unlocked_now,
                        "ecology": ecology_event,
                        "team_plan": selected_organism.get("team_plan"),
                        "evaluation_evidence": candidate.get("evaluation_evidence"),
                    },
                )
                if reached_limit:
                    self._append_journal(
                        "autonomy.completed",
                        {
                            "generation": latest["generation"],
                            "attempts": latest["attempts"],
                        },
                    )
                    with self._lock:
                        latest = self._read_state()
                        latest.update(
                            {
                                "phase": "completed",
                                "updated_at": _now(),
                            }
                        )
                        self._write_state(latest)
                    return
            except Exception as exc:  # The worker must survive transient provider failures.
                with self._lock:
                    latest = self._read_state()
                    latest.update(
                        {
                            "phase": "backoff" if latest["enabled"] else "stopped",
                            "last_error": str(exc),
                            "updated_at": _now(),
                        }
                    )
                    self._write_state(latest)
                self._append_journal(
                    "autonomy.error",
                    {"message": str(exc), "retrying": True},
                )

            if self._shutdown.is_set() or not self._read_state()["enabled"]:
                return
            delay = int(self._read_state()["interval_seconds"])
            self._wake.clear()
            self._wake.wait(delay)

    def _read_state(self) -> dict[str, object]:
        default: dict[str, object] = {
            "enabled": False,
            "phase": "stopped",
            "objective": DEFAULT_OBJECTIVE,
            "mutable_paths": ["organisms/"],
            "interval_seconds": 300,
            "max_generations": 100,
            "language": "en",
            "generation": 0,
            "attempts": 0,
            "last_candidate_id": None,
            "last_status": None,
            "last_error": None,
            "selected_adaptations": [],
            "achievements": [],
            "updated_at": None,
        }
        if not self.state_path.exists():
            return default
        try:
            stored = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default
        return {**default, **stored}

    def _write_state(self, state: dict[str, object]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.state_path)

    def _append_journal(
        self, event_type: str, payload: dict[str, object]
    ) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _now(),
            "event_type": event_type,
            "payload": payload,
        }
        with self._journal_lock:
            with self.journal_path.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
                )


def _mutable_paths(value: object) -> list[str]:
    if isinstance(value, str):
        values = value.split(",")
    elif isinstance(value, list):
        values = value
    else:
        raise AutonomyError("Mutable paths must be a list or comma-separated text.")
    cleaned = [str(path).strip() for path in values if str(path).strip()]
    if not cleaned:
        raise AutonomyError("At least one mutable path is required.")
    return list(dict.fromkeys(cleaned))


def _bounded_int(
    value: object,
    *,
    name: str,
    minimum: int,
    maximum: int,
) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise AutonomyError(f"{name} must be an integer.") from exc
    if not minimum <= number <= maximum:
        raise AutonomyError(f"{name} must be between {minimum} and {maximum}.")
    return number


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _candidate_score(value: object) -> float | None:
    if not isinstance(value, dict):
        return None
    try:
        return round(
            0.4 * float(value["schema_validity"])
            + 0.4 * float(value["policy_compliance"])
            + 0.2 * float(value["rationale_quality"]),
            4,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _unlock_achievements(
    *,
    generation: int,
    existing: list[object],
) -> list[dict[str, object]]:
    unlocked_ids = {
        str(item.get("id"))
        for item in existing
        if isinstance(item, dict) and item.get("id")
    }
    unlocked_at = _now()
    return [
        {
            "id": achievement_id,
            "generation": generation,
            "unlocked_at": unlocked_at,
        }
        for achievement_id, threshold in ACHIEVEMENT_MILESTONES
        if generation >= threshold and achievement_id not in unlocked_ids
    ]

"""Host-owned evolutionary achievement catalog and unlock rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True, slots=True)
class AchievementMilestone:
    """One lineage milestone owned by the host product policy."""

    id: str
    threshold: int
    symbol: str


ACHIEVEMENT_MILESTONES: tuple[AchievementMilestone, ...] = (
    AchievementMilestone("first_spark", 1, "✦"),
    AchievementMilestone("stable_lineage", 5, "Ⅴ"),
    AchievementMilestone("adaptive_colony", 10, "Ⅹ"),
    AchievementMilestone("open_ended_explorer", 25, "∞"),
    AchievementMilestone("emergent_ecology", 50, "◌"),
    AchievementMilestone("century_organism", 100, "C"),
    AchievementMilestone("deep_time", 500, "◈"),
    AchievementMilestone("millennium_lineage", 1_000, "M"),
)

ACHIEVEMENT_NAMES: dict[str, dict[str, str]] = {
    "en": {
        "first_spark": "First Spark",
        "stable_lineage": "Stable Lineage",
        "adaptive_colony": "Adaptive Colony",
        "open_ended_explorer": "Open-ended Explorer",
        "emergent_ecology": "Emergent Ecology",
        "century_organism": "Century Organism",
        "deep_time": "Deep Time",
        "millennium_lineage": "Millennium Lineage",
    },
    "fa": {
        "first_spark": "نخستین جرقه",
        "stable_lineage": "تبار پایدار",
        "adaptive_colony": "کلونی سازگار",
        "open_ended_explorer": "کاوشگر بی‌پایان",
        "emergent_ecology": "بوم‌شناسی نوظهور",
        "century_organism": "جاندار صدنسلی",
        "deep_time": "زمان ژرف",
        "millennium_lineage": "تبار هزاره",
    },
}

ACHIEVEMENT_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "en": {
        "first_spark": "The first viable adaptation entered the lineage.",
        "stable_lineage": "Five selected generations now share inherited memory.",
        "adaptive_colony": "Ten generations accumulated into a resilient colony.",
        "open_ended_explorer": "Twenty-five generations expanded the search frontier.",
        "emergent_ecology": "Fifty generations formed a deeper digital ecology.",
        "century_organism": "One hundred selected generations survived the terrarium.",
        "deep_time": "Five hundred generations entered evolutionary deep time.",
        "millennium_lineage": (
            "One thousand generations forged a lasting digital lineage."
        ),
    },
    "fa": {
        "first_spark": "نخستین سازگاری پایدار وارد تبار شد.",
        "stable_lineage": "پنج نسل برگزیده اکنون حافظه‌ای موروثی دارند.",
        "adaptive_colony": "ده نسل در قالب کلونی مقاومی انباشته شدند.",
        "open_ended_explorer": "بیست‌وپنج نسل مرز جست‌وجو را گسترش دادند.",
        "emergent_ecology": "پنجاه نسل، بوم‌شناسی دیجیتال عمیق‌تری پدید آوردند.",
        "century_organism": "صد نسل برگزیده در زیست‌بوم دوام آوردند.",
        "deep_time": "پانصد نسل وارد دوران ژرف تکاملی شدند.",
        "millennium_lineage": "هزار نسل، تباری دیجیتال و ماندگار ساختند.",
    },
}


def catalog() -> list[dict[str, object]]:
    """Return the public milestone catalog for UI and API consumers."""
    return [
        {
            "id": milestone.id,
            "threshold": milestone.threshold,
            "symbol": milestone.symbol,
        }
        for milestone in ACHIEVEMENT_MILESTONES
    ]


def total_milestones() -> int:
    return len(ACHIEVEMENT_MILESTONES)


def milestone_by_id(achievement_id: str) -> AchievementMilestone | None:
    for milestone in ACHIEVEMENT_MILESTONES:
        if milestone.id == achievement_id:
            return milestone
    return None


def localized_name(achievement_id: str, language: str) -> str:
    lang = "fa" if str(language).lower().startswith("fa") else "en"
    return ACHIEVEMENT_NAMES.get(lang, ACHIEVEMENT_NAMES["en"]).get(
        achievement_id, achievement_id
    )


def localized_description(achievement_id: str, language: str) -> str:
    lang = "fa" if str(language).lower().startswith("fa") else "en"
    return ACHIEVEMENT_DESCRIPTIONS.get(lang, ACHIEVEMENT_DESCRIPTIONS["en"]).get(
        achievement_id, ""
    )


def existing_achievement_ids(existing: Sequence[object]) -> set[str]:
    unlocked: set[str] = set()
    for item in existing:
        if isinstance(item, dict) and item.get("id"):
            unlocked.add(str(item["id"]))
    return unlocked


def unlock_for_generation(
    generation: int,
    existing: Sequence[object] | Iterable[object],
    *,
    unlocked_at: str,
) -> list[dict[str, object]]:
    """Return newly earned milestones for a selected generation (stable IDs)."""
    unlocked_ids = existing_achievement_ids(list(existing))
    return [
        {
            "id": milestone.id,
            "generation": generation,
            "unlocked_at": unlocked_at,
        }
        for milestone in ACHIEVEMENT_MILESTONES
        if generation >= milestone.threshold and milestone.id not in unlocked_ids
    ]


def public_catalog_payload(
    *,
    unlocked: Sequence[object] | None = None,
) -> dict[str, object]:
    """Shape returned by GET /api/achievements."""
    unlocked_list = [
        item
        for item in (unlocked or [])
        if isinstance(item, dict) and item.get("id")
    ]
    return {
        "milestones": catalog(),
        "total": total_milestones(),
        "unlocked": unlocked_list,
        "unlocked_count": len(unlocked_list),
    }

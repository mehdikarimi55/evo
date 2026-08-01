"""Storytelling narrative for the public evolution journal."""

from __future__ import annotations

from typing import Mapping, Sequence

from evo.achievements import (
    ACHIEVEMENT_DESCRIPTIONS,
    ACHIEVEMENT_NAMES,
)


class JournalStoryError(ValueError):
    """Raised when a journey story cannot be built."""


_ACHIEVEMENT_NAMES = ACHIEVEMENT_NAMES
_ACHIEVEMENT_DESCRIPTIONS = ACHIEVEMENT_DESCRIPTIONS

_STATUS_LABELS = {
    "en": {
        "eligible": "eligible",
        "rejected": "rejected",
        "proposed": "proposed",
    },
    "fa": {
        "eligible": "واجد شرایط",
        "rejected": "ردشده",
        "proposed": "پیشنهادشده",
    },
}

_EVIDENCE_LABELS = {
    "en": {
        "proposal_only": "proposal only",
        "sandbox_verified": "sandbox verified",
        "sandbox_failed": "sandbox failed",
        "invalid": "invalid evidence",
        "preserved_baseline": "baseline preserved",
        "repaired_baseline": "baseline repaired",
        "regression": "regression detected",
        "still_failing": "still failing",
        "patch_rejected": "patch rejected",
        "incomplete": "incomplete evaluation",
    },
    "fa": {
        "proposal_only": "فقط پیشنهاد",
        "sandbox_verified": "تأیید سندباکس",
        "sandbox_failed": "شکست سندباکس",
        "invalid": "شواهد نامعتبر",
        "preserved_baseline": "پایه حفظ شد",
        "repaired_baseline": "پایه ترمیم شد",
        "regression": "پسرفت تشخیص داده شد",
        "still_failing": "همچنان ناموفق",
        "patch_rejected": "پچ رد شد",
        "incomplete": "ارزیابی ناقص",
    },
}

_ROLE_LABELS = {
    "en": {
        "explorer": "explorer",
        "guardian": "guardian",
        "economizer": "economizer",
        "archivist": "archivist",
        "generalist": "generalist",
        "undifferentiated": "undifferentiated",
    },
    "fa": {
        "explorer": "کاوشگر",
        "guardian": "نگهبان",
        "economizer": "صرفه‌جو",
        "archivist": "بایگان",
        "generalist": "عمومی‌کار",
        "undifferentiated": "بدون تمایز",
    },
}

_PHASE_LABELS = {
    "en": {
        "balanced": "balanced",
        "scarcity": "scarcity",
        "novelty_surge": "novelty surge",
        "stability": "stability",
    },
    "fa": {
        "balanced": "متوازن",
        "scarcity": "کمبود",
        "novelty_surge": "موج تازگی",
        "stability": "پایداری",
    },
}

_SCORE_LABELS = {
    "en": {
        "schema_validity": "schema validity",
        "policy_compliance": "policy compliance",
        "rationale_quality": "rationale quality",
    },
    "fa": {
        "schema_validity": "اعتبار ساختار",
        "policy_compliance": "انطباق با سیاست",
        "rationale_quality": "کیفیت استدلال",
    },
}

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

_TEMPLATES = {
    "en": {
        "empty": (
            "The terrarium is quiet. No autonomous journey has been written yet."
        ),
        "prologue": (
            "This is the complete chronicle of the gnome’s evolution—from the "
            "first spark of autonomy through every recorded moment up to this "
            "point in the lineage record. What follows is the path as it was lived."
        ),
        "moment": "At {timestamp},",
        "started": (
            "the journey began. The gnome stepped into open-ended exploration "
            "with a guiding purpose: {objective}"
        ),
        "started_bounds": (
            "It would attempt up to {max_generations} generations, pausing "
            "{interval_seconds} seconds between each breath of search"
            "{paths}."
        ),
        "mutable_paths": ", watching over mutable paths {paths}",
        "generation_eligible": (
            "selected generation {generation} took root on attempt {attempt}. "
            "A candidate scored {score} and earned a place in the lineage. "
            "It proposed: {summary}"
        ),
        "generation_rejected": (
            "on attempt {attempt}, selected generation {generation} held its "
            "ground while a candidate was set aside with status “{status}” "
            "and score {score}. {detail}"
        ),
        "generation_other": (
            "attempt {attempt} touched selected generation {generation}. "
            "Status: {status}. Score: {score}. {detail}"
        ),
        "rationale": "The reasoning behind the proposal was: {rationale}",
        "target": "The intended target path was {path}.",
        "benefit": "The expected benefit was {benefit}.",
        "risk": "The noted risk was {risk}.",
        "evidence": "Evaluation evidence stood as “{status}”.",
        "team": "A cooperative team shaped the attempt: {members}.",
        "ecology": (
            "Around the dish, organism {organism_id} moved through ecological "
            "epoch {epoch} as a {role}, carrying fitness {fitness} and energy "
            "{energy}."
        ),
        "ecology_birth": " A new offspring, {offspring_id}, entered the lineage.",
        "ecology_extinct": " Extinctions claimed {ids}.",
        "ecology_phase": " The environment phase was {phase}.",
        "achievement": "A milestone marked the path: {name}—{description}",
        "error": (
            "the path darkened when the provider connection faltered: {message} "
            "The gnome would try again."
        ),
        "stopped": "autonomous exploration paused. The chronicle waited in stillness.",
        "completed": (
            "the generation limit was reached after {attempts} attempts, "
            "leaving selected generation {generation} as the high-water mark."
        ),
        "epilogue": (
            "And so the story stands at this checkpoint—{moments} recorded "
            "moments, {eligible} eligible adaptations, {rejected} setbacks, "
            "{achievements} milestone unlocks, and selected generation "
            "{generation} as the present crest of the lineage. The chronicle "
            "is neither finished nor forgotten."
        ),
        "fallback_objective": "explore digital abiogenesis without end",
        "fallback_summary": "an unnamed adaptation",
        "fallback_detail": "No further detail was recorded.",
        "fallback_message": "an unknown interruption",
        "achievement_fallback_desc": "A new evolutionary milestone unlocked.",
        "unknown_role": "undifferentiated",
        "title_prologue": "Opening of the chronicle",
        "title_started": "Autonomy begins",
        "title_generation": "Generation {generation}",
        "title_error": "Connection setback",
        "title_stopped": "Exploration paused",
        "title_completed": "Generation limit reached",
        "title_epilogue": "Checkpoint summary",
        "badge_eligible": "Eligible",
        "badge_rejected": "Rejected",
        "badge_proposed": "Proposed",
        "badge_attempt": "Attempt {attempt}",
        "badge_score": "Score {score}",
        "badge_evidence": "Evidence · {status}",
        "badge_epoch": "Epoch {epoch}",
        "badge_role": "{role}",
        "badge_birth": "Birth · {id}",
        "badge_achievement": "✦ {name}",
        "badge_generation": "Gen {generation}",
        "badge_moments": "{count} moments",
        "badge_eligible_count": "{count} eligible",
        "badge_rejected_count": "{count} setbacks",
        "badge_achievement_count": "{count} milestones",
        "tag_objective": "Objective",
        "tag_benefit": "Benefit",
        "tag_risk": "Risk",
        "tag_target": "Target",
        "tag_team": "Team",
        "tag_rationale": "Rationale",
        "tag_ecology": "Ecology",
        "column_features": "Features achieved",
        "column_skills": "Skills achieved",
        "feature_adaptation": "Adaptation",
        "feature_benefit": "Expected benefit",
        "feature_target": "Target path",
        "feature_milestone": "Milestone",
        "feature_birth": "Lineage birth",
        "feature_none": "No new feature recorded for this generation.",
        "skill_role": "Emergent role",
        "skill_fitness": "Measured fitness",
        "skill_energy": "Energy reserve",
        "skill_team": "Team skill · {role}",
        "skill_trait": "Trait · {name}",
        "skill_vector": "Capability · {name}",
        "skill_none": "No skill signal recorded for this generation.",
        "skill_validity": "Validity",
        "skill_safety": "Safety",
        "skill_reasoning": "Reasoning",
        "skill_novelty": "Novelty",
        "skill_efficiency": "Efficiency",
        "skill_environmental_fit": "Environmental fit",
        "skill_cooperation": "Cooperation",
        "trait_mutation_rate": "Mutation rate",
        "trait_resource_efficiency": "Resource efficiency",
        "trait_exploration": "Exploration",
        "trait_memory_retention": "Memory retention",
        "synopsis_empty": (
            "No journey has been written yet. The terrarium waits for its first spark."
        ),
        "synopsis_title": "Story so far",
        "synopsis_body": (
            "From “{objective}”, the gnome has lived {moments} recorded moments, "
            "secured {eligible} eligible adaptations, faced {rejected} setbacks, "
            "and unlocked {achievements} milestones—reaching selected generation "
            "{generation}.{latest}{achievements_line}{ending}"
        ),
        "synopsis_latest": " The latest selected adaptation: {summary}.",
        "synopsis_achievements": " Milestones earned: {names}.",
        "synopsis_running": " The chronicle continues.",
        "synopsis_paused": " Exploration is currently paused.",
        "synopsis_completed": " The generation limit has been reached.",
        "synopsis_error": " The path most recently darkened under a connection fault.",
    },
    "fa": {
        "empty": "زیست‌بوم خاموش است. هنوز روایتی از سفر خودکار نوشته نشده است.",
        "prologue": (
            "این روایت کامل تکامل گنوم است—از نخستین جرقه خودمختاری تا همهٔ "
            "لحظه‌های ثبت‌شده تا همین نقطه در دفتر تبار. آنچه می‌آید، مسیر "
            "همان‌گونه است که زیسته شد."
        ),
        "moment": "در {timestamp}،",
        "started": (
            "سفر آغاز شد. گنوم با هدفی روشن پا به کاوش بی‌پایان گذاشت: {objective}"
        ),
        "started_bounds": (
            "تا {max_generations} نسل تلاش می‌کرد و میان هر نفس جست‌وجو "
            "{interval_seconds} ثانیه درنگ می‌نمود{paths}."
        ),
        "mutable_paths": " و مسیرهای قابل‌تغییر {paths} را زیر نظر داشت",
        "generation_eligible": (
            "نسل برگزیده {generation} در تلاش {attempt} ریشه دواند. "
            "نامزدی با امتیاز {score} جای خود را در تبار یافت. "
            "پیشنهادش چنین بود: {summary}"
        ),
        "generation_rejected": (
            "در تلاش {attempt}، نسل برگزیده {generation} بر جای ماند "
            "و نامزدی با وضعیت «{status}» و امتیاز {score} کنار گذاشته شد. "
            "{detail}"
        ),
        "generation_other": (
            "تلاش {attempt} نسل برگزیده {generation} را لمس کرد. "
            "وضعیت: {status}. امتیاز: {score}. {detail}"
        ),
        "rationale": "منطق پیشنهاد چنین بود: {rationale}",
        "target": "مسیر هدف چنین بود: {path}.",
        "benefit": "فایده مورد انتظار چنین بود: {benefit}.",
        "risk": "ریسک ثبت‌شده چنین بود: {risk}.",
        "evidence": "شواهد ارزیابی در وضعیت «{status}» قرار داشت.",
        "team": "تیمی همکار این تلاش را شکل داد: {members}.",
        "ecology": (
            "در پتری‌دیش، جاندار {organism_id} در عصر بوم‌شناختی {epoch} "
            "به‌عنوان {role} گام برداشت؛ برازندگی‌اش {fitness} و انرژی‌اش "
            "{energy} بود."
        ),
        "ecology_birth": " زاده‌ای تازه، {offspring_id}، وارد تبار شد.",
        "ecology_extinct": " انقراض‌ها {ids} را گرفتند.",
        "ecology_phase": " فاز محیطی {phase} بود.",
        "achievement": "نشانه‌ای در مسیر درخشید: {name}—{description}",
        "error": (
            "مسیر تاریک شد؛ ارتباط با ارائه‌دهنده قطع شد: {message} "
            "گنوم دوباره تلاش می‌کند."
        ),
        "stopped": "کاوش خودکار آرام گرفت. روایت در سکوت منتظر ماند.",
        "completed": (
            "سقف نسل‌ها پس از {attempts} تلاش تکمیل شد و نسل برگزیده "
            "{generation} به‌عنوان نشانه‌ی بلندی مسیر باقی ماند."
        ),
        "epilogue": (
            "و داستان تا این ایستگاه ایستاده است—{moments} لحظهٔ ثبت‌شده، "
            "{eligible} سازگاری واجد شرایط، {rejected} ناکامی، "
            "{achievements} دستاورد، و نسل برگزیده {generation} به‌عنوان "
            "قلهٔ کنونی تبار. روایت نه تمام است و نه فراموش."
        ),
        "fallback_objective": "کاوش زایش دیجیتال بی‌پایان",
        "fallback_summary": "سازگاری بی‌نام",
        "fallback_detail": "جزئیات بیشتری ثبت نشده بود.",
        "fallback_message": "وقفه‌ای ناشناخته",
        "achievement_fallback_desc": "دستاورد تکاملی تازه‌ای گشوده شد.",
        "unknown_role": "بدون تمایز",
        "title_prologue": "آغاز روایت",
        "title_started": "آغاز خودمختاری",
        "title_generation": "نسل {generation}",
        "title_error": "وقفه در ارتباط",
        "title_stopped": "توقف کاوش",
        "title_completed": "تکمیل سقف نسل‌ها",
        "title_epilogue": "خلاصه ایستگاه",
        "badge_eligible": "واجد شرایط",
        "badge_rejected": "ردشده",
        "badge_proposed": "پیشنهادشده",
        "badge_attempt": "تلاش {attempt}",
        "badge_score": "امتیاز {score}",
        "badge_evidence": "شواهد · {status}",
        "badge_epoch": "عصر {epoch}",
        "badge_role": "{role}",
        "badge_birth": "تولد · {id}",
        "badge_achievement": "✦ {name}",
        "badge_generation": "نسل {generation}",
        "badge_moments": "{count} لحظه",
        "badge_eligible_count": "{count} واجد شرایط",
        "badge_rejected_count": "{count} ناکامی",
        "badge_achievement_count": "{count} دستاورد",
        "tag_objective": "هدف",
        "tag_benefit": "فایده",
        "tag_risk": "ریسک",
        "tag_target": "مسیر",
        "tag_team": "تیم",
        "tag_rationale": "منطق",
        "tag_ecology": "بوم‌شناسی",
        "column_features": "ویژگی‌های به‌دست‌آمده",
        "column_skills": "مهارت‌های به‌دست‌آمده",
        "feature_adaptation": "سازگاری",
        "feature_benefit": "فایدهٔ مورد انتظار",
        "feature_target": "مسیر هدف",
        "feature_milestone": "دستاورد",
        "feature_birth": "تولد تباری",
        "feature_none": "برای این نسل ویژگی تازه‌ای ثبت نشده است.",
        "skill_role": "نقش نوظهور",
        "skill_fitness": "برازش اندازه‌گیری‌شده",
        "skill_energy": "ذخیره انرژی",
        "skill_team": "مهارت تیمی · {role}",
        "skill_trait": "صفت · {name}",
        "skill_vector": "توانایی · {name}",
        "skill_none": "برای این نسل سیگنال مهارتی ثبت نشده است.",
        "skill_validity": "اعتبار",
        "skill_safety": "ایمنی",
        "skill_reasoning": "استدلال",
        "skill_novelty": "تازگی",
        "skill_efficiency": "کارایی",
        "skill_environmental_fit": "تناسب محیطی",
        "skill_cooperation": "همکاری",
        "trait_mutation_rate": "نرخ جهش",
        "trait_resource_efficiency": "کارایی منابع",
        "trait_exploration": "کاوش",
        "trait_memory_retention": "حفظ حافظه",
        "synopsis_empty": (
            "هنوز سفری نوشته نشده است. زیست‌بوم در انتظار نخستین جرقه است."
        ),
        "synopsis_title": "داستان تا اینجا",
        "synopsis_body": (
            "از هدف «{objective}»، گنوم {moments} لحظهٔ ثبت‌شده را زیسته، "
            "{eligible} سازگاری واجد شرایط به‌دست آورده، با {rejected} ناکامی "
            "روبه‌رو شده و {achievements} دستاورد گشوده است—تا نسل برگزیده "
            "{generation}.{latest}{achievements_line}{ending}"
        ),
        "synopsis_latest": " تازه‌ترین سازگاری برگزیده: {summary}.",
        "synopsis_achievements": " دستاوردهای کسب‌شده: {names}.",
        "synopsis_running": " روایت همچنان ادامه دارد.",
        "synopsis_paused": " کاوش در حال حاضر متوقف است.",
        "synopsis_completed": " سقف نسل‌ها تکمیل شده است.",
        "synopsis_error": " مسیر اخیراً با خطای ارتباط تاریک شده است.",
    },
}


def normalize_language(value: object) -> str:
    """Normalize UI/API language codes to ``en`` or ``fa``."""
    text = str(value or "en").strip().lower().replace("_", "-")
    if text.startswith("fa"):
        return "fa"
    return "en"


def normalize_timestamp(value: object) -> str:
    """Normalize journal timestamps, including query-string '+' → space cases."""
    text = str(value or "").strip()
    if "T" in text and " " in text and "+" not in text and text.count(":") >= 2:
        head, tail = text.rsplit(" ", 1)
        if tail and all(part.isdigit() for part in tail.split(":")):
            text = f"{head}+{tail}"
    return text


def entries_until(
    entries: Sequence[Mapping[str, object]],
    *,
    until_timestamp: str,
) -> list[dict[str, object]]:
    """Return journal entries from the beginning through ``until_timestamp``.

    ``entries`` may arrive newest-first (UI/API journal order). The returned
    list is chronological (oldest first) and inclusive of the matching stamp.
    """
    stamp = normalize_timestamp(until_timestamp)
    if not stamp:
        raise JournalStoryError("Journey cutoff timestamp is required.")
    matched = [
        dict(entry)
        for entry in entries
        if normalize_timestamp(entry.get("timestamp", "")) <= stamp
    ]
    if not matched:
        raise JournalStoryError("No journal entries exist at or before that point.")
    matched.sort(key=lambda entry: normalize_timestamp(entry.get("timestamp", "")))
    return matched


def narrate_journey(
    entries: Sequence[Mapping[str, object]],
    *,
    language: str = "en",
) -> str:
    """Compose a storytelling chronicle from chronological journal entries."""
    composed = compose_journey(entries, language=language)
    return str(composed["story"])


def compose_journey(
    entries: Sequence[Mapping[str, object]],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build narrative text plus structured chapters for rich UI rendering."""
    lang = normalize_language(language)
    templates = _TEMPLATES[lang]
    chronological = sorted(
        (dict(entry) for entry in entries),
        key=lambda entry: normalize_timestamp(entry.get("timestamp", "")),
    )
    if not chronological:
        empty = templates["empty"]
        synopsis = templates["synopsis_empty"]
        return {
            "story": empty,
            "synopsis": synopsis,
            "synopsis_title": templates["synopsis_title"],
            "chapters": [
                {
                    "kind": "empty",
                    "tone": "neutral",
                    "icon": "○",
                    "title": templates["title_prologue"],
                    "timestamp": None,
                    "body": empty,
                    "details": [],
                    "badges": [],
                    "tags": [],
                }
            ],
            "summary": {
                "moments": 0,
                "eligible": 0,
                "rejected": 0,
                "achievements": 0,
                "generation": 0,
            },
        }

    chapters: list[dict[str, object]] = [
        {
            "kind": "prologue",
            "tone": "prologue",
            "icon": "✧",
            "title": templates["title_prologue"],
            "timestamp": None,
            "body": templates["prologue"],
            "details": [],
            "badges": [],
            "tags": [],
        }
    ]
    eligible = 0
    rejected = 0
    achievements = 0
    generation = 0
    objective = templates["fallback_objective"]
    latest_summary = ""
    achievement_names: list[str] = []
    ending_key = "synopsis_running"
    for entry in chronological:
        payload = entry.get("payload")
        data = payload if isinstance(payload, Mapping) else {}
        event_type = str(entry.get("event_type", ""))
        if event_type == "autonomy.started":
            objective = _text(data.get("objective"), objective)
            ending_key = "synopsis_running"
        elif event_type == "autonomy.generation":
            status = str(data.get("status") or "")
            if status == "eligible":
                eligible += 1
                latest_summary = _text(
                    data.get("summary"), latest_summary or templates["fallback_summary"]
                )
            elif status == "rejected":
                rejected += 1
            generation = max(generation, int(data.get("generation") or 0))
            for achievement in data.get("achievements") or []:
                if not isinstance(achievement, Mapping):
                    continue
                achievement_id = str(achievement.get("id", ""))
                name = _ACHIEVEMENT_NAMES[lang].get(
                    achievement_id, achievement_id or ""
                )
                if name and name not in achievement_names:
                    achievement_names.append(name)
                achievements += 1
            ending_key = "synopsis_running"
        elif event_type == "autonomy.completed":
            generation = max(generation, int(data.get("generation") or 0))
            ending_key = "synopsis_completed"
        elif event_type == "autonomy.stopped":
            ending_key = "synopsis_paused"
        elif event_type == "autonomy.error":
            ending_key = "synopsis_error"
        chapter = _chapter_for_entry(entry, lang=lang, templates=templates)
        if chapter:
            chapters.append(chapter)

    epilogue_body = templates["epilogue"].format(
        moments=_localize_value(len(chronological), lang),
        eligible=_localize_value(eligible, lang),
        rejected=_localize_value(rejected, lang),
        achievements=_localize_value(achievements, lang),
        generation=_localize_value(generation, lang),
    )
    chapters.append(
        {
            "kind": "epilogue",
            "tone": "epilogue",
            "icon": "◎",
            "title": templates["title_epilogue"],
            "timestamp": None,
            "body": epilogue_body,
            "details": [],
            "badges": [
                {
                    "label": templates["badge_moments"].format(
                        count=_localize_value(len(chronological), lang)
                    ),
                    "tone": "info",
                },
                {
                    "label": templates["badge_eligible_count"].format(
                        count=_localize_value(eligible, lang)
                    ),
                    "tone": "success",
                },
                {
                    "label": templates["badge_rejected_count"].format(
                        count=_localize_value(rejected, lang)
                    ),
                    "tone": "danger",
                },
                {
                    "label": templates["badge_achievement_count"].format(
                        count=_localize_value(achievements, lang)
                    ),
                    "tone": "amber",
                },
                {
                    "label": templates["badge_generation"].format(
                        generation=_localize_value(generation, lang)
                    ),
                    "tone": "info",
                },
            ],
            "tags": [],
        }
    )
    story = "\n\n".join(
        str(chapter.get("body") or "")
        for chapter in chapters
        if chapter.get("body")
    )
    latest_line = (
        templates["synopsis_latest"].format(summary=latest_summary)
        if latest_summary
        else ""
    )
    achievements_line = (
        templates["synopsis_achievements"].format(names=", ".join(achievement_names))
        if achievement_names
        else ""
    )
    synopsis = templates["synopsis_body"].format(
        objective=objective,
        moments=_localize_value(len(chronological), lang),
        eligible=_localize_value(eligible, lang),
        rejected=_localize_value(rejected, lang),
        achievements=_localize_value(achievements, lang),
        generation=_localize_value(generation, lang),
        latest=latest_line,
        achievements_line=achievements_line,
        ending=templates[ending_key],
    )
    return {
        "story": story,
        "synopsis": synopsis,
        "synopsis_title": templates["synopsis_title"],
        "chapters": chapters,
        "summary": {
            "moments": len(chronological),
            "eligible": eligible,
            "rejected": rejected,
            "achievements": achievements,
            "generation": generation,
        },
    }


def build_journey_story(
    entries: Sequence[Mapping[str, object]],
    *,
    until_timestamp: str,
    language: str = "en",
) -> dict[str, object]:
    """Build a public journey story cut off at a journal timestamp."""
    selected = entries_until(entries, until_timestamp=until_timestamp)
    composed = compose_journey(selected, language=language)
    return {
        "until_timestamp": normalize_timestamp(until_timestamp),
        "language": normalize_language(language),
        "entry_count": len(selected),
        "story": composed["story"],
        "synopsis": composed["synopsis"],
        "synopsis_title": composed["synopsis_title"],
        "chapters": composed["chapters"],
        "summary": composed["summary"],
    }


def _chapter_for_entry(
    entry: Mapping[str, object],
    *,
    lang: str,
    templates: Mapping[str, str],
) -> dict[str, object] | None:
    event_type = str(entry.get("event_type", ""))
    payload = entry.get("payload")
    data = payload if isinstance(payload, Mapping) else {}
    timestamp = _text(entry.get("timestamp"), "—")
    body = _narrate_entry(entry, lang=lang, templates=templates)
    if not body:
        return None

    if event_type == "autonomy.started":
        tags = []
        objective = _text(data.get("objective"), "")
        if objective:
            tags.append({"label": templates["tag_objective"], "tone": "info"})
        paths = data.get("mutable_paths") or []
        if isinstance(paths, list):
            for path in paths[:4]:
                tags.append({"label": str(path), "tone": "muted"})
        badges = []
        if data.get("max_generations") is not None:
            badges.append(
                {
                    "label": templates["badge_generation"].format(
                        generation=_localize_value(data.get("max_generations"), lang)
                    ),
                    "tone": "info",
                }
            )
        return {
            "kind": "started",
            "tone": "start",
            "icon": "◈",
            "title": templates["title_started"],
            "timestamp": timestamp,
            "body": body,
            "details": [],
            "badges": badges,
            "tags": tags,
        }

    if event_type == "autonomy.stopped":
        return {
            "kind": "stopped",
            "tone": "neutral",
            "icon": "❚❚",
            "title": templates["title_stopped"],
            "timestamp": timestamp,
            "body": body,
            "details": [],
            "badges": [],
            "tags": [],
        }

    if event_type == "autonomy.completed":
        return {
            "kind": "completed",
            "tone": "epilogue",
            "icon": "★",
            "title": templates["title_completed"],
            "timestamp": timestamp,
            "body": body,
            "details": [],
            "badges": [
                {
                    "label": templates["badge_generation"].format(
                        generation=_localize_value(data.get("generation", "—"), lang)
                    ),
                    "tone": "info",
                }
            ],
            "tags": [],
        }

    if event_type == "autonomy.error":
        return {
            "kind": "error",
            "tone": "danger",
            "icon": "⚠",
            "title": templates["title_error"],
            "timestamp": timestamp,
            "body": body,
            "details": [],
            "badges": [{"label": templates["badge_rejected"], "tone": "danger"}],
            "tags": [],
        }

    if event_type == "autonomy.generation":
        return _generation_chapter(
            data, body=body, timestamp=timestamp, lang=lang, templates=templates
        )

    return None


def _generation_chapter(
    data: Mapping[str, object],
    *,
    body: str,
    timestamp: str,
    lang: str,
    templates: Mapping[str, str],
) -> dict[str, object]:
    status = str(data.get("status") or "—")
    generation = _localize_value(data.get("generation", "—"), lang)
    attempt = _localize_value(data.get("attempt", "—"), lang)
    score = _format_score(data.get("score"), lang=lang)
    if status == "eligible":
        tone = "success"
        status_badge = {
            "label": templates["badge_eligible"],
            "tone": "success",
        }
    elif status == "rejected":
        tone = "danger"
        status_badge = {
            "label": templates["badge_rejected"],
            "tone": "danger",
        }
    else:
        tone = "warning"
        status_badge = {
            "label": templates["badge_proposed"],
            "tone": "amber",
        }

    badges = [
        status_badge,
        {
            "label": templates["badge_attempt"].format(attempt=attempt),
            "tone": "muted",
        },
        {
            "label": templates["badge_score"].format(score=score),
            "tone": "info",
        },
    ]
    tags: list[dict[str, str]] = []

    if _text(data.get("rationale"), ""):
        tags.append({"label": templates["tag_rationale"], "tone": "info"})
    target = _text(data.get("target_path"), "")
    if target:
        tags.append({"label": f"{templates['tag_target']}: {target}", "tone": "muted"})
    if _text(data.get("expected_benefit"), ""):
        tags.append({"label": templates["tag_benefit"], "tone": "success"})
    if _text(data.get("risk"), ""):
        tags.append({"label": templates["tag_risk"], "tone": "danger"})

    evidence = data.get("evaluation_evidence")
    if isinstance(evidence, Mapping) and evidence.get("status"):
        badges.append(
            {
                "label": templates["badge_evidence"].format(
                    status=_localize_evidence(evidence.get("status"), lang)
                ),
                "tone": "info",
            }
        )

    team_plan = data.get("team_plan")
    if isinstance(team_plan, Mapping):
        members = team_plan.get("members") or []
        if isinstance(members, list) and members:
            tags.append({"label": templates["tag_team"], "tone": "amber"})

    ecology = data.get("ecology")
    if isinstance(ecology, Mapping):
        tags.append({"label": templates["tag_ecology"], "tone": "info"})
        if ecology.get("epoch") is not None:
            badges.append(
                {
                    "label": templates["badge_epoch"].format(
                        epoch=_localize_value(ecology.get("epoch"), lang)
                    ),
                    "tone": "info",
                }
            )
        if ecology.get("emergent_role"):
            badges.append(
                {
                    "label": templates["badge_role"].format(
                        role=_localize_role(ecology.get("emergent_role"), lang, templates)
                    ),
                    "tone": "amber",
                }
            )
        if ecology.get("offspring_id"):
            badges.append(
                {
                    "label": templates["badge_birth"].format(
                        id=_localize_value(ecology.get("offspring_id"), lang)
                    ),
                    "tone": "success",
                }
            )

    for achievement in data.get("achievements") or []:
        if not isinstance(achievement, Mapping):
            continue
        achievement_id = str(achievement.get("id", ""))
        name = _ACHIEVEMENT_NAMES[lang].get(achievement_id, achievement_id or "—")
        badges.append(
            {
                "label": templates["badge_achievement"].format(name=name),
                "tone": "amber",
            }
        )

    features, skills = _generation_gains(data, lang=lang, templates=templates)
    return {
        "kind": "generation",
        "tone": tone,
        "icon": "●" if status == "eligible" else "◇" if status == "rejected" else "○",
        "title": templates["title_generation"].format(generation=generation),
        "timestamp": timestamp,
        "body": body,
        "details": [],
        "badges": badges,
        "tags": tags,
        "features": features,
        "skills": skills,
        "columns": {
            "features_title": templates["column_features"],
            "skills_title": templates["column_skills"],
        },
    }


def _generation_gains(
    data: Mapping[str, object],
    *,
    lang: str,
    templates: Mapping[str, str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Build per-generation feature and skill columns for the journey UI."""
    features: list[dict[str, str]] = []
    skills: list[dict[str, str]] = []

    summary = _text(data.get("summary"), "")
    if summary:
        features.append(
            {
                "kind": "adaptation",
                "title": templates["feature_adaptation"],
                "detail": summary,
            }
        )
    benefit = _text(data.get("expected_benefit"), "")
    if benefit:
        features.append(
            {
                "kind": "benefit",
                "title": templates["feature_benefit"],
                "detail": benefit,
            }
        )
    target = _text(data.get("target_path"), "")
    if target:
        features.append(
            {
                "kind": "target",
                "title": templates["feature_target"],
                "detail": target,
            }
        )
    for achievement in data.get("achievements") or []:
        if not isinstance(achievement, Mapping):
            continue
        achievement_id = str(achievement.get("id", ""))
        name = _ACHIEVEMENT_NAMES[lang].get(achievement_id, achievement_id or "—")
        description = _ACHIEVEMENT_DESCRIPTIONS[lang].get(achievement_id, "")
        features.append(
            {
                "kind": "milestone",
                "title": templates["feature_milestone"],
                "detail": f"{name} — {description}".strip(" —"),
            }
        )

    ecology = data.get("ecology")
    ecology_data = ecology if isinstance(ecology, Mapping) else {}
    offspring = _text(ecology_data.get("offspring_id"), "")
    if offspring:
        features.append(
            {
                "kind": "birth",
                "title": templates["feature_birth"],
                "detail": offspring,
            }
        )

    role = ecology_data.get("emergent_role")
    if role:
        skills.append(
            {
                "kind": "role",
                "title": templates["skill_role"],
                "detail": _localize_role(role, lang, templates),
            }
        )
    if ecology_data.get("fitness") is not None:
        skills.append(
            {
                "kind": "fitness",
                "title": templates["skill_fitness"],
                "detail": _localize_value(ecology_data.get("fitness"), lang),
            }
        )
    if ecology_data.get("energy") is not None:
        skills.append(
            {
                "kind": "energy",
                "title": templates["skill_energy"],
                "detail": _localize_value(ecology_data.get("energy"), lang),
            }
        )

    vector = ecology_data.get("fitness_vector")
    if isinstance(vector, Mapping):
        for key in (
            "validity",
            "safety",
            "reasoning",
            "novelty",
            "efficiency",
            "environmental_fit",
            "cooperation",
        ):
            if key not in vector:
                continue
            skills.append(
                {
                    "kind": f"vector_{key}",
                    "title": templates["skill_vector"].format(
                        name=templates.get(f"skill_{key}", key)
                    ),
                    "detail": _localize_value(
                        round(float(vector[key]), 3),
                        lang,
                    ),
                }
            )

    traits = ecology_data.get("traits")
    if isinstance(traits, Mapping):
        for name, value in traits.items():
            if not isinstance(value, (int, float)):
                continue
            trait_key = f"trait_{name}"
            skills.append(
                {
                    "kind": f"trait_{name}",
                    "title": templates["skill_trait"].format(
                        name=templates.get(trait_key, str(name).replace("_", " "))
                    ),
                    "detail": _localize_value(round(float(value), 3), lang),
                }
            )

    team_plan = data.get("team_plan")
    if isinstance(team_plan, Mapping):
        members = team_plan.get("members") or []
        if isinstance(members, list):
            for member in members:
                if not isinstance(member, Mapping):
                    continue
                member_role = _localize_role(
                    member.get("role") or member.get("emergent_role"),
                    lang,
                    templates,
                )
                responsibility = _text(member.get("responsibility"), "")
                detail = responsibility or _text(
                    member.get("verified_adaptation"), ""
                )
                if not detail:
                    continue
                skills.append(
                    {
                        "kind": "team",
                        "title": templates["skill_team"].format(role=member_role),
                        "detail": detail,
                    }
                )

    if not features:
        features.append(
            {
                "kind": "empty",
                "title": templates["column_features"],
                "detail": templates["feature_none"],
            }
        )
    if not skills:
        skills.append(
            {
                "kind": "empty",
                "title": templates["column_skills"],
                "detail": templates["skill_none"],
            }
        )
    return features, skills


def _narrate_entry(
    entry: Mapping[str, object],
    *,
    lang: str,
    templates: Mapping[str, str],
) -> str:
    event_type = str(entry.get("event_type", ""))
    payload = entry.get("payload")
    data = payload if isinstance(payload, Mapping) else {}
    moment = templates["moment"].format(
        timestamp=_text(entry.get("timestamp"), "—")
    )

    if event_type == "autonomy.started":
        paths = data.get("mutable_paths") or []
        path_text = ""
        if isinstance(paths, list) and paths:
            path_text = templates["mutable_paths"].format(
                paths=", ".join(str(item) for item in paths)
            )
        parts = [
            f"{moment} "
            + templates["started"].format(
                objective=_text(data.get("objective"), templates["fallback_objective"])
            )
        ]
        if data.get("max_generations") is not None or data.get("interval_seconds") is not None:
            parts.append(
                templates["started_bounds"].format(
                    max_generations=_localize_value(data.get("max_generations", "—"), lang),
                    interval_seconds=_localize_value(
                        data.get("interval_seconds", "—"), lang
                    ),
                    paths=path_text,
                )
            )
        return " ".join(parts)

    if event_type == "autonomy.stopped":
        return f"{moment} {templates['stopped']}"

    if event_type == "autonomy.completed":
        return f"{moment} " + templates["completed"].format(
            generation=_localize_value(data.get("generation", "—"), lang),
            attempts=_localize_value(data.get("attempts", "—"), lang),
        )

    if event_type == "autonomy.error":
        return f"{moment} " + templates["error"].format(
            message=_text(data.get("message"), templates["fallback_message"])
        )

    if event_type == "autonomy.generation":
        return f"{moment} " + _narrate_generation(
            data, lang=lang, templates=templates
        )

    return ""


def _narrate_generation(
    data: Mapping[str, object],
    *,
    lang: str,
    templates: Mapping[str, str],
) -> str:
    status = str(data.get("status") or "—")
    status_label = _localize_status(status, lang)
    summary = _text(data.get("summary"), "")
    rejection = _text(data.get("rejection_reason"), "")
    detail = summary or rejection or templates["fallback_detail"]
    generation = _localize_value(data.get("generation", "—"), lang)
    attempt = _localize_value(data.get("attempt", "—"), lang)
    score = _format_score(data.get("score"), lang=lang)

    if status == "eligible":
        body = templates["generation_eligible"].format(
            generation=generation,
            attempt=attempt,
            score=score,
            summary=summary or templates["fallback_summary"],
        )
    elif status == "rejected":
        body = templates["generation_rejected"].format(
            generation=generation,
            attempt=attempt,
            status=status_label,
            score=score,
            detail=detail,
        )
    else:
        body = templates["generation_other"].format(
            generation=generation,
            attempt=attempt,
            status=status_label,
            score=score,
            detail=detail,
        )

    extras: list[str] = [body]
    rationale = _text(data.get("rationale"), "")
    if rationale:
        extras.append(templates["rationale"].format(rationale=rationale))
    target = _text(data.get("target_path"), "")
    if target:
        extras.append(templates["target"].format(path=target))
    benefit = _text(data.get("expected_benefit"), "")
    if benefit:
        extras.append(templates["benefit"].format(benefit=benefit))
    risk = _text(data.get("risk"), "")
    if risk:
        extras.append(templates["risk"].format(risk=risk))

    evidence = data.get("evaluation_evidence")
    if isinstance(evidence, Mapping) and evidence.get("status"):
        extras.append(
            templates["evidence"].format(
                status=_localize_evidence(evidence.get("status"), lang)
            )
        )

    team_plan = data.get("team_plan")
    if isinstance(team_plan, Mapping):
        members = team_plan.get("members") or []
        if isinstance(members, list) and members:
            labels = []
            for member in members:
                if not isinstance(member, Mapping):
                    continue
                role = _localize_role(
                    member.get("role", templates["unknown_role"]),
                    lang,
                    templates,
                )
                labels.append(f"{member.get('organism_id', '—')} ({role})")
            if labels:
                extras.append(templates["team"].format(members=", ".join(labels)))

    ecology = data.get("ecology")
    if isinstance(ecology, Mapping):
        role = _localize_role(
            ecology.get("emergent_role"), lang, templates
        )
        ecology_line = templates["ecology"].format(
            organism_id=_localize_value(ecology.get("organism_id", "—"), lang),
            epoch=_localize_value(ecology.get("epoch", "—"), lang),
            role=role,
            fitness=_localize_value(ecology.get("fitness", "—"), lang),
            energy=_localize_value(ecology.get("energy", "—"), lang),
        )
        if ecology.get("environment_phase"):
            ecology_line += templates["ecology_phase"].format(
                phase=_localize_phase(ecology.get("environment_phase"), lang)
            )
        offspring_id = ecology.get("offspring_id")
        if offspring_id:
            ecology_line += templates["ecology_birth"].format(
                offspring_id=_localize_value(offspring_id, lang)
            )
        extinct_ids = ecology.get("extinct_ids") or []
        if isinstance(extinct_ids, list) and extinct_ids:
            ecology_line += templates["ecology_extinct"].format(
                ids=", ".join(_localize_value(item, lang) for item in extinct_ids)
            )
        extras.append(ecology_line)

    for achievement in data.get("achievements") or []:
        if not isinstance(achievement, Mapping):
            continue
        achievement_id = str(achievement.get("id", ""))
        names = _ACHIEVEMENT_NAMES[lang]
        descriptions = _ACHIEVEMENT_DESCRIPTIONS[lang]
        extras.append(
            templates["achievement"].format(
                name=names.get(achievement_id, achievement_id or "—"),
                description=descriptions.get(
                    achievement_id, templates["achievement_fallback_desc"]
                ),
            )
        )
    return " ".join(extras)


def _format_score(value: object, *, lang: str = "en") -> str:
    if isinstance(value, Mapping):
        parts = []
        labels = _SCORE_LABELS.get(lang, _SCORE_LABELS["en"])
        for key, item in value.items():
            label = labels.get(str(key), str(key))
            parts.append(f"{label}={_localize_value(item, lang)}")
        return ", ".join(parts) if parts else "—"
    if value is None:
        return "—"
    return _localize_value(value, lang)


def _localize_status(value: object, lang: str) -> str:
    key = str(value or "").strip()
    return _STATUS_LABELS.get(lang, _STATUS_LABELS["en"]).get(key, key or "—")


def _localize_evidence(value: object, lang: str) -> str:
    key = str(value or "").strip()
    return _EVIDENCE_LABELS.get(lang, _EVIDENCE_LABELS["en"]).get(
        key, key or "—"
    )


def _localize_role(
    value: object, lang: str, templates: Mapping[str, str]
) -> str:
    key = str(value or "").strip() or "undifferentiated"
    return _ROLE_LABELS.get(lang, _ROLE_LABELS["en"]).get(
        key, templates.get("unknown_role", key)
    )


def _localize_phase(value: object, lang: str) -> str:
    key = str(value or "").strip()
    return _PHASE_LABELS.get(lang, _PHASE_LABELS["en"]).get(key, key or "—")


def _localize_value(value: object, lang: str) -> str:
    text = "—" if value is None else str(value)
    if lang != "fa":
        return text
    return text.translate(_PERSIAN_DIGITS)


def _text(value: object, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback

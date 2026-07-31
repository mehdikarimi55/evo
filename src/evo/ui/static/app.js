const DEFAULTS = {
  groq: {
    model: "openai/gpt-oss-20b",
    base_url: "https://api.groq.com/openai/v1",
  },
  nvidia: {
    model: "meta/llama-3.1-70b-instruct",
    base_url: "https://integrate.api.nvidia.com/v1",
  },
};

const I18N = {
  en: {
    pageTitle: "EVO | Evolutionary Terrarium",
    heroEyebrow: "DIGITAL ABIOGENESIS · SPECIMEN 0001",
    heroTitle: "Evolutionary Terrarium",
    heroDescription: "A living laboratory where bounded intelligence accumulates memory, selects adaptations, and grows a digital lineage.",
    heroNote: "Observe emergence in real time. Every generation leaves evidence.",
    openWorkspace: "Enter the terrarium",
    checkConfig: "Check life support",
    lifeSupport: "LIFE SUPPORT",
    environmentControls: "ENVIRONMENT CONTROLS",
    manualSelection: "MANUAL SELECTION",
    openEndedLoop: "OPEN-ENDED LOOP",
    lineageRecord: "LINEAGE RECORD",
    immutableMemory: "IMMUTABLE MEMORY",
    hostStatus: "Host status",
    loadingConfig: "Loading configuration…",
    settings: "Settings",
    settingsDescription: "Provider credentials remain on the host. Raw keys are never displayed.",
    provider: "Provider",
    model: "Model",
    baseUrl: "Base URL",
    apiKey: "API key",
    keepSavedKey: "Leave blank to keep the saved key",
    enterNewKey: "Enter a newly generated provider key",
    maxInputTokens: "Maximum input tokens",
    maxOutputTokens: "Maximum output tokens",
    maxCalls: "Maximum calls per run",
    requestTimeout: "Request timeout (seconds)",
    saveSettings: "Save settings",
    probeProvider: "Probe provider",
    runGeneration: "Run one generation",
    generationDescription: "Produces an eligible or rejected candidate. Nothing is applied to the repository.",
    objective: "Objective",
    objectivePlaceholder: "Improve input validation without changing public behavior.",
    mutablePaths: "Mutable paths",
    evolve: "Evolve",
    thinking: "Thinking…",
    autonomousEvolution: "Autonomous evolution",
    autonomyDescription: "Continuously explores digital abiogenesis and open-ended artificial life while the app is running.",
    autonomousObjective: "Autonomous objective",
    autonomyObjectivePlaceholder: "Explore digital abiogenesis and open-ended artificial life...",
    intervalSeconds: "Interval between generations (seconds)",
    generationLimit: "Generation attempt limit",
    autonomyMutablePaths: "Autonomous mutable paths",
    autonomySafety: "Autonomous mode consumes provider API quota. It evaluates and selects proposals, but never merges, deploys, purchases, or changes the immutable kernel.",
    startAutonomy: "Start autonomous evolution",
    stopAutonomy: "Stop",
    evolutionJournal: "Evolution journal",
    journalDescription: "A public-facing chronicle of this gnome’s selected generations, adaptations, and setbacks.",
    achievements: "Evolutionary achievements",
    noAchievements: "No achievements unlocked yet.",
    achievementUnlocked: "Achievement unlocked",
    noEvolutionYet: "No autonomous evolution has been recorded yet.",
    auditTrail: "Audit trail",
    auditDescription: "Redacted local events from `.evo/audit.jsonl`.",
    search: "Search",
    searchPlaceholder: "Search audit, status, and settings…",
    action: "Action",
    when: "When",
    event: "Event",
    status: "Status",
    score: "Score",
    noAuditEvents: "No audit events yet.",
    requestFailed: "Request failed",
    invalidServerResponse: "The server returned an invalid response",
    configured: "Configured",
    yes: "Yes",
    no: "No",
    envFile: "Environment file",
    present: "Present",
    missing: "Missing",
    callsPerRun: "Calls per run",
    configurationIncomplete: "Configuration incomplete",
    inspectEvent: "Inspect event",
    proposed: "Proposed",
    eligible: "Eligible",
    rejected: "Rejected",
    generationCompleted: "Generation completed",
    mutationApplied: "Mutation applied",
    mutationRejected: "Mutation rejected",
    settingsSaved: "Settings saved to .env.local",
    configurationValid: "Configuration is valid",
    waitingCandidate: "Waiting for the model to propose a candidate…",
    candidateStatus: "Candidate status",
    evoError: "EVO error",
    candidateId: "candidate_id",
    genomeFingerprint: "genome_fingerprint",
    proposal: "proposal",
    targetPath: "target_path",
    summary: "summary",
    rationale: "rationale",
    expectedBenefit: "expected_benefit",
    risk: "risk",
    schemaValidity: "schema_validity",
    policyCompliance: "policy_compliance",
    rationaleQuality: "rationale_quality",
    rejectionReason: "rejection_reason",
    phase: "Phase",
    generation: "Selected generation",
    attempts: "Attempts",
    nextInterval: "Interval",
    stopped: "Stopped",
    starting: "Starting",
    evolving: "Evolving",
    waiting: "Waiting",
    backoff: "Waiting for connection",
    completed: "Completed",
    finalizing: "Finalizing",
    enabled: "Running",
    autonomyStarted: "Autonomous evolution started",
    autonomyStopped: "Autonomous evolution stopped",
    journalStarted: "Autonomous exploration started",
    journalStopped: "Autonomous exploration stopped",
    journalCompleted: "Generation limit reached",
    journalError: "Provider connection interrupted",
    journalGeneration: "Generation",
    attempt: "Attempt",
    seconds: "seconds",
    retrying: "The gnome will retry automatically.",
    achievement_first_spark: "First Spark",
    achievement_first_spark_desc: "The first viable adaptation entered the lineage.",
    achievement_stable_lineage: "Stable Lineage",
    achievement_stable_lineage_desc: "Five selected generations now share inherited memory.",
    achievement_adaptive_colony: "Adaptive Colony",
    achievement_adaptive_colony_desc: "Ten generations accumulated into a resilient colony.",
    achievement_open_ended_explorer: "Open-ended Explorer",
    achievement_open_ended_explorer_desc: "Twenty-five generations expanded the search frontier.",
    achievement_emergent_ecology: "Emergent Ecology",
    achievement_emergent_ecology_desc: "Fifty generations formed a deeper digital ecology.",
    achievement_century_organism: "Century Organism",
    achievement_century_organism_desc: "One hundred selected generations survived the terrarium.",
    achievement_deep_time: "Deep Time",
    achievement_deep_time_desc: "Five hundred generations entered evolutionary deep time.",
    achievement_millennium_lineage: "Millennium Lineage",
    achievement_millennium_lineage_desc: "One thousand generations formed an enduring digital lineage.",
  },
  fa: {
    pageTitle: "EVO | زیست‌بوم تکاملی",
    heroEyebrow: "زایش دیجیتال · نمونه ۰۰۰۱",
    heroTitle: "زیست‌بوم تکاملی",
    heroDescription: "آزمایشگاهی زنده که در آن هوش کنترل‌شده حافظه می‌اندوزد، سازگاری‌ها را برمی‌گزیند و یک تبار دیجیتال می‌پروراند.",
    heroNote: "ظهور رفتار را زنده تماشا کنید؛ هر نسل، مدرکی از خود به جا می‌گذارد.",
    openWorkspace: "ورود به زیست‌بوم",
    checkConfig: "بررسی پشتیبانی حیات",
    lifeSupport: "پشتیبانی حیات",
    environmentControls: "کنترل‌های محیط",
    manualSelection: "گزینش دستی",
    openEndedLoop: "چرخه بی‌پایان",
    lineageRecord: "روایت تبار",
    immutableMemory: "حافظه تغییرناپذیر",
    hostStatus: "وضعیت میزبان",
    loadingConfig: "در حال بارگذاری پیکربندی…",
    settings: "تنظیمات",
    settingsDescription: "اطلاعات ورود ارائه‌دهنده روی میزبان می‌ماند و کلید خام هرگز نمایش داده نمی‌شود.",
    provider: "ارائه‌دهنده",
    model: "مدل",
    baseUrl: "نشانی پایه",
    apiKey: "کلید API",
    keepSavedKey: "برای حفظ کلید ذخیره‌شده، این قسمت را خالی بگذارید",
    enterNewKey: "کلید تازه ایجادشده ارائه‌دهنده را وارد کنید",
    maxInputTokens: "حداکثر توکن ورودی",
    maxOutputTokens: "حداکثر توکن خروجی",
    maxCalls: "حداکثر درخواست در هر اجرا",
    requestTimeout: "مهلت پاسخ‌گویی (ثانیه)",
    saveSettings: "ذخیره تنظیمات",
    probeProvider: "آزمون اتصال ارائه‌دهنده",
    runGeneration: "اجرای یک نسل",
    generationDescription: "یک نامزد واجد شرایط یا ردشده تولید می‌کند؛ هیچ تغییری روی مخزن اعمال نمی‌شود.",
    objective: "هدف",
    objectivePlaceholder: "اعتبارسنجی ورودی را بدون تغییر رفتار عمومی بهبود بده.",
    mutablePaths: "مسیرهای قابل‌تغییر",
    evolve: "تکامل",
    thinking: "در حال فکر کردن…",
    autonomousEvolution: "تکامل خودکار",
    autonomyDescription: "تا زمانی که برنامه در حال اجراست، زایش دیجیتال و حیات مصنوعی بی‌پایان را پیوسته کاوش می‌کند.",
    autonomousObjective: "هدف تکامل خودکار",
    autonomyObjectivePlaceholder: "زایش دیجیتال و حیات مصنوعی بی‌پایان را کاوش کن...",
    intervalSeconds: "فاصله میان نسل‌ها (ثانیه)",
    generationLimit: "سقف تلاش برای تولید نسل",
    autonomyMutablePaths: "مسیرهای قابل‌تغییر در حالت خودکار",
    autonomySafety: "حالت خودکار از سهمیه API ارائه‌دهنده مصرف می‌کند. پیشنهادها را ارزیابی و انتخاب می‌کند، اما هرگز ادغام، استقرار، خرید یا تغییر هسته را انجام نمی‌دهد.",
    startAutonomy: "شروع تکامل خودکار",
    stopAutonomy: "توقف",
    evolutionJournal: "روایت تکامل",
    journalDescription: "روایتی عمومی از نسل‌های برگزیده، سازگاری‌ها و ناکامی‌های این گنوم.",
    achievements: "دستاوردهای تکاملی",
    noAchievements: "هنوز دستاوردی باز نشده است.",
    achievementUnlocked: "دستاورد تازه",
    noEvolutionYet: "هنوز تکامل خودکاری ثبت نشده است.",
    auditTrail: "گزارش رویدادها",
    auditDescription: "رویدادهای محلی پالایش‌شده از `.evo/audit.jsonl`.",
    search: "جست‌وجو",
    searchPlaceholder: "جست‌وجو در رویدادها، وضعیت و تنظیمات…",
    action: "عملیات",
    when: "زمان",
    event: "رویداد",
    status: "وضعیت",
    score: "امتیاز",
    noAuditEvents: "هنوز رویدادی ثبت نشده است.",
    requestFailed: "درخواست ناموفق بود",
    invalidServerResponse: "پاسخ دریافت‌شده از سرور معتبر نیست",
    configured: "پیکربندی",
    yes: "انجام شده",
    no: "انجام نشده",
    envFile: "فایل محیطی",
    present: "موجود",
    missing: "ناموجود",
    callsPerRun: "درخواست در هر اجرا",
    configurationIncomplete: "پیکربندی کامل نیست",
    inspectEvent: "مشاهده جزئیات رویداد",
    proposed: "پیشنهادشده",
    eligible: "واجد شرایط",
    rejected: "ردشده",
    generationCompleted: "تکمیل نسل",
    mutationApplied: "اعمال تغییر",
    mutationRejected: "رد تغییر",
    settingsSaved: "تنظیمات در فایل .env.local ذخیره شد",
    configurationValid: "پیکربندی معتبر است",
    waitingCandidate: "در انتظار پیشنهاد نامزد از سوی مدل…",
    candidateStatus: "وضعیت نامزد",
    evoError: "خطای EVO",
    candidateId: "شناسه_نامزد",
    genomeFingerprint: "اثرانگشت_ژنوم",
    proposal: "پیشنهاد",
    targetPath: "مسیر_هدف",
    summary: "خلاصه",
    rationale: "منطق_پیشنهاد",
    expectedBenefit: "فایده_موردانتظار",
    risk: "ریسک",
    schemaValidity: "اعتبار_ساختار",
    policyCompliance: "انطباق_با_سیاست",
    rationaleQuality: "کیفیت_استدلال",
    rejectionReason: "دلیل_رد",
    phase: "مرحله",
    generation: "نسل برگزیده",
    attempts: "تلاش‌ها",
    nextInterval: "فاصله",
    stopped: "متوقف",
    starting: "در حال آغاز",
    evolving: "در حال تکامل",
    waiting: "در انتظار",
    backoff: "در انتظار اتصال",
    completed: "تکمیل‌شده",
    finalizing: "در حال نهایی‌سازی",
    enabled: "در حال اجرا",
    autonomyStarted: "تکامل خودکار آغاز شد",
    autonomyStopped: "تکامل خودکار متوقف شد",
    journalStarted: "کاوش خودکار آغاز شد",
    journalStopped: "کاوش خودکار متوقف شد",
    journalCompleted: "سقف نسل‌ها تکمیل شد",
    journalError: "ارتباط با ارائه‌دهنده قطع شد",
    journalGeneration: "نسل",
    attempt: "تلاش",
    seconds: "ثانیه",
    retrying: "گنوم به‌صورت خودکار دوباره تلاش می‌کند.",
    achievement_first_spark: "نخستین جرقه",
    achievement_first_spark_desc: "نخستین سازگاری پایدار وارد تبار شد.",
    achievement_stable_lineage: "تبار پایدار",
    achievement_stable_lineage_desc: "پنج نسل برگزیده اکنون حافظه‌ای موروثی دارند.",
    achievement_adaptive_colony: "کلونی سازگار",
    achievement_adaptive_colony_desc: "ده نسل در قالب کلونی مقاومی انباشته شدند.",
    achievement_open_ended_explorer: "کاوشگر بی‌پایان",
    achievement_open_ended_explorer_desc: "بیست‌وپنج نسل مرز جست‌وجو را گسترش دادند.",
    achievement_emergent_ecology: "بوم‌شناسی نوظهور",
    achievement_emergent_ecology_desc: "پنجاه نسل، بوم‌شناسی دیجیتال عمیق‌تری پدید آوردند.",
    achievement_century_organism: "جاندار صدنسلی",
    achievement_century_organism_desc: "صد نسل برگزیده در زیست‌بوم دوام آوردند.",
    achievement_deep_time: "زمان ژرف",
    achievement_deep_time_desc: "پانصد نسل وارد دوران ژرف تکاملی شدند.",
    achievement_millennium_lineage: "تبار هزاره",
    achievement_millennium_lineage_desc: "هزار نسل، تباری دیجیتال و ماندگار ساختند.",
  },
};

const ACHIEVEMENT_CATALOG = {
  first_spark: { symbol: "✦" },
  stable_lineage: { symbol: "Ⅴ" },
  adaptive_colony: { symbol: "Ⅹ" },
  open_ended_explorer: { symbol: "∞" },
  emergent_ecology: { symbol: "◌" },
  century_organism: { symbol: "C" },
  deep_time: { symbol: "◈" },
  millennium_lineage: { symbol: "M" },
};

const AUTONOMY_OBJECTIVES = {
  en: "Explore digital abiogenesis and artificial life through open-ended, self-organizing multi-agent systems. Propose one safe, incremental improvement that increases emergence, adaptation, diversity, or observability without weakening the immutable kernel.",
  fa: "زایش دیجیتال و حیات مصنوعی را از مسیر سامانه‌های چندعاملی خودسازمان‌ده و بی‌پایان کاوش کن. یک بهبود ایمن و تدریجی پیشنهاد بده که ظهور رفتار، سازگاری، تنوع یا مشاهده‌پذیری را بدون تضعیف هسته تغییرناپذیر افزایش دهد.",
};

let language = localStorage.getItem("evo-language") || "en";
let cachedSettings = null;
let cachedAudit = [];
let cachedAutonomy = null;
let cachedJournal = [];

const statusSummary = document.getElementById("status-summary");
const statusGrid = document.getElementById("status-grid");
const settingsForm = document.getElementById("settings-form");
const evolveForm = document.getElementById("evolve-form");
const evolveResult = document.getElementById("evolve-result");
const evolveButton = document.getElementById("evolve-button");
const evolveButtonLabel = document.getElementById("evolve-button-label");
const evolveThinking = document.getElementById("evolve-thinking");
const auditBody = document.getElementById("audit-body");
const toast = document.getElementById("toast");
const globalSearch = document.getElementById("global-search");
const providerSelect = document.getElementById("provider");
const autonomyForm = document.getElementById("autonomy-form");
const autonomyBadge = document.getElementById("autonomy-badge");
const autonomyStats = document.getElementById("autonomy-stats");
const autonomyObjective = document.getElementById("autonomy-objective");
const journalContainer = document.getElementById("evolution-journal");
const achievementGallery = document.getElementById("achievement-gallery");
const achievementCount = document.getElementById("achievement-count");

function t(key) {
  return I18N[language][key] || I18N.en[key] || key;
}

function setLanguage(nextLanguage) {
  const previousLanguage = language;
  language = nextLanguage === "fa" ? "fa" : "en";
  localStorage.setItem("evo-language", language);
  document.documentElement.lang = language;
  document.documentElement.dir = language === "fa" ? "rtl" : "ltr";
  document.title = t("pageTitle");
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.classList.toggle("active", button.dataset.language === language);
  });
  if (
    !autonomyObjective.value ||
    autonomyObjective.value === AUTONOMY_OBJECTIVES[previousLanguage]
  ) {
    autonomyObjective.value = AUTONOMY_OBJECTIVES[language];
  }
  if (cachedSettings) {
    fillSettings(cachedSettings);
    renderStatus(cachedSettings);
  }
  renderAudit(cachedAudit);
  renderAutonomy(cachedAutonomy);
  renderJournal(cachedJournal);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": language,
    },
    ...options,
  });
  const responseText = await response.text();
  let payload = {};
  if (responseText) {
    try {
      payload = JSON.parse(responseText);
    } catch {
      throw new Error(`${t("invalidServerResponse")} (${response.status})`);
    }
  }
  if (!response.ok) {
    throw new Error(payload.error || t("requestFailed"));
  }
  return payload;
}

function showToast(message) {
  toast.hidden = false;
  toast.textContent = message;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.hidden = true;
  }, 4200);
}

function fillSettings(settings) {
  cachedSettings = settings;
  const provider = settings.provider || "groq";
  const defaults = DEFAULTS[provider] || DEFAULTS.groq;
  providerSelect.value = provider;
  document.getElementById("model").value = settings.model || defaults.model;
  document.getElementById("base_url").value = settings.base_url || defaults.base_url;
  document.getElementById("max_input_tokens").value = settings.max_input_tokens || 6000;
  document.getElementById("max_output_tokens").value = settings.max_output_tokens || 1200;
  document.getElementById("max_calls_per_run").value = settings.max_calls_per_run || 4;
  document.getElementById("request_timeout_seconds").value =
    settings.request_timeout_seconds || 45;
  document.getElementById("api_key").value = "";
  document.getElementById("api_key").placeholder = settings.configured
    ? t("keepSavedKey")
    : t("enterNewKey");
}

function renderStatus(settings) {
  const rows = [
    [t("configured"), settings.configured ? t("yes") : t("no")],
    [t("provider"), settings.provider || "—"],
    [t("model"), settings.model || "—"],
    [t("apiKey"), settings.api_key ? t("configured") : t("missing")],
    [t("envFile"), settings.env_file_exists ? t("present") : t("missing")],
    [t("callsPerRun"), settings.max_calls_per_run || "—"],
  ];
  statusGrid.innerHTML = rows
    .map(
      ([label, value]) => `
      <div>
        <dt>${escapeHtml(String(label))}</dt>
        <dd>${escapeHtml(String(value))}</dd>
      </div>`
    )
    .join("");
  statusSummary.textContent = settings.configured
    ? `${settings.provider} · ${settings.model}`
    : settings.error || t("configurationIncomplete");
}

function translateStatus(value) {
  return t(value) || value || "—";
}

function translateEvent(value) {
  const eventKeys = {
    "generation.completed": "generationCompleted",
    "mutation.applied": "mutationApplied",
    "mutation.rejected": "mutationRejected",
  };
  return eventKeys[value] ? t(eventKeys[value]) : value || "—";
}

function localizeCandidate(candidate) {
  const proposal = candidate.proposal
    ? {
        [t("targetPath")]: candidate.proposal.target_path,
        [t("summary")]: candidate.proposal.summary,
        [t("rationale")]: candidate.proposal.rationale,
        [t("expectedBenefit")]: candidate.proposal.expected_benefit,
        [t("risk")]: candidate.proposal.risk,
      }
    : null;
  const score = candidate.score
    ? {
        [t("schemaValidity")]: candidate.score.schema_validity,
        [t("policyCompliance")]: candidate.score.policy_compliance,
        [t("rationaleQuality")]: candidate.score.rationale_quality,
      }
    : null;
  return {
    [t("candidateId")]: candidate.candidate_id,
    [t("genomeFingerprint")]: candidate.genome_fingerprint,
    [t("proposal")]: proposal,
    [t("score")]: score,
    [t("status")]: translateStatus(candidate.status),
    [t("rejectionReason")]: candidate.rejection_reason,
  };
}

function renderAudit(events) {
  cachedAudit = events || [];
  if (!cachedAudit.length) {
    auditBody.innerHTML = `<tr><td colspan="6">${t("noAuditEvents")}</td></tr>`;
    return;
  }
  auditBody.innerHTML = cachedAudit
    .map((event, index) => {
      const payload = event.payload || {};
      const status = payload.status || "—";
      const badgeClass = status === "rejected" ? "badge rejected" : "badge";
      return `
        <tr data-search="${escapeAttr(JSON.stringify(event).toLowerCase())}">
          <td>
            <button class="icon-button" type="button"
              title="${escapeAttr(t("inspectEvent"))}"
              aria-label="${escapeAttr(`${t("inspectEvent")} ${index + 1}`)}"
              data-event-index="${index}">◉</button>
          </td>
          <td>${escapeHtml(formatTime(event.timestamp))}</td>
          <td>${escapeHtml(translateEvent(event.event_type))}</td>
          <td><span class="${badgeClass}">${escapeHtml(translateStatus(status))}</span></td>
          <td>${escapeHtml(String(payload.score ?? "—"))}</td>
          <td>${escapeHtml(String(payload.model || "—"))}</td>
        </tr>`;
    })
    .join("");
  auditBody.querySelectorAll("[data-event-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const event = cachedAudit[Number(button.dataset.eventIndex)];
      evolveResult.hidden = false;
      evolveResult.textContent = JSON.stringify(event, null, 2);
      evolveResult.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

function renderAutonomy(state) {
  if (!state) return;
  cachedAutonomy = state;
  renderAchievements(state.achievements || []);
  const phaseKey = state.enabled ? state.phase || "enabled" : state.phase || "stopped";
  autonomyBadge.textContent = t(phaseKey);
  autonomyBadge.className = state.phase === "backoff" ? "badge rejected" : "badge";
  autonomyStats.innerHTML = [
    [t("phase"), t(phaseKey)],
    [t("generation"), state.generation ?? 0],
    [t("attempts"), `${state.attempts ?? 0} / ${state.max_generations ?? "—"}`],
    [t("nextInterval"), `${state.interval_seconds ?? "—"} ${t("seconds")}`],
  ]
    .map(
      ([label, value]) => `
        <div class="autonomy-stat">
          <span>${escapeHtml(String(label))}</span>
          <strong>${escapeHtml(String(value))}</strong>
        </div>`
    )
    .join("");
  if (document.activeElement !== autonomyObjective) {
    autonomyObjective.value = state.updated_at
      ? state.objective
      : AUTONOMY_OBJECTIVES[language];
  }
  document.getElementById("interval_seconds").value = state.interval_seconds || 300;
  document.getElementById("max_generations").value = state.max_generations || 100;
  document.getElementById("autonomy-mutable-paths").value =
    (state.mutable_paths || ["organisms/"]).join(", ");
  document.getElementById("start-autonomy").disabled = Boolean(state.enabled);
  document.getElementById("stop-autonomy").disabled = !state.enabled;
}

function achievementName(id) {
  return t(`achievement_${id}`);
}

function achievementDescription(id) {
  return t(`achievement_${id}_desc`);
}

function renderAchievements(achievements) {
  const total = Object.keys(ACHIEVEMENT_CATALOG).length;
  achievementCount.textContent = `${achievements.length} / ${total}`;
  if (!achievements.length) {
    achievementGallery.innerHTML =
      `<p class="empty-state">${escapeHtml(t("noAchievements"))}</p>`;
    return;
  }
  achievementGallery.innerHTML = achievements
    .map((achievement) => {
      const catalog = ACHIEVEMENT_CATALOG[achievement.id] || { symbol: "✦" };
      return `
        <article class="achievement-card">
          <span class="achievement-symbol" aria-hidden="true">${escapeHtml(catalog.symbol)}</span>
          <div>
            <strong>${escapeHtml(achievementName(achievement.id))}</strong>
            <small>${escapeHtml(achievementDescription(achievement.id))}</small>
          </div>
        </article>`;
    })
    .join("");
}

function renderJournal(entries) {
  cachedJournal = entries || [];
  if (!cachedJournal.length) {
    journalContainer.innerHTML = `<p class="empty-state">${t("noEvolutionYet")}</p>`;
    return;
  }
  const titles = {
    "autonomy.started": "journalStarted",
    "autonomy.stopped": "journalStopped",
    "autonomy.completed": "journalCompleted",
    "autonomy.error": "journalError",
  };
  journalContainer.innerHTML = cachedJournal
    .map((entry) => {
      const payload = entry.payload || {};
      const isGeneration = entry.event_type === "autonomy.generation";
      const title = isGeneration
        ? `${t("journalGeneration")} ${payload.generation ?? "—"}`
        : t(titles[entry.event_type] || "evolutionJournal");
      const detail = isGeneration
        ? payload.summary || payload.rejection_reason || "—"
        : entry.event_type === "autonomy.error"
          ? `${payload.message || "—"} ${t("retrying")}`
          : payload.objective || "";
      const meta = isGeneration
        ? `${t("attempt")} ${payload.attempt ?? "—"} · ${translateStatus(payload.status)} · ${t("score")}: ${payload.score ?? "—"}`
        : "";
      const achievementChips = (payload.achievements || [])
        .map(
          (achievement) => `
            <span class="achievement-chip">
              ✦ ${escapeHtml(t("achievementUnlocked"))}: ${escapeHtml(achievementName(achievement.id))}
            </span>`
        )
        .join("");
      return `
        <article class="timeline-entry ${entry.event_type === "autonomy.error" ? "error" : ""}">
          <h3>${escapeHtml(String(title))}</h3>
          <div class="timeline-meta">${escapeHtml(`${formatTime(entry.timestamp)}${meta ? ` · ${meta}` : ""}`)}</div>
          ${detail ? `<p>${escapeHtml(String(detail))}</p>` : ""}
          ${payload.expected_benefit ? `<p><strong>${escapeHtml(t("expectedBenefit"))}:</strong> ${escapeHtml(String(payload.expected_benefit))}</p>` : ""}
          ${payload.risk ? `<p><strong>${escapeHtml(t("risk"))}:</strong> ${escapeHtml(String(payload.risk))}</p>` : ""}
          ${achievementChips ? `<div class="achievement-unlocks">${achievementChips}</div>` : ""}
        </article>`;
    })
    .join("");
}

function formatTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(language === "fa" ? "fa-IR" : "en-US");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

function formObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function setEvolveThinking(active) {
  evolveButton.disabled = active;
  evolveButton.classList.toggle("is-thinking", active);
  evolveButton.setAttribute("aria-busy", String(active));
  evolveButtonLabel.textContent = active ? t("thinking") : t("evolve");
  evolveThinking.hidden = !active;
  evolveResult.setAttribute("aria-busy", String(active));
}

function applySearch(query) {
  const needle = query.trim().toLowerCase();
  document.querySelectorAll(".panel").forEach((panel) => {
    const haystack = panel.textContent.toLowerCase();
    panel.classList.toggle("hidden-by-search", Boolean(needle) && !haystack.includes(needle));
  });
}

async function refresh() {
  const [settings, audit, autonomy, journal] = await Promise.all([
    api("/api/settings"),
    api("/api/audit?limit=50"),
    api("/api/autonomy"),
    api("/api/evolution-journal?limit=100"),
  ]);
  fillSettings(settings);
  renderStatus(settings);
  renderAudit(audit.events || []);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  applySearch(globalSearch.value);
}

async function refreshEvolution() {
  const [autonomy, journal, audit] = await Promise.all([
    api("/api/autonomy"),
    api("/api/evolution-journal?limit=100"),
    api("/api/audit?limit=50"),
  ]);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  renderAudit(audit.events || []);
}

document.querySelectorAll("[data-language]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

providerSelect.addEventListener("change", () => {
  const defaults = DEFAULTS[providerSelect.value];
  document.getElementById("model").value = defaults.model;
  document.getElementById("base_url").value = defaults.base_url;
});

settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = formObject(settingsForm);
    const settings = await api("/api/settings", {
      method: "POST",
      body: JSON.stringify({
        ...payload,
        max_input_tokens: Number(payload.max_input_tokens),
        max_output_tokens: Number(payload.max_output_tokens),
        max_calls_per_run: Number(payload.max_calls_per_run),
        request_timeout_seconds: Number(payload.request_timeout_seconds),
      }),
    });
    fillSettings(settings);
    renderStatus(settings);
    showToast(t("settingsSaved"));
  } catch (error) {
    showToast(error.message);
  }
});

document.getElementById("run-doctor").addEventListener("click", async () => {
  try {
    const result = await api("/api/doctor");
    showToast(`${t("configurationValid")}: ${result.provider} · ${result.model}`);
    await refresh();
  } catch (error) {
    showToast(error.message);
  }
});

document.getElementById("run-probe").addEventListener("click", async () => {
  try {
    const result = await api("/api/probe", { method: "POST", body: "{}" });
    showToast(result.message);
  } catch (error) {
    showToast(error.message);
  }
});

evolveForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (evolveButton.disabled) return;
  setEvolveThinking(true);
  evolveResult.hidden = false;
  evolveResult.textContent = t("waitingCandidate");
  try {
    const payload = formObject(evolveForm);
    const candidate = await api("/api/evolve", {
      method: "POST",
      body: JSON.stringify({
        task: payload.task,
        mutable_paths: payload.mutable_paths,
        language,
      }),
    });
    evolveResult.textContent = JSON.stringify(localizeCandidate(candidate), null, 2);
    showToast(`${t("candidateStatus")}: ${translateStatus(candidate.status)}`);
    await refreshEvolution();
  } catch (error) {
    showToast(error.message);
    evolveResult.textContent = `${t("evoError")}: ${error.message}`;
  } finally {
    setEvolveThinking(false);
  }
});

autonomyForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = formObject(autonomyForm);
    cachedAutonomy = await api("/api/autonomy/start", {
      method: "POST",
      body: JSON.stringify({
        objective: payload.objective,
        mutable_paths: payload.mutable_paths,
        interval_seconds: Number(payload.interval_seconds),
        max_generations: Number(payload.max_generations),
        language,
      }),
    });
    renderAutonomy(cachedAutonomy);
    showToast(t("autonomyStarted"));
    await refreshEvolution();
  } catch (error) {
    showToast(error.message);
  }
});

document.getElementById("stop-autonomy").addEventListener("click", async () => {
  try {
    cachedAutonomy = await api("/api/autonomy/stop", {
      method: "POST",
      body: "{}",
    });
    renderAutonomy(cachedAutonomy);
    showToast(t("autonomyStopped"));
    await refreshEvolution();
  } catch (error) {
    showToast(error.message);
  }
});

globalSearch.addEventListener("input", () => applySearch(globalSearch.value));

setLanguage(language);
refresh().catch((error) => {
  statusSummary.textContent = error.message;
  showToast(error.message);
});
window.setInterval(() => {
  if (cachedAutonomy?.enabled) {
    refreshEvolution().catch(() => {});
  }
}, 5000);

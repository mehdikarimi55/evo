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
    populationEcology: "POPULATION ECOLOGY",
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
    sandboxImage: "Rootless sandbox image",
    sandboxEngine: "Sandbox engine",
    evaluationCommand: "Evaluation command",
    sandboxTimeout: "Sandbox timeout (seconds)",
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
    digitalPetriDish: "Digital Petri Dish",
    petriDescription: "A bounded population where energy, heredity, reproduction, and selection shape a visible digital lineage.",
    lineageMap: "Lineage map",
    living: "Living",
    extinct: "Extinct",
    births: "Births",
    meanEnergy: "Mean energy",
    meanFitness: "Mean fitness",
    epoch: "Ecological epoch",
    capacity: "Carrying capacity",
    energy: "Energy",
    fitness: "Fitness",
    founder: "Founder",
    offspring: "Offspring",
    noPopulation: "No population evidence is available.",
    resourcePools: "Environmental resources",
    emergentNiches: "Emergent niches",
    cooperationNetwork: "Cooperation network",
    noCooperation: "No cooperation signal has formed yet.",
    environmentPhase: "Environment phase",
    compute: "Compute",
    knowledge: "Knowledge",
    novelty: "Novelty",
    stability: "Stability",
    balanced: "Balanced",
    scarcity: "Scarcity",
    novelty_surge: "Novelty surge",
    explorer: "Explorer",
    guardian: "Guardian",
    economizer: "Economizer",
    archivist: "Archivist",
    generalist: "Generalist",
    undifferentiated: "Undifferentiated",
    interactions: "interactions",
    researchEvidence: "RESEARCH EVIDENCE",
    ecologySignals: "Ecology signals",
    ecologicalStability: "Ecological stability",
    populationDiversity: "Population diversity",
    openEndednessProxy: "Open-endedness proxy",
    openEndednessCaveat: "Open-endedness is an operational proxy for novelty, adaptation diversity, and lineage branching—not proof of unbounded evolution.",
    cooperativeTeam: "Latest cooperative team",
    noTeamEvidence: "No team evaluation has been recorded yet.",
    lead: "Lead",
    collaborator: "Collaborator",
    proposal_only: "Proposal only",
    sandbox_verified: "Sandbox verified",
    sandbox_failed: "Sandbox failed",
    invalid: "Invalid evidence",
    preserved_baseline: "Baseline preserved",
    repaired_baseline: "Baseline repaired",
    regression: "Regression detected",
    still_failing: "Still failing",
    patch_rejected: "Patch rejected",
    incomplete: "Incomplete evaluation",
    promotionEligible: "Promotion eligible",
    changedPaths: "Changed paths",
    evidenceIntegrity: "EVIDENCE INTEGRITY",
    promotionGate: "Human-controlled promotion gate",
    promotionGateDescription: "Replay every ecological epoch, authenticate the evidence bundle, and record an explicit human decision.",
    bundleInstructions: "Create a host-authenticated snapshot only after deterministic replay succeeds.",
    createEvidenceBundle: "Create evidence bundle",
    approver: "Reviewer",
    approverPlaceholder: "Your name or local reviewer label",
    decision: "Decision",
    approve: "Approve",
    rejectDecision: "Reject",
    reviewNote: "Review note",
    reviewNotePlaceholder: "What evidence did you inspect?",
    recordDecision: "Record human decision",
    promotionGateSafety: "This is a signed local assertion—not verified identity, repository promotion, merge, or deployment authorization.",
    evidenceBundle: "Evidence bundle",
    deterministicReplay: "Deterministic replay",
    humanDecision: "Human decision",
    deploymentAuthority: "Deployment authority",
    noBundle: "No bundle yet",
    noDecision: "No decision yet",
    verified: "Verified",
    unverified: "Unverified",
    denied: "Not authorized",
    bundleCreated: "Verified evidence bundle created",
    decisionRecorded: "Human decision recorded",
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
    populationEcology: "بوم‌شناسی جمعیت",
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
    sandboxImage: "تصویر محیط ایزوله بدون ریشه",
    sandboxEngine: "موتور محیط ایزوله",
    evaluationCommand: "دستور ارزیابی",
    sandboxTimeout: "مهلت محیط ایزوله (ثانیه)",
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
    digitalPetriDish: "پتری‌دیش دیجیتال",
    petriDescription: "جمعیتی کنترل‌شده که در آن انرژی، وراثت، تولیدمثل و گزینش، تباری دیجیتال و قابل مشاهده می‌سازند.",
    lineageMap: "نقشه تبار",
    living: "زنده",
    extinct: "منقرض‌شده",
    births: "تولدها",
    meanEnergy: "میانگین انرژی",
    meanFitness: "میانگین برازندگی",
    epoch: "دوره بوم‌شناختی",
    capacity: "ظرفیت زیست‌بوم",
    energy: "انرژی",
    fitness: "برازندگی",
    founder: "بنیان‌گذار",
    offspring: "فرزند",
    noPopulation: "هنوز داده‌ای از جمعیت در دسترس نیست.",
    resourcePools: "منابع محیطی",
    emergentNiches: "آشیان‌های نوظهور",
    cooperationNetwork: "شبکه همکاری",
    noCooperation: "هنوز سیگنال همکاری شکل نگرفته است.",
    environmentPhase: "وضعیت محیط",
    compute: "توان محاسباتی",
    knowledge: "دانش",
    novelty: "نوآوری",
    stability: "پایداری",
    balanced: "متعادل",
    scarcity: "کمبود منابع",
    novelty_surge: "جهش نوآوری",
    explorer: "کاوشگر",
    guardian: "نگهبان",
    economizer: "بهینه‌گر منابع",
    archivist: "حافظ",
    generalist: "همه‌فن‌حریف",
    undifferentiated: "تمایزنیافته",
    interactions: "تعامل",
    researchEvidence: "شواهد پژوهشی",
    ecologySignals: "سیگنال‌های بوم‌شناختی",
    ecologicalStability: "پایداری بوم‌شناختی",
    populationDiversity: "تنوع جمعیت",
    openEndednessProxy: "شاخص تقریبی تکامل بازپایان",
    openEndednessCaveat: "تکامل بازپایان در اینجا شاخصی عملیاتی بر پایه نوآوری، تنوع سازگاری و شاخه‌زایی تبار است؛ نه اثبات تکامل نامحدود.",
    cooperativeTeam: "آخرین تیم همکار",
    noTeamEvidence: "هنوز ارزیابی تیمی ثبت نشده است.",
    lead: "راهبر",
    collaborator: "همکار",
    proposal_only: "فقط پیشنهاد",
    sandbox_verified: "تأییدشده در محیط ایزوله",
    sandbox_failed: "ناموفق در محیط ایزوله",
    invalid: "شواهد نامعتبر",
    preserved_baseline: "خط مبنا حفظ شد",
    repaired_baseline: "خط مبنا اصلاح شد",
    regression: "پس‌رفت شناسایی شد",
    still_failing: "همچنان ناموفق",
    patch_rejected: "وصله رد شد",
    incomplete: "ارزیابی ناقص",
    promotionEligible: "واجد شرایط ارتقا",
    changedPaths: "مسیرهای تغییرکرده",
    evidenceIntegrity: "یکپارچگی شواهد",
    promotionGate: "دروازه ارتقا با کنترل انسانی",
    promotionGateDescription: "تمام دوره‌های بوم‌شناختی را بازپخش کنید، اصالت بسته شواهد را بسنجید و تصمیم صریح انسان را ثبت کنید.",
    bundleInstructions: "تنها پس از موفقیت بازپخش قطعی، یک نمای لحظه‌ای احرازاصالت‌شده توسط میزبان بسازید.",
    createEvidenceBundle: "ساخت بسته شواهد",
    approver: "بازبین",
    approverPlaceholder: "نام شما یا عنوان بازبین محلی",
    decision: "تصمیم",
    approve: "تأیید",
    rejectDecision: "رد",
    reviewNote: "یادداشت بازبینی",
    reviewNotePlaceholder: "کدام شواهد را بررسی کردید؟",
    recordDecision: "ثبت تصمیم انسانی",
    promotionGateSafety: "این فقط یک اظهار محلی امضاشده است؛ نه هویت تأییدشده، ارتقای مخزن، ادغام یا مجوز استقرار.",
    evidenceBundle: "بسته شواهد",
    deterministicReplay: "بازپخش قطعی",
    humanDecision: "تصمیم انسانی",
    deploymentAuthority: "اختیار استقرار",
    noBundle: "هنوز بسته‌ای ساخته نشده",
    noDecision: "هنوز تصمیمی ثبت نشده",
    verified: "تأییدشده",
    unverified: "تأییدنشده",
    denied: "مجاز نیست",
    bundleCreated: "بسته شواهد تأییدشده ساخته شد",
    decisionRecorded: "تصمیم انسانی ثبت شد",
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
let cachedPetri = null;
let cachedEvidenceControl = null;

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
const petriStats = document.getElementById("petri-stats");
const lineageMap = document.getElementById("lineage-map");
const populationRoster = document.getElementById("population-roster");
const resourcePools = document.getElementById("resource-pools");
const nicheDistribution = document.getElementById("niche-distribution");
const cooperationNetwork = document.getElementById("cooperation-network");
const ecologyMetrics = document.getElementById("ecology-metrics");
const evaluationEvidence = document.getElementById("evaluation-evidence");
const teamObservatory = document.getElementById("team-observatory");
const evidenceControlStatus = document.getElementById("evidence-control-status");
const createEvidenceBundle = document.getElementById("create-evidence-bundle");
const approvalForm = document.getElementById("approval-form");

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
  renderPetriDish(cachedPetri);
  renderEvidenceControl(cachedEvidenceControl);
}

function renderEvidenceControl(status) {
  if (!status) return;
  cachedEvidenceControl = status;
  const bundle = status.latest_bundle;
  const approval = status.latest_approval;
  const replayVerified = Boolean(bundle?.replay_verified);
  const bundleVerified = Boolean(bundle?.verified);
  const approvalValid = Boolean(
    approval && status.approval_signature_valid && bundleVerified
  );
  const cards = [
    ["evidenceBundle", bundle?.bundle_id || t("noBundle"), bundleVerified],
    ["deterministicReplay", bundle ? (replayVerified ? t("verified") : t("unverified")) : t("noBundle"), replayVerified],
    ["humanDecision", approvalValid ? `${t(approval.decision === "approve" ? "approve" : "rejectDecision")} · ${approval.approver}` : t("noDecision"), approvalValid],
    ["deploymentAuthority", t("denied"), false],
  ];
  evidenceControlStatus.innerHTML = cards.map(([label, value, valid]) => `
    <article class="gate-status-card ${valid ? "verified" : "restricted"}">
      <span>${escapeHtml(t(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
  approvalForm.querySelector("button[type='submit']").disabled = !bundleVerified;
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
  document.getElementById("sandbox_image").value = settings.sandbox_image || "";
  document.getElementById("sandbox_engine").value = settings.sandbox_engine || "podman";
  document.getElementById("evaluation_command").value =
    settings.evaluation_command || "python -m unittest discover -s tests";
  document.getElementById("sandbox_timeout_seconds").value =
    settings.sandbox_timeout_seconds || 60;
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
    : language === "fa"
      ? settings.error || t("configurationIncomplete")
      : t("configurationIncomplete");
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

function renderPetriDish(state) {
  if (!state) return;
  cachedPetri = state;
  const summary = state.summary || {};
  const metrics = state.metrics || {};
  ecologyMetrics.innerHTML = [
    ["ecologicalStability", metrics.ecological_stability],
    ["populationDiversity", metrics.population_diversity],
    ["openEndednessProxy", metrics.open_endedness_proxy],
  ]
    .map(([label, rawValue]) => {
      const value = Math.max(0, Math.min(1, Number(rawValue || 0)));
      return `<article class="metric-card">
        <span>${escapeHtml(t(label))}</span>
        <strong>${escapeHtml(`${Math.round(value * 100)}%`)}</strong>
        <div class="metric-track"><i style="width:${value * 100}%"></i></div>
      </article>`;
    })
    .join("");

  const latestEvent = (state.events || []).at(-1) || {};
  const evidence = latestEvent.evaluation_evidence || { status: "proposal_only" };
  evaluationEvidence.className = `evidence-state ${escapeAttr(evidence.status || "proposal_only")}`;
  evaluationEvidence.textContent = t(evidence.status || "proposal_only");
  const team = latestEvent.team || [];
  const comparisonDetails = evidence.source === "rootless_sandbox_comparison"
    ? `<div class="comparison-evidence">
        <span><strong>${escapeHtml(t(evidence.classification || "incomplete"))}</strong>${escapeHtml(t("promotionEligible"))}: ${escapeHtml(evidence.promotion_eligible ? t("yes") : t("no"))}</span>
        <span><strong>${escapeHtml(t("changedPaths"))}</strong>${escapeHtml((evidence.changed_paths || []).join(", ") || "—")}</span>
      </div>`
    : "";
  teamObservatory.innerHTML = team.length
    ? `${comparisonDetails}<h4>${escapeHtml(t("cooperativeTeam"))}</h4><div class="team-members">${team
        .map(
          (member, index) => `<span class="team-member">
            <strong>${escapeHtml(member.organism_id)}</strong>
            ${escapeHtml(t(member.emergent_role || "undifferentiated"))} · ${escapeHtml(t(index === 0 ? "lead" : "collaborator"))}
          </span>`
        )
        .join("")}</div>`
    : `${comparisonDetails}<p class="empty-state">${escapeHtml(t("noTeamEvidence"))}</p>`;
  petriStats.innerHTML = [
    [t("epoch"), summary.epoch ?? 0],
    [t("living"), `${summary.living ?? 0} / ${summary.capacity ?? 0}`],
    [t("births"), summary.births ?? 0],
    [t("extinct"), summary.extinct ?? 0],
    [t("meanEnergy"), summary.mean_energy ?? 0],
    [t("meanFitness"), summary.mean_fitness ?? 0],
  ]
    .map(
      ([label, value]) => `
        <div class="petri-stat">
          <span>${escapeHtml(String(label))}</span>
          <strong>${escapeHtml(String(value))}</strong>
        </div>`
    )
    .join("");

  const environment = state.environment || { phase: "balanced", resources: {} };
  resourcePools.innerHTML = `
    <p class="environment-phase">${escapeHtml(t("environmentPhase"))}: <strong>${escapeHtml(t(environment.phase || "balanced"))}</strong></p>
    ${Object.entries(environment.resources || {})
      .map(([name, value]) => {
        const amount = Math.max(0, Math.min(120, Number(value || 0)));
        return `
          <div class="resource-row">
            <span>${escapeHtml(t(name))}</span>
            <div class="resource-track"><i style="width:${(amount / 120) * 100}%"></i></div>
            <strong>${escapeHtml(amount.toFixed(1))}</strong>
          </div>`;
      })
      .join("")}`;

  const niches = summary.niche_distribution || {};
  nicheDistribution.innerHTML = Object.entries(niches)
    .map(
      ([role, count]) => `
        <span class="niche-chip">
          ${escapeHtml(t(role))}<strong>${escapeHtml(String(count))}</strong>
        </span>`
    )
    .join("");

  const cooperation = (state.cooperation || []).slice(-8).reverse();
  cooperationNetwork.innerHTML = cooperation.length
    ? cooperation
        .map(
          (edge) => `
            <div class="cooperation-edge">
              <span>${escapeHtml(edge.organism_a)}</span>
              <i aria-hidden="true">⇄</i>
              <span>${escapeHtml(edge.organism_b)}</span>
              <strong>${escapeHtml(`${edge.successful_interactions}/${edge.interactions}`)} ${escapeHtml(t("interactions"))}</strong>
            </div>`
        )
        .join("")
    : `<p class="empty-state">${escapeHtml(t("noCooperation"))}</p>`;

  const organisms = (state.organisms || []).slice(-80);
  if (!organisms.length) {
    lineageMap.innerHTML = "";
    populationRoster.innerHTML =
      `<p class="empty-state">${escapeHtml(t("noPopulation"))}</p>`;
    return;
  }

  const visibleIds = new Set(organisms.map((organism) => organism.organism_id));
  const grouped = new Map();
  organisms.forEach((organism) => {
    const generation = Number(organism.generation || 0);
    if (!grouped.has(generation)) grouped.set(generation, []);
    grouped.get(generation).push(organism);
  });
  const generations = [...grouped.keys()].sort((a, b) => a - b);
  const positions = new Map();
  const columnWidth = 190;
  const rowHeight = 84;
  const marginX = 74;
  const marginY = 58;
  generations.forEach((generation, column) => {
    grouped
      .get(generation)
      .sort((a, b) => a.organism_id.localeCompare(b.organism_id))
      .forEach((organism, row) => {
        positions.set(organism.organism_id, {
          x: marginX + column * columnWidth,
          y: marginY + row * rowHeight,
        });
      });
  });
  const maxRows = Math.max(...[...grouped.values()].map((items) => items.length));
  const width = Math.max(540, marginX * 2 + generations.length * columnWidth);
  const height = Math.max(260, marginY * 2 + maxRows * rowHeight);
  lineageMap.setAttribute("viewBox", `0 0 ${width} ${height}`);
  lineageMap.setAttribute("width", width);
  lineageMap.setAttribute("height", height);

  const edges = (state.lineage || [])
    .filter(
      (edge) =>
        visibleIds.has(edge.parent_id) &&
        visibleIds.has(edge.child_id) &&
        positions.has(edge.parent_id) &&
        positions.has(edge.child_id)
    )
    .map((edge) => {
      const parent = positions.get(edge.parent_id);
      const child = positions.get(edge.child_id);
      return `<path class="lineage-edge" d="M ${parent.x + 22} ${parent.y} C ${parent.x + 82} ${parent.y}, ${child.x - 82} ${child.y}, ${child.x - 22} ${child.y}" />`;
    })
    .join("");

  const generationLabels = generations
    .map((generation, column) => {
      const x = marginX + column * columnWidth;
      return `<text class="generation-label" x="${x}" y="22" text-anchor="middle">${escapeHtml(`${t("generation")} ${generation}`)}</text>`;
    })
    .join("");

  const nodes = organisms
    .map((organism) => {
      const position = positions.get(organism.organism_id);
      const alive = organism.status === "alive";
      const energy = Math.max(0, Math.min(100, Number(organism.energy || 0)));
      return `
        <g class="lineage-node ${alive ? "alive" : "extinct"}" transform="translate(${position.x} ${position.y})">
          <circle class="node-halo" r="25"></circle>
          <circle class="node-body" r="19"></circle>
          <circle class="energy-ring" r="22" pathLength="100"
            stroke-dasharray="${energy} ${100 - energy}" transform="rotate(-90)"></circle>
          <text class="node-id" y="4" text-anchor="middle">${escapeHtml(organism.organism_id.replace("gnome-", ""))}</text>
          <text class="node-metric" y="37" text-anchor="middle">${escapeHtml(`${t("fitness")} ${Number(organism.fitness || 0).toFixed(2)}`)}</text>
        </g>`;
    })
    .join("");
  lineageMap.innerHTML = `${generationLabels}${edges}${nodes}`;

  populationRoster.innerHTML = organisms
    .filter((organism) => organism.status === "alive")
    .sort((a, b) => Number(b.fitness) - Number(a.fitness))
    .slice(0, 12)
    .map(
      (organism) => `
        <article class="organism-card">
          <div>
            <strong>${escapeHtml(organism.organism_id)}</strong>
            <small>${escapeHtml(
              organism.parent_ids?.length ? t("offspring") : t("founder")
            )} · ${escapeHtml(`${t("generation")} ${organism.generation}`)} · ${escapeHtml(t(organism.emergent_role || "undifferentiated"))}</small>
          </div>
          <dl>
            <div><dt>${escapeHtml(t("energy"))}</dt><dd>${escapeHtml(String(organism.energy))}</dd></div>
            <div><dt>${escapeHtml(t("fitness"))}</dt><dd>${escapeHtml(Number(organism.fitness || 0).toFixed(3))}</dd></div>
          </dl>
        </article>`
    )
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
  const [settings, audit, autonomy, journal, petri, evidenceControl] = await Promise.all([
    api("/api/settings"),
    api("/api/audit?limit=50"),
    api("/api/autonomy"),
    api("/api/evolution-journal?limit=100"),
    api("/api/petri-dish"),
    api("/api/evidence-control"),
  ]);
  fillSettings(settings);
  renderStatus(settings);
  renderAudit(audit.events || []);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  renderPetriDish(petri);
  renderEvidenceControl(evidenceControl);
  applySearch(globalSearch.value);
}

async function refreshEvolution() {
  const [autonomy, journal, audit, petri, evidenceControl] = await Promise.all([
    api("/api/autonomy"),
    api("/api/evolution-journal?limit=100"),
    api("/api/audit?limit=50"),
    api("/api/petri-dish"),
    api("/api/evidence-control"),
  ]);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  renderAudit(audit.events || []);
  renderPetriDish(petri);
  renderEvidenceControl(evidenceControl);
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
        sandbox_timeout_seconds: Number(payload.sandbox_timeout_seconds),
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

createEvidenceBundle.addEventListener("click", async () => {
  createEvidenceBundle.disabled = true;
  try {
    await api("/api/evidence/bundle", { method: "POST", body: "{}" });
    renderEvidenceControl(await api("/api/evidence-control"));
    showToast(t("bundleCreated"));
  } catch (error) {
    showToast(error.message);
  } finally {
    createEvidenceBundle.disabled = false;
  }
});

approvalForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = formObject(approvalForm);
    await api("/api/evidence/approve", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderEvidenceControl(await api("/api/evidence-control"));
    showToast(t("decisionRecorded"));
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

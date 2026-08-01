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

const GROQ_MODEL_FALLBACK = [
  "openai/gpt-oss-20b",
  "openai/gpt-oss-120b",
  "llama-3.3-70b-versatile",
  "llama-3.1-8b-instant",
  "meta-llama/llama-4-scout-17b-16e-instruct",
  "qwen/qwen3-32b",
  "gemma2-9b-it",
  "llama-guard-3-8b",
  "openai/gpt-oss-safeguard-20b",
];

const NVIDIA_MODEL_FALLBACK = [
  "meta/llama-3.1-70b-instruct",
  "meta/llama-3.1-8b-instruct",
  "meta/llama-3.3-70b-instruct",
  "meta/llama-3.1-405b-instruct",
  "nvidia/llama-3.1-nemotron-70b-instruct",
  "nvidia/llama-3.3-nemotron-super-49b-v1",
  "mistralai/mistral-large-2-instruct",
  "mistralai/mixtral-8x22b-instruct-v0.1",
  "mistralai/mistral-7b-instruct-v0.3",
  "google/gemma-2-27b-it",
  "google/gemma-2-9b-it",
  "qwen/qwen2.5-72b-instruct",
  "qwen/qwen2.5-coder-32b-instruct",
  "microsoft/phi-3-mini-128k-instruct",
  "deepseek-ai/deepseek-r1",
];

const PROVIDER_MODEL_FALLBACK = {
  groq: GROQ_MODEL_FALLBACK,
  nvidia: NVIDIA_MODEL_FALLBACK,
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
    nvidiaGenerationProfile: "NVIDIA generation profile",
    nvidiaProfilePrecise: "Precise (temperature 0.2)",
    nvidiaProfileBalanced: "Balanced (temperature 0.7)",
    nvidiaProfileExploratory: "Exploratory (temperature 1.0)",
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
    lineageHint: "Drag to pan · scrollbars explore · wheel zooms",
    lineageZoomIn: "Zoom in",
    lineageZoomOut: "Zoom out",
    lineageZoomReset: "Reset",
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
    pipelineEvidenceStep: "GATE · v0.7",
    pipelineEvidenceTitle: "Evidence & human review",
    pipelineEvidenceBlurb: "Authenticate a replay bundle, then record an explicit local human decision.",
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
    publicTrust: "PUBLIC TRUST · v0.8",
    trustAuthority: "Independent trust authority",
    trustAuthorityDescription: "Publish an Ed25519 evidence attestation, verify an independently signed reviewer decision, and evaluate the immutable promotion policy.",
    attestEvidence: "Publish evidence attestation",
    authorizePromotion: "Authorize manual promotion",
    trustAuthoritySafety: "Reviewer keys are managed only through the CLI. Authorization creates a signed artifact; EVO still cannot modify Git, push, merge, or deploy.",
    authorityIdentity: "Authority identity",
    trustedReviewers: "Trusted reviewers",
    publicAttestation: "Public attestation",
    independentReview: "Independent review",
    promotionPolicy: "Promotion policy",
    manualAuthorization: "Manual authorization",
    noAttestation: "No attestation yet",
    noIndependentReview: "No independent review",
    policySatisfied: "Policy satisfied",
    policyBlocked: "Policy blocked",
    noAuthorization: "No authorization",
    attestationCreated: "Public evidence attestation created",
    promotionAuthorized: "Manual promotion authorization created",
    controlledRelease: "CONTROLLED RELEASE · v0.9",
    releaseControl: "Reproducible local promotion",
    releaseControlDescription: "Preserve the exact sandbox-verified patch, consume one signed authorization, and support exact-state rollback from the CLI.",
    releaseControlSafety: "Apply and rollback are CLI-only and require exact confirmation phrases. EVO never commits, pushes, merges, or deploys the promoted worktree.",
    sealedArtifact: "Sealed candidate artifact",
    authorizationUse: "Authorization use",
    localRepository: "Local repository",
    promotionState: "Promotion state",
    rollbackState: "Rollback state",
    noArtifact: "No sealed artifact",
    authorizationReady: "Ready and unused",
    authorizationUsed: "Already consumed",
    authorizationMissing: "No current authorization",
    clean: "Clean",
    dirty: "Not clean",
    noActivePromotion: "No active promotion",
    rollbackReady: "Exact rollback available",
    noRollback: "No rollback pending",
    productionHandoff: "PRODUCTION HANDOFF · v1.0",
    deploymentHandoff: "Signed external deployment handoff",
    deploymentHandoffDescription: "Bind a committed release to signed stage, health, production, and rollback intents, then verify receipts from an independent operator.",
    deploymentHandoffSafety: "This panel is read-only. EVO holds no cloud credentials and performs no network deployment; an independent operator executes every external change.",
    releaseCapsule: "Signed release capsule",
    trustedOperators: "Trusted operators",
    deploymentPhase: "Deployment phase",
    nextDeploymentAction: "Next controlled action",
    operatorReceipt: "Latest operator receipt",
    externalExecution: "External execution",
    noReleaseCapsule: "No release capsule",
    noOperatorReceipt: "No receipt yet",
    required: "Required",
    ready_to_stage: "Ready to request staging",
    stage_requested: "Awaiting staging receipt",
    staged: "Staged",
    health_requested: "Awaiting health receipt",
    unhealthy: "Health check failed",
    healthy: "Healthy in staging",
    promotion_requested: "Awaiting production receipt",
    promoted: "Promoted to production",
    rollback_requested: "Awaiting rollback receipt",
    rolled_back: "Rolled back",
    no_release: "No prepared release",
    failed: "External action failed",
    prepare_release: "Prepare a signed release",
    request_stage: "Request staging",
    await_operator_receipt: "Await operator receipt",
    request_health: "Request a health check",
    await_health_receipt: "Await health receipt",
    request_health_or_rollback: "Retry health or request rollback",
    request_promote: "Request production promotion",
    await_promotion_receipt: "Await production receipt",
    monitor_or_request_rollback: "Monitor or request rollback",
    await_rollback_receipt: "Await rollback receipt",
    complete: "Complete",
    retry_failed_action: "Retry the failed action",
    inspect_state: "Inspect state",
    journalStarted: "Autonomous exploration started",
    journalStopped: "Autonomous exploration stopped",
    journalCompleted: "Generation limit reached",
    journalError: "Provider connection interrupted",
    journalGeneration: "Generation",
    readJourney: "Read journey",
    journeyKicker: "LINEAGE STORY",
    journeyTitle: "Evolution journey",
    journeyLoading: "Gathering the chronicle…",
    journeyTranslating: "Translating journey text to Persian…",
    journeyMeta: "{count} moments in the chronicle",
    journeySynopsisTitle: "Story so far",
    journeyFeaturesColumn: "Features achieved",
    journeySkillsColumn: "Skills achieved",
    journeyStatMoments: "Moments",
    journeyStatEligible: "Eligible",
    journeyStatRejected: "Setbacks",
    journeyStatAchievements: "Milestones",
    journeyStatGeneration: "Generation",
    closeJourney: "Close",
    journeyFailed: "The evolution journey could not be opened.",
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
    helpHostStatus: "Shows whether the host has a provider, model, and API key configured for safe local runs.",
    helpSettings: "Configure the model provider, budgets, timeout, and optional rootless sandbox used for evaluation.",
    helpRunGeneration: "Run a single bounded generation. Produces an eligible or rejected candidate without changing the repository.",
    helpAutonomousEvolution: "Start or stop the continuous open-ended loop that proposes adaptations on an interval.",
    helpDigitalPetriDish: "Observatory for population ecology: living organisms, niches, cooperation, and lineage.",
    helpEcologySignals: "Research-facing metrics for stability, diversity, open-endedness proxy, and latest evaluation evidence.",
    helpResourcePools: "Shared environmental resources that shift with the current selection phase.",
    helpEmergentNiches: "Counts of living organisms by behaviour-derived role such as explorer or guardian.",
    helpCooperationNetwork: "Recent cooperative links between organisms in the bounded population.",
    helpLineageMap: "Parent-child map of every recorded generation. Scroll, zoom, and drag to explore.",
    helpPromotionGate: "Human-controlled evidence, trust, release, and deployment handoff stages. Browser actions never deploy.",
    helpPipelineEvidence: "Create a replay-verified evidence bundle and record a local human approve/reject decision.",
    helpPipelineTrust: "Independent trust authority status: attestation, reviewer policy, and manual authorization.",
    helpPipelineRelease: "Read-only view of sealed candidate artifacts and local promotion readiness.",
    helpPipelineDeployment: "Read-only external deployment handoff. EVO never holds cloud credentials or deploys itself.",
    helpEvolutionJournal: "Public narrative of autonomous progress, unlocked achievements, and journey storytelling.",
    helpAchievements: "Milestones unlocked when selected generations reach host-defined thresholds.",
    helpAuditTrail: "Redacted immutable events from the local audit log for inspection and search.",
    helpConfigured: "Whether required host settings are complete enough to call a provider.",
    helpProvider: "Active model provider for this terrarium (Groq or NVIDIA NIM).",
    helpModel: "Model identifier currently selected for generation requests.",
    helpApiKey: "Whether an API key is stored on the host. The raw secret is never shown.",
    helpEnvFile: "Presence of the local environment file used to persist settings.",
    helpCallsPerRun: "Maximum provider calls allowed inside one evolve/autonomy generation budget.",
    helpEcologicalStability: "Proxy for how steady the living population remains across recent ecology.",
    helpPopulationDiversity: "Proxy for behavioural and lineage variety among living organisms.",
    helpOpenEndednessProxy: "Qualified research proxy for continued novelty; not a claim of open-ended AGI.",
    helpEpoch: "Current ecological epoch counter for the Petri dish simulation.",
    helpLiving: "Living organisms versus the dish carrying capacity.",
    helpBirths: "Total births recorded in the population history.",
    helpExtinct: "Organisms that have died out in the Petri dish.",
    helpMeanEnergy: "Average energy across currently living organisms.",
    helpMeanFitness: "Average fitness across currently living organisms.",
    helpPhase: "Current autonomous worker phase such as waiting, running, or backoff.",
    helpGeneration: "Highest selected generation recorded for the lineage so far.",
    helpAttempts: "Generation attempts consumed versus the configured attempt limit.",
    helpNextInterval: "Seconds the autonomy worker waits between generation attempts.",
    helpEvidenceBundle: "Latest host-authenticated evidence bundle identifier and verification state.",
    helpDeterministicReplay: "Whether the latest bundle’s deterministic replay check passed.",
    helpHumanDecision: "Local human approve/reject assertion attached to the latest verified bundle.",
    helpDeploymentAuthority: "Browser deployment authority is always denied in EVO.",
    helpAuthorityIdentity: "Fingerprint of the local Ed25519 trust authority identity.",
    helpTrustedReviewers: "Number of registered independent reviewers trusted by this host.",
    helpPublicAttestation: "Latest public attestation over a verified evidence bundle.",
    helpIndependentReview: "Latest independently signed reviewer decision.",
    helpPromotionPolicy: "Whether trust policy requirements for promotion are currently satisfied.",
    helpManualAuthorization: "Manual promotion authorization record when policy allows it.",
    helpSealedArtifact: "Latest sealed candidate artifact available for controlled local promotion.",
    helpAuthorizationUse: "Whether the current authorization is ready, missing, or already consumed.",
    helpLocalRepository: "Whether the local repository is clean enough for a controlled release step.",
    helpPromotionState: "Currently active local promotion, if any.",
    helpRollbackState: "Whether a rollback path is available for the active promotion.",
    helpDeploymentDenied: "Reminder that deployment remains permanently outside browser control.",
    helpReleaseCapsule: "Latest signed release capsule prepared for external operator handoff.",
    helpTrustedOperators: "Count of trusted external operators registered for handoff.",
    helpDeploymentPhase: "Current external deployment handoff phase.",
    helpNextDeploymentAction: "Suggested next operator action for the handoff workflow.",
    helpOperatorReceipt: "Latest operator receipt recorded for an external execution step.",
    helpExternalExecution: "External execution is required; EVO does not perform cloud deploys.",
    helpOrganismCard: "One living organism: role, fitness, energy, and lineage identifiers.",
    helpOrganismNoParents: "none (founder line)",
    helpOrganismDetail: "{id} is a living {lineage} from selected generation {generation}, currently acting as {role}. Energy {energy}; fitness {fitness}. Parents: {parents}. Selected adaptations: {adaptations}. Evaluations {evaluations}; collaborations {collaborations} ({successes} successful).",
    helpJourneyStatMoments: "How many journal moments are included in this journey chapter set.",
    helpJourneyStatEligible: "How many eligible adaptations appear in the selected journey window.",
    helpJourneyStatRejected: "How many rejected proposals appear in the selected journey window.",
    helpJourneyStatAchievements: "How many milestone unlock events appear in the selected journey window.",
    helpJourneyStatGeneration: "Highest selected generation reached in the selected journey window.",
    helpJourneyChapter: "One chronological chapter of the evolution story for the selected cutoff.",
    helpJourneySynopsis: "Short synopsis of the story so far through the selected journal point.",
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
    nvidiaGenerationProfile: "نمایه تولید انویدیا",
    nvidiaProfilePrecise: "دقیق (دما ۰٫۲)",
    nvidiaProfileBalanced: "متعادل (دما ۰٫۷)",
    nvidiaProfileExploratory: "اکتشافی (دما ۱٫۰)",
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
    lineageHint: "با کشیدن جابه‌جا شوید · نوارها کاوش می‌کنند · چرخ زوم می‌کند",
    lineageZoomIn: "بزرگ‌نمایی",
    lineageZoomOut: "کوچک‌نمایی",
    lineageZoomReset: "بازنشانی",
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
    pipelineEvidenceStep: "دروازه · v0.7",
    pipelineEvidenceTitle: "شواهد و بازبینی انسانی",
    pipelineEvidenceBlurb: "یک بسته بازپخش را احراز اصالت کنید و سپس تصمیم صریح محلی انسان را ثبت کنید.",
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
    publicTrust: "اعتماد عمومی · نسخه ۰٫۸",
    trustAuthority: "مرجع اعتماد مستقل",
    trustAuthorityDescription: "گواهی عمومی Ed25519 برای شواهد منتشر کنید، تصمیم امضاشدهٔ بازبین مستقل را اعتبارسنجی کنید و سیاست تغییرناپذیر ارتقا را بسنجید.",
    attestEvidence: "انتشار گواهی شواهد",
    authorizePromotion: "صدور مجوز ارتقای دستی",
    trustAuthoritySafety: "کلیدهای بازبین فقط از طریق خط فرمان مدیریت می‌شوند. مجوز، یک سند امضاشده می‌سازد؛ EVO همچنان نمی‌تواند Git را تغییر دهد، push یا merge کند یا چیزی را مستقر سازد.",
    authorityIdentity: "هویت مرجع",
    trustedReviewers: "بازبینان مورد اعتماد",
    publicAttestation: "گواهی عمومی",
    independentReview: "بازبینی مستقل",
    promotionPolicy: "سیاست ارتقا",
    manualAuthorization: "مجوز دستی",
    noAttestation: "هنوز گواهی‌ای وجود ندارد",
    noIndependentReview: "هنوز بازبینی مستقلی وجود ندارد",
    policySatisfied: "سیاست برآورده شده است",
    policyBlocked: "سیاست مسدود است",
    noAuthorization: "هنوز مجوزی صادر نشده است",
    attestationCreated: "گواهی عمومی شواهد ساخته شد",
    promotionAuthorized: "مجوز امضاشدهٔ ارتقای دستی صادر شد",
    controlledRelease: "انتشار کنترل‌شده · نسخه ۰٫۹",
    releaseControl: "ارتقای محلی بازتولیدپذیر",
    releaseControlDescription: "وصلهٔ دقیق و تأییدشده در محیط ایزوله را نگه دارید، یک مجوز امضاشده را فقط یک‌بار مصرف کنید و از خط فرمان بازگردانی دقیق وضعیت را انجام دهید.",
    releaseControlSafety: "اعمال و بازگردانی فقط از خط فرمان و با عبارت تأیید دقیق انجام می‌شوند. EVO هرگز worktree ارتقایافته را commit، push، merge یا مستقر نمی‌کند.",
    sealedArtifact: "بستهٔ مهروموم‌شدهٔ نامزد",
    authorizationUse: "مصرف مجوز",
    localRepository: "مخزن محلی",
    promotionState: "وضعیت ارتقا",
    rollbackState: "وضعیت بازگردانی",
    noArtifact: "هنوز بسته‌ای مهروموم نشده است",
    authorizationReady: "آماده و مصرف‌نشده",
    authorizationUsed: "قبلاً مصرف شده است",
    authorizationMissing: "مجوز معتبری وجود ندارد",
    clean: "پاک",
    dirty: "پاک نیست",
    noActivePromotion: "ارتقای فعالی وجود ندارد",
    rollbackReady: "بازگردانی دقیق آماده است",
    noRollback: "بازگردانی معوقی وجود ندارد",
    productionHandoff: "تحویل به محیط عملیاتی · نسخه ۱٫۰",
    deploymentHandoff: "تحویل امضاشده به اپراتور مستقل استقرار",
    deploymentHandoffDescription: "انتشار commit‌شده را به درخواست‌های امضاشدهٔ مرحله‌بندی، سلامت، محیط عملیاتی و بازگردانی پیوند دهید و سپس رسیدهای اپراتور مستقل را اعتبارسنجی کنید.",
    deploymentHandoffSafety: "این بخش فقط خواندنی است. EVO هیچ کلید دسترسی ابری نگه نمی‌دارد و استقرار شبکه‌ای انجام نمی‌دهد؛ تمام تغییرات بیرونی را اپراتور مستقل اجرا می‌کند.",
    releaseCapsule: "کپسول امضاشدهٔ انتشار",
    trustedOperators: "اپراتورهای مورد اعتماد",
    deploymentPhase: "مرحلهٔ استقرار",
    nextDeploymentAction: "اقدام کنترل‌شدهٔ بعدی",
    operatorReceipt: "آخرین رسید اپراتور",
    externalExecution: "اجرای بیرونی",
    noReleaseCapsule: "هنوز کپسول انتشاری وجود ندارد",
    noOperatorReceipt: "هنوز رسیدی دریافت نشده است",
    required: "الزامی",
    ready_to_stage: "آمادهٔ درخواست مرحله‌بندی",
    stage_requested: "در انتظار رسید مرحله‌بندی",
    staged: "مرحله‌بندی‌شده",
    health_requested: "در انتظار رسید سلامت",
    unhealthy: "بررسی سلامت ناموفق بود",
    healthy: "در محیط آزمایشی سالم است",
    promotion_requested: "در انتظار رسید محیط عملیاتی",
    promoted: "به محیط عملیاتی ارتقا یافت",
    rollback_requested: "در انتظار رسید بازگردانی",
    rolled_back: "بازگردانی شد",
    no_release: "انتشاری آماده نشده است",
    failed: "اقدام بیرونی ناموفق بود",
    prepare_release: "آماده‌سازی انتشار امضاشده",
    request_stage: "درخواست مرحله‌بندی",
    await_operator_receipt: "انتظار برای رسید اپراتور",
    request_health: "درخواست بررسی سلامت",
    await_health_receipt: "انتظار برای رسید سلامت",
    request_health_or_rollback: "تکرار بررسی سلامت یا درخواست بازگردانی",
    request_promote: "درخواست ارتقا به محیط عملیاتی",
    await_promotion_receipt: "انتظار برای رسید محیط عملیاتی",
    monitor_or_request_rollback: "پایش یا درخواست بازگردانی",
    await_rollback_receipt: "انتظار برای رسید بازگردانی",
    complete: "تکمیل‌شده",
    retry_failed_action: "تکرار اقدام ناموفق",
    inspect_state: "بررسی وضعیت",
    journalStarted: "کاوش خودکار آغاز شد",
    journalStopped: "کاوش خودکار متوقف شد",
    journalCompleted: "سقف نسل‌ها تکمیل شد",
    journalError: "ارتباط با ارائه‌دهنده قطع شد",
    journalGeneration: "نسل",
    readJourney: "خواندن سفر",
    journeyKicker: "داستان تبار",
    journeyTitle: "سفر تکامل",
    journeyLoading: "در حال گردآوری روایت…",
    journeyTranslating: "در حال ترجمهٔ متن سفر به فارسی…",
    journeyMeta: "{count} لحظه در روایت",
    journeySynopsisTitle: "داستان تا اینجا",
    journeyFeaturesColumn: "ویژگی‌های به‌دست‌آمده",
    journeySkillsColumn: "مهارت‌های به‌دست‌آمده",
    journeyStatMoments: "لحظه‌ها",
    journeyStatEligible: "واجد شرایط",
    journeyStatRejected: "ناکامی‌ها",
    journeyStatAchievements: "دستاوردها",
    journeyStatGeneration: "نسل",
    closeJourney: "بستن",
    journeyFailed: "باز کردن سفر تکامل ممکن نشد.",
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
    helpHostStatus: "نشان می‌دهد آیا میزبان برای اجرای ایمن محلی، ارائه‌دهنده، مدل و کلید API را پیکربندی کرده است.",
    helpSettings: "ارائه‌دهنده مدل، بودجه، مهلت زمانی و سندباکس اختیاری بدون ریشه را برای ارزیابی تنظیم کنید.",
    helpRunGeneration: "یک نسل محدود اجرا می‌کند و نامزد واجد شرایط یا ردشده می‌سازد؛ مخزن را تغییر نمی‌دهد.",
    helpAutonomousEvolution: "چرخه پیوسته و بی‌پایان را شروع یا متوقف می‌کند که در فواصل زمانی سازگاری پیشنهاد می‌دهد.",
    helpDigitalPetriDish: "رصدخانه بوم‌شناسی جمعیت: جانداران زنده، Nicheها، همکاری و تبار.",
    helpEcologySignals: "معیارهای پژوهشی برای پایداری، تنوع، شاخص بی‌پایانی و تازه‌ترین شواهد ارزیابی.",
    helpResourcePools: "منابع محیطی مشترک که با فاز گزینش فعلی جابه‌جا می‌شوند.",
    helpEmergentNiches: "شمار جانداران زنده بر اساس نقش رفتاری مانند کاوشگر یا نگهبان.",
    helpCooperationNetwork: "پیوندهای همکاری اخیر میان جانداران در جمعیت محدود.",
    helpLineageMap: "نقشه والد-فرزند همه نسل‌های ثبت‌شده. برای کاوش، پیمایش، بزرگ‌نمایی و کشیدن را به کار ببرید.",
    helpPromotionGate: "مراحل شواهد، اعتماد، انتشار و تحویل استقرار تحت کنترل انسان. اقدامات مرورگر هرگز استقرار نمی‌کنند.",
    helpPipelineEvidence: "بسته شواهد تأیید‌شده با بازپخش بسازید و تصمیم محلی تأیید/رد انسانی را ثبت کنید.",
    helpPipelineTrust: "وضعیت مرجع اعتماد مستقل: تأیید عمومی، سیاست بازبین و مجوز دستی.",
    helpPipelineRelease: "نمای فقط‌خواندنی از آثار نامزد مهروموم‌شده و آمادگی ارتقای محلی.",
    helpPipelineDeployment: "تحویل استقرار خارجی فقط‌خواندنی. EVO هرگز اعتبار ابری نگه نمی‌دارد و خودش استقرار نمی‌کند.",
    helpEvolutionJournal: "روایت عمومی پیشرفت خودکار، دستاوردها و داستان‌گویی سفر تکامل.",
    helpAchievements: "دستاوردهایی که با رسیدن نسل‌های برگزیده به آستانه‌های تعریف‌شده میزبان باز می‌شوند.",
    helpAuditTrail: "رویدادهای ویرایش‌شده و تغییرناپذیر از گزارش ممیزی محلی برای بررسی و جست‌وجو.",
    helpConfigured: "آیا تنظیمات لازم میزبان برای تماس با ارائه‌دهنده کامل است.",
    helpProvider: "ارائه‌دهنده فعال مدل برای این زیست‌بوم (Groq یا NVIDIA NIM).",
    helpModel: "شناسه مدل انتخاب‌شده برای درخواست‌های تولید.",
    helpApiKey: "آیا کلید API روی میزبان ذخیره شده است. راز خام هرگز نمایش داده نمی‌شود.",
    helpEnvFile: "وجود فایل محیطی محلی که تنظیمات را نگه می‌دارد.",
    helpCallsPerRun: "حداکثر تماس‌های ارائه‌دهنده مجاز در بودجه یک نسل.",
    helpEcologicalStability: "شاخص تقریبی پایداری جمعیت زنده در بوم‌شناسی اخیر.",
    helpPopulationDiversity: "شاخص تقریبی تنوع رفتاری و تباری میان جانداران زنده.",
    helpOpenEndednessProxy: "شاخص پژوهشی مشروط برای تازگی مداوم؛ ادعای AGI بی‌پایان نیست.",
    helpEpoch: "شمارنده عصر بوم‌شناسی فعلی ظرف پتری.",
    helpLiving: "جانداران زنده در برابر ظرفیت ظرف.",
    helpBirths: "کل زادآوری‌های ثبت‌شده در تاریخ جمعیت.",
    helpExtinct: "جاندارانی که در ظرف پتری منقرض شده‌اند.",
    helpMeanEnergy: "میانگین انرژی جانداران زنده فعلی.",
    helpMeanFitness: "میانگین برازش جانداران زنده فعلی.",
    helpPhase: "فاز فعلی کارگر خودمختار مانند انتظار، اجرا یا عقب‌نشینی.",
    helpGeneration: "بالاترین نسل برگزیده ثبت‌شده برای تبار تا این لحظه.",
    helpAttempts: "تلاش‌های نسل مصرف‌شده در برابر سقف پیکربندی‌شده.",
    helpNextInterval: "ثانیه‌هایی که کارگر خودمختار میان تلاش‌های نسل صبر می‌کند.",
    helpEvidenceBundle: "شناسه و وضعیت تأیید تازه‌ترین بسته شواهد میزبان.",
    helpDeterministicReplay: "آیا بررسی بازپخش قطعی تازه‌ترین بسته موفق بوده است.",
    helpHumanDecision: "تصمیم محلی تأیید/رد انسانی متصل به تازه‌ترین بسته تأییدشده.",
    helpDeploymentAuthority: "اختیار استقرار از مرورگر در EVO همیشه رد می‌شود.",
    helpAuthorityIdentity: "اثرانگشت هویت محلی مرجع اعتماد Ed25519.",
    helpTrustedReviewers: "تعداد بازبینان مستقل ثبت‌شده و مورد اعتماد این میزبان.",
    helpPublicAttestation: "تازه‌ترین تأیید عمومی روی بسته شواهد تأییدشده.",
    helpIndependentReview: "تازه‌ترین تصمیم امضاشده بازبین مستقل.",
    helpPromotionPolicy: "آیا الزامات سیاست اعتماد برای ارتقا فعلاً برقرار است.",
    helpManualAuthorization: "سابقه مجوز ارتقای دستی وقتی سیاست اجازه می‌دهد.",
    helpSealedArtifact: "تازه‌ترین اثر نامزد مهروموم‌شده برای ارتقای کنترل‌شده محلی.",
    helpAuthorizationUse: "آیا مجوز فعلی آماده، غایب یا مصرف‌شده است.",
    helpLocalRepository: "آیا مخزن محلی برای گام انتشار کنترل‌شده به اندازه کافی پاک است.",
    helpPromotionState: "ارتقای محلی فعال فعلی، در صورت وجود.",
    helpRollbackState: "آیا مسیر بازگشت برای ارتقای فعال در دسترس است.",
    helpDeploymentDenied: "یادآوری که استقرار برای همیشه خارج از کنترل مرورگر است.",
    helpReleaseCapsule: "تازه‌ترین کپسول انتشار امضاشده برای تحویل به اپراتور خارجی.",
    helpTrustedOperators: "شمار اپراتورهای خارجی مورد اعتماد برای تحویل.",
    helpDeploymentPhase: "فاز فعلی تحویل استقرار خارجی.",
    helpNextDeploymentAction: "اقدام پیشنهادی بعدی اپراتور در گردش کار تحویل.",
    helpOperatorReceipt: "تازه‌ترین رسید اپراتور برای یک گام اجرای خارجی.",
    helpExternalExecution: "اجرای خارجی لازم است؛ EVO استقرار ابری انجام نمی‌دهد.",
    helpOrganismCard: "یک جاندار زنده: نقش، برازش، انرژی و شناسه‌های تبار.",
    helpOrganismNoParents: "ندارد (خط بنیان‌گذار)",
    helpOrganismDetail: "{id} یک {lineage} زنده از نسل برگزیده {generation} است و فعلاً نقش {role} را دارد. انرژی {energy}؛ برازندگی {fitness}. والدین: {parents}. سازگاری‌های برگزیده: {adaptations}. ارزیابی‌ها {evaluations}؛ همکاری‌ها {collaborations} ({successes} موفق).",
    helpJourneyStatMoments: "تعداد لحظه‌های ژورنال در این مجموعه فصل‌های سفر.",
    helpJourneyStatEligible: "تعداد سازگاری‌های واجد شرایط در بازه سفر انتخاب‌شده.",
    helpJourneyStatRejected: "تعداد پیشنهادهای ردشده در بازه سفر انتخاب‌شده.",
    helpJourneyStatAchievements: "تعداد رویدادهای بازشدن دستاورد در بازه سفر انتخاب‌شده.",
    helpJourneyStatGeneration: "بالاترین نسل برگزیده در بازه سفر انتخاب‌شده.",
    helpJourneyChapter: "یک فصل زمانی از داستان تکامل تا نقطه برش انتخاب‌شده.",
    helpJourneySynopsis: "خلاصه داستان تا اینجا تا نقطه ژورنال انتخاب‌شده.",
  },
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
let openJourneyUntil = null;
let cachedPetri = null;
let cachedEvidenceControl = null;
let cachedTrustAuthority = null;
let cachedPromotionControl = null;
let cachedDeploymentControl = null;
let cachedAchievementCatalog = [];
let cachedAchievementTotal = 0;

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
const modelInput = document.getElementById("model");
const modelSelect = document.getElementById("model-select");
const autonomyForm = document.getElementById("autonomy-form");
const autonomyBadge = document.getElementById("autonomy-badge");
const autonomyStats = document.getElementById("autonomy-stats");
const autonomyObjective = document.getElementById("autonomy-objective");
const journalContainer = document.getElementById("evolution-journal");
const journeyModal = document.getElementById("journey-modal");
const journeyModalBody = document.getElementById("journey-modal-body");
const journeyModalMeta = document.getElementById("journey-modal-meta");
const journeySynopsis = document.getElementById("journey-synopsis");
const journeySynopsisText = document.getElementById("journey-synopsis-text");
const journeySummary = document.getElementById("journey-summary");
const achievementGallery = document.getElementById("achievement-gallery");
const achievementCount = document.getElementById("achievement-count");
const petriStats = document.getElementById("petri-stats");
const lineageMap = document.getElementById("lineage-map");
const lineageViewport = document.getElementById("lineage-viewport");
const lineageZoomLabel = document.getElementById("lineage-zoom-label");
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
const trustAuthorityStatus = document.getElementById("trust-authority-status");
const attestEvidence = document.getElementById("attest-evidence");
const authorizePromotion = document.getElementById("authorize-promotion");
const promotionControlStatus = document.getElementById("promotion-control-status");
const deploymentControlStatus = document.getElementById("deployment-control-status");

function t(key) {
  return I18N[language][key] || I18N.en[key] || key;
}

function helpKeyFromLabel(labelKey) {
  if (!labelKey) return "";
  return `help${labelKey.charAt(0).toUpperCase()}${labelKey.slice(1)}`;
}

function helpAttrs(helpKey) {
  if (!helpKey || !t(helpKey) || t(helpKey) === helpKey) {
    return "";
  }
  const text = t(helpKey);
  return dynamicHelpAttrs(text, helpKey);
}

function dynamicHelpAttrs(text, helpKey = "") {
  const value = String(text || "").trim();
  if (!value) return "";
  const keyAttr = helpKey
    ? ` data-i18n-help="${escapeAttr(helpKey)}"`
    : "";
  return `${keyAttr} data-help="${escapeAttr(value)}" aria-description="${escapeAttr(value)}"`;
}

function formatOrganismHelp(organism) {
  const parents = Array.isArray(organism.parent_ids) ? organism.parent_ids : [];
  const adaptations = Array.isArray(organism.selected_adaptations)
    ? organism.selected_adaptations.length
    : 0;
  return t("helpOrganismDetail")
    .replaceAll("{id}", String(organism.organism_id || "—"))
    .replaceAll(
      "{lineage}",
      parents.length ? t("offspring") : t("founder")
    )
    .replaceAll("{generation}", localizeNumber(organism.generation ?? "—"))
    .replaceAll(
      "{role}",
      t(organism.emergent_role || "undifferentiated")
    )
    .replaceAll("{energy}", localizeNumber(organism.energy ?? "—"))
    .replaceAll(
      "{fitness}",
      localizeNumber(Number(organism.fitness || 0).toFixed(3))
    )
    .replaceAll(
      "{parents}",
      parents.length ? parents.join(", ") : t("helpOrganismNoParents")
    )
    .replaceAll("{adaptations}", localizeNumber(adaptations))
    .replaceAll(
      "{evaluations}",
      localizeNumber(organism.evaluations ?? 0)
    )
    .replaceAll(
      "{collaborations}",
      localizeNumber(organism.collaborations ?? 0)
    )
    .replaceAll(
      "{successes}",
      localizeNumber(organism.successful_collaborations ?? 0)
    );
}

function applyHelpTips(root = document) {
  root.querySelectorAll("[data-i18n-help]").forEach((element) => {
    const key = element.dataset.i18nHelp;
    const text = t(key);
    if (!text || text === key) {
      element.removeAttribute("data-help");
      element.removeAttribute("aria-description");
      return;
    }
    element.dataset.help = text;
    element.setAttribute("aria-description", text);
    element.classList.add("has-help");
  });
}

function ensureHelpTooltip() {
  let tip = document.getElementById("help-tooltip");
  if (tip) return tip;
  tip = document.createElement("div");
  tip.id = "help-tooltip";
  tip.className = "help-tooltip";
  tip.hidden = true;
  tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);
  return tip;
}

function positionHelpTooltip(tip, anchor) {
  const margin = 12;
  const rect = anchor.getBoundingClientRect();
  tip.hidden = false;
  const tipRect = tip.getBoundingClientRect();
  let left = rect.left + rect.width / 2 - tipRect.width / 2;
  let top = rect.top - tipRect.height - 10;
  if (top < margin) {
    top = rect.bottom + 10;
    tip.classList.add("help-tooltip-below");
  } else {
    tip.classList.remove("help-tooltip-below");
  }
  left = Math.max(margin, Math.min(left, window.innerWidth - tipRect.width - margin));
  tip.style.left = `${Math.round(left)}px`;
  tip.style.top = `${Math.round(top)}px`;
}

function showHelpTooltip(anchor) {
  const text = anchor.getAttribute("data-help") || "";
  if (!text.trim()) return;
  const tip = ensureHelpTooltip();
  tip.textContent = text;
  tip.dataset.anchor = "1";
  positionHelpTooltip(tip, anchor);
}

function hideHelpTooltip() {
  const tip = document.getElementById("help-tooltip");
  if (!tip) return;
  tip.hidden = true;
  tip.textContent = "";
  delete tip.dataset.anchor;
}

function initHelpTooltips() {
  document.addEventListener("pointerover", (event) => {
    const target = event.target.closest("[data-help], [data-i18n-help]");
    if (!target || target.closest("#help-tooltip")) return;
    if (!target.getAttribute("data-help") && target.dataset.i18nHelp) {
      applyHelpTips(target.parentElement || document);
    }
    if (target.getAttribute("data-help")) {
      showHelpTooltip(target);
    }
  });
  document.addEventListener("pointerout", (event) => {
    const from = event.target.closest("[data-help], [data-i18n-help]");
    const to = event.relatedTarget && event.relatedTarget.closest
      ? event.relatedTarget.closest("[data-help], [data-i18n-help]")
      : null;
    if (from && from !== to) {
      hideHelpTooltip();
    }
  });
  document.addEventListener("focusin", (event) => {
    const target = event.target.closest("[data-help], [data-i18n-help]");
    if (target && target.getAttribute("data-help")) {
      showHelpTooltip(target);
    }
  });
  document.addEventListener("focusout", () => {
    hideHelpTooltip();
  });
  window.addEventListener("scroll", hideHelpTooltip, true);
  window.addEventListener("resize", hideHelpTooltip);
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
  document.querySelectorAll("[data-i18n-title]").forEach((element) => {
    const label = t(element.dataset.i18nTitle);
    element.title = label;
    element.setAttribute("aria-label", label);
  });
  applyHelpTips();
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.classList.toggle("active", button.dataset.language === language);
  });
  updateLineageZoomLabel();
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
  if (journeyModal.open && openJourneyUntil) {
    journeyModal.querySelectorAll("[data-i18n]").forEach((element) => {
      element.textContent = t(element.dataset.i18n);
    });
    openEvolutionJourney({ timestamp: openJourneyUntil }).catch(() => {});
  }
  renderPetriDish(cachedPetri);
  renderEvidenceControl(cachedEvidenceControl);
  renderTrustAuthority(cachedTrustAuthority);
  renderPromotionControl(cachedPromotionControl);
  renderDeploymentControl(cachedDeploymentControl);
  applyHelpTips();
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
    <article class="gate-status-card has-help ${valid ? "verified" : "restricted"}"${helpAttrs(helpKeyFromLabel(label))}>
      <span>${escapeHtml(t(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
  approvalForm.querySelector("button[type='submit']").disabled = !bundleVerified;
}

function renderTrustAuthority(status) {
  if (!status) return;
  cachedTrustAuthority = status;
  const authority = status.authority || {};
  const attestation = status.latest_attestation;
  const review = status.latest_review;
  const policy = status.policy || {};
  const authorization = status.latest_authorization;
  const attestationValid = Boolean(attestation?.verified);
  const reviewValid = Boolean(review?.verified);
  const policySatisfied = Boolean(policy.satisfied);
  const authorizationValid = Boolean(authorization?.verified && policySatisfied);
  const cards = [
    ["authorityIdentity", authority.fingerprint || t("unverified"), Boolean(authority.fingerprint)],
    ["trustedReviewers", String(status.trusted_reviewer_count || 0), Number(status.trusted_reviewer_count || 0) > 0],
    ["publicAttestation", attestationValid ? attestation.attestation_id : t("noAttestation"), attestationValid],
    ["independentReview", reviewValid ? `${t(review.decision === "approve" ? "approve" : "rejectDecision")} · ${review.reviewer_id}` : t("noIndependentReview"), reviewValid],
    ["promotionPolicy", policySatisfied ? t("policySatisfied") : t("policyBlocked"), policySatisfied],
    ["manualAuthorization", authorizationValid ? authorization.authorization_id : t("noAuthorization"), authorizationValid],
  ];
  trustAuthorityStatus.innerHTML = cards.map(([label, value, valid]) => `
    <article class="gate-status-card has-help ${valid ? "verified" : "restricted"}"${helpAttrs(helpKeyFromLabel(label))}>
      <span>${escapeHtml(t(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
  attestEvidence.disabled = !cachedEvidenceControl?.latest_bundle?.verified;
  authorizePromotion.disabled = !policySatisfied;
}

function renderPromotionControl(status) {
  if (!status) return;
  cachedPromotionControl = status;
  const artifact = status.latest_artifact;
  const artifactValid = Boolean(artifact?.verified);
  const authorizationReady = Boolean(
    status.authorization_current && !status.authorization_consumed
  );
  const active = status.active_promotion;
  const activeValid = Boolean(active?.verified);
  const cards = [
    ["sealedArtifact", artifactValid ? artifact.artifact_id : t("noArtifact"), artifactValid],
    ["authorizationUse", status.authorization_consumed ? t("authorizationUsed") : authorizationReady ? t("authorizationReady") : t("authorizationMissing"), authorizationReady],
    ["localRepository", status.repository_clean ? t("clean") : t("dirty"), Boolean(status.repository_clean)],
    ["promotionState", activeValid ? active.record_id : t("noActivePromotion"), activeValid],
    ["rollbackState", activeValid ? t("rollbackReady") : t("noRollback"), activeValid],
    ["deploymentAuthority", t("denied"), false],
  ];
  promotionControlStatus.innerHTML = cards.map(([label, value, valid]) => `
    <article class="gate-status-card has-help ${valid ? "verified" : "restricted"}"${helpAttrs(helpKeyFromLabel(label))}>
      <span>${escapeHtml(t(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
}

function renderDeploymentControl(status) {
  if (!status) return;
  cachedDeploymentControl = status;
  const release = status.latest_release;
  const receipt = status.latest_receipt;
  const releaseValid = Boolean(release?.verified);
  const operatorCount = Number(status.trusted_operator_count || 0);
  const cards = [
    ["releaseCapsule", releaseValid ? release.release_id : t("noReleaseCapsule"), releaseValid],
    ["trustedOperators", String(operatorCount), operatorCount > 0],
    ["deploymentPhase", t(status.phase || "no_release"), ["healthy", "promoted", "rolled_back"].includes(status.phase)],
    ["nextDeploymentAction", t(status.next_action || "inspect_state"), false],
    ["operatorReceipt", receipt ? `${t(receipt.status)} · ${receipt.operator_id}` : t("noOperatorReceipt"), Boolean(receipt)],
    ["externalExecution", t("required"), Boolean(status.external_execution_required)],
  ];
  deploymentControlStatus.innerHTML = cards.map(([label, value, valid]) => `
    <article class="gate-status-card has-help ${valid ? "verified" : "restricted"}"${helpAttrs(helpKeyFromLabel(label))}>
      <span>${escapeHtml(t(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
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
  document.getElementById("nvidia_generation_profile").value =
    settings.nvidia_generation_profile || "balanced";
  document.getElementById("api_key").value = "";
  document.getElementById("api_key").placeholder = settings.configured
    ? t("keepSavedKey")
    : t("enterNewKey");
  syncModelControls(provider, settings.model || defaults.model);
  syncNvidiaProfileVisibility(provider);
}

function syncNvidiaProfileVisibility(provider) {
  const field = document.getElementById("nvidia-profile-field");
  const select = document.getElementById("nvidia_generation_profile");
  const isNvidia = provider === "nvidia";
  field.hidden = !isNvidia;
  select.disabled = !isNvidia;
  if (!isNvidia) {
    select.removeAttribute("name");
  } else {
    select.name = "nvidia_generation_profile";
  }
}

function populateModelSelect(models, selectedModel) {
  const choices = [...models];
  if (selectedModel && !choices.includes(selectedModel)) {
    choices.unshift(selectedModel);
  }
  modelSelect.innerHTML = choices
    .map(
      (model) =>
        `<option value="${escapeAttr(model)}"${
          model === selectedModel ? " selected" : ""
        }>${escapeHtml(model)}</option>`
    )
    .join("");
}

function syncModelControls(provider, selectedModel) {
  const defaults = DEFAULTS[provider] || DEFAULTS.groq;
  const model = selectedModel || defaults.model;
  const fallback = PROVIDER_MODEL_FALLBACK[provider] || GROQ_MODEL_FALLBACK;
  modelSelect.hidden = false;
  modelSelect.required = true;
  modelSelect.name = "model";
  modelSelect.setAttribute("aria-label", provider === "nvidia" ? "NVIDIA NIM model" : "Groq model");
  modelInput.hidden = true;
  modelInput.required = false;
  modelInput.removeAttribute("name");
  populateModelSelect(fallback, model);
  modelInput.value = modelSelect.value;
  loadProviderModels(provider, model);
}

async function loadProviderModels(provider, selectedModel) {
  try {
    const payload = await api(`/api/models?provider=${encodeURIComponent(provider)}`);
    if (!Array.isArray(payload.models) || !payload.models.length) return;
    if (providerSelect.value !== provider) return;
    populateModelSelect(payload.models, selectedModel || modelSelect.value);
    modelInput.value = modelSelect.value;
  } catch {
    // Keep curated fallback options when the live catalog is unavailable.
  }
}

function renderStatus(settings) {
  const rows = [
    ["configured", t("configured"), settings.configured ? t("yes") : t("no")],
    ["provider", t("provider"), settings.provider || "—"],
    ["model", t("model"), settings.model || "—"],
    ["apiKey", t("apiKey"), settings.api_key ? t("configured") : t("missing")],
    ["envFile", t("envFile"), settings.env_file_exists ? t("present") : t("missing")],
    ["callsPerRun", t("callsPerRun"), settings.max_calls_per_run || "—"],
  ];
  statusGrid.innerHTML = rows
    .map(
      ([key, label, value]) => `
      <div class="has-help"${helpAttrs(helpKeyFromLabel(key))}>
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

function localizeNumber(value) {
  if (value == null || value === "") return "—";
  const raw = String(value);
  const numeric = Number(raw);
  if (Number.isFinite(numeric) && /^-?\d+(\.\d+)?$/.test(raw.trim())) {
    return numeric.toLocaleString(language === "fa" ? "fa-IR" : "en-US");
  }
  if (language !== "fa") return raw;
  return raw.replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]);
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
    ["phase", t("phase"), t(phaseKey)],
    ["generation", t("generation"), state.generation ?? 0],
    ["attempts", t("attempts"), `${state.attempts ?? 0} / ${state.max_generations ?? "—"}`],
    ["nextInterval", t("nextInterval"), `${state.interval_seconds ?? "—"} ${t("seconds")}`],
  ]
    .map(
      ([key, label, value]) => `
        <div class="autonomy-stat has-help"${helpAttrs(helpKeyFromLabel(key))}>
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

function achievementSymbol(id) {
  const milestone = cachedAchievementCatalog.find((item) => item.id === id);
  return milestone?.symbol || "✦";
}

function renderAchievements(achievements) {
  const total = cachedAchievementTotal || cachedAchievementCatalog.length || 0;
  achievementCount.textContent = `${achievements.length} / ${total}`;
  if (!achievements.length) {
    achievementGallery.innerHTML =
      `<p class="empty-state">${escapeHtml(t("noAchievements"))}</p>`;
    return;
  }
  achievementGallery.innerHTML = achievements
    .map((achievement) => {
      const descKey = `achievement_${achievement.id}_desc`;
      return `
        <article class="achievement-card has-help"${helpAttrs(descKey)}>
          <span class="achievement-symbol" aria-hidden="true">${escapeHtml(achievementSymbol(achievement.id))}</span>
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
    .map((entry, index) => {
      const payload = entry.payload || {};
      const isGeneration = entry.event_type === "autonomy.generation";
      const title = isGeneration
        ? `${t("journalGeneration")} ${localizeNumber(payload.generation ?? "—")}`
        : t(titles[entry.event_type] || "evolutionJournal");
      const detail = isGeneration
        ? payload.summary || payload.rejection_reason || "—"
        : entry.event_type === "autonomy.error"
          ? `${payload.message || "—"} ${t("retrying")}`
          : payload.objective || "";
      const meta = isGeneration
        ? `${t("attempt")} ${localizeNumber(payload.attempt ?? "—")} · ${translateStatus(payload.status)} · ${t("score")}: ${localizeNumber(payload.score ?? "—")}`
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
          <div class="timeline-entry-head">
            <h3>${escapeHtml(String(title))}</h3>
            <button
              class="button ghost journey-button"
              type="button"
              data-journey-index="${index}"
              title="${escapeAttr(t("readJourney"))}"
              aria-label="${escapeAttr(`${t("readJourney")}: ${title}`)}"
            >${escapeHtml(t("readJourney"))}</button>
          </div>
          <div class="timeline-meta">${escapeHtml(`${formatTime(entry.timestamp)}${meta ? ` · ${meta}` : ""}`)}</div>
          ${detail ? `<p>${escapeHtml(String(detail))}</p>` : ""}
          ${payload.expected_benefit ? `<p><strong>${escapeHtml(t("expectedBenefit"))}:</strong> ${escapeHtml(String(payload.expected_benefit))}</p>` : ""}
          ${payload.risk ? `<p><strong>${escapeHtml(t("risk"))}:</strong> ${escapeHtml(String(payload.risk))}</p>` : ""}
          ${achievementChips ? `<div class="achievement-unlocks">${achievementChips}</div>` : ""}
        </article>`;
    })
    .join("");
  journalContainer.querySelectorAll("[data-journey-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const entry = cachedJournal[Number(button.dataset.journeyIndex)];
      if (entry) {
        openEvolutionJourney(entry).catch((error) => showToast(error.message));
      }
    });
  });
}

async function openEvolutionJourney(entry) {
  openJourneyUntil = entry.timestamp;
  journeyModalMeta.textContent = "";
  clearJourneyHeaderExtras();
  journeyModal.setAttribute("lang", language);
  journeyModal.setAttribute("dir", language === "fa" ? "rtl" : "ltr");
  journeyModalBody.innerHTML = `<p class="empty-state">${escapeHtml(
    language === "fa" ? t("journeyTranslating") : t("journeyLoading")
  )}</p>`;
  if (typeof journeyModal.showModal === "function") {
    if (!journeyModal.open) {
      journeyModal.showModal();
    }
  } else if (!journeyModal.hasAttribute("open")) {
    journeyModal.setAttribute("open", "");
  }
  try {
    const payload = await api("/api/evolution-journey", {
      method: "POST",
      body: JSON.stringify({
        until: entry.timestamp,
        language,
      }),
    });
    journeyModalMeta.textContent = t("journeyMeta").replace(
      "{count}",
      String(payload.entry_count ?? 0)
    );
    renderJourneySynopsis(payload.synopsis || "", payload.synopsis_title || "");
    renderJourneySummary(payload.summary || {});
    renderJourneyChapters(payload.chapters || [], payload.story || "");
    journeyModalBody.focus();
    if (language === "fa") {
      refreshEvolution().catch(() => {});
    }
  } catch (error) {
    clearJourneyHeaderExtras();
    journeyModalBody.innerHTML = `<p class="empty-state">${escapeHtml(error.message || t("journeyFailed"))}</p>`;
    throw error;
  }
}

function clearJourneyHeaderExtras() {
  if (journeySynopsis) {
    journeySynopsis.hidden = true;
  }
  if (journeySynopsisText) {
    journeySynopsisText.textContent = "";
  }
  if (journeySummary) {
    journeySummary.hidden = true;
    journeySummary.innerHTML = "";
  }
}

function renderJourneySynopsis(synopsis, title) {
  if (!journeySynopsis || !journeySynopsisText) return;
  const text = String(synopsis || "").trim();
  if (!text) {
    journeySynopsis.hidden = true;
    journeySynopsisText.textContent = "";
    return;
  }
  const kicker = journeySynopsis.querySelector(".journey-synopsis-kicker");
  if (kicker) {
    kicker.textContent = title || t("journeySynopsisTitle");
  }
  journeySynopsisText.textContent = text;
  journeySynopsis.hidden = false;
}

function renderJourneySummary(summary) {
  if (!journeySummary) return;
  const cards = [
    ["journeyStatMoments", summary.moments, "info"],
    ["journeyStatEligible", summary.eligible, "success"],
    ["journeyStatRejected", summary.rejected, "danger"],
    ["journeyStatAchievements", summary.achievements, "amber"],
    ["journeyStatGeneration", summary.generation, "canopy"],
  ];
  journeySummary.innerHTML = cards
    .map(
      ([label, value, tone]) => `
        <div class="journey-stat journey-stat-${escapeAttr(tone)} has-help"${helpAttrs(helpKeyFromLabel(label))}>
          <span>${escapeHtml(t(label))}</span>
          <strong>${escapeHtml(localizeNumber(value ?? 0))}</strong>
        </div>`
    )
    .join("");
  journeySummary.hidden = false;
}

function renderJourneyChapters(chapters, fallbackStory) {
  if (!chapters.length) {
    const story = String(fallbackStory || "").trim();
    journeyModalBody.innerHTML = story
      ? story
          .split(/\n\n+/)
          .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
          .join("")
      : `<p class="empty-state">${escapeHtml(t("noEvolutionYet"))}</p>`;
    return;
  }

  journeyModalBody.innerHTML = `
    <div class="journey-timeline" role="list">
      ${chapters
        .map((chapter) => {
          const tone = escapeAttr(chapter.tone || "neutral");
          const badges = (chapter.badges || [])
            .map(
              (badge) =>
                `<span class="journey-badge tone-${escapeAttr(badge.tone || "muted")}">${escapeHtml(badge.label || "")}</span>`
            )
            .join("");
          const tags = (chapter.tags || [])
            .map(
              (tag) =>
                `<span class="journey-tag tone-${escapeAttr(tag.tone || "muted")}">${escapeHtml(tag.label || "")}</span>`
            )
            .join("");
          const details = (chapter.details || [])
            .map((detail) => `<p class="journey-detail">${escapeHtml(String(detail))}</p>`)
            .join("");
          const features = renderJourneyGainColumn(
            chapter.columns?.features_title || t("journeyFeaturesColumn"),
            chapter.features || []
          );
          const skills = renderJourneyGainColumn(
            chapter.columns?.skills_title || t("journeySkillsColumn"),
            chapter.skills || []
          );
          const gains =
            chapter.kind === "generation"
              ? `<div class="journey-gains">${features}${skills}</div>`
              : "";
          return `
            <article class="journey-chapter tone-${tone} has-help" role="listitem"${helpAttrs("helpJourneyChapter")}>
              <div class="journey-chapter-rail" aria-hidden="true">
                <span class="journey-chapter-icon">${escapeHtml(chapter.icon || "●")}</span>
              </div>
              <div class="journey-chapter-card">
                <div class="journey-chapter-head">
                  <div>
                    <h3>${escapeHtml(chapter.title || t("evolutionJournal"))}</h3>
                    ${
                      chapter.timestamp
                        ? `<time class="journey-chapter-time">${escapeHtml(formatTime(chapter.timestamp))}</time>`
                        : ""
                    }
                  </div>
                </div>
                ${badges ? `<div class="journey-badges">${badges}</div>` : ""}
                ${tags ? `<div class="journey-tags">${tags}</div>` : ""}
                <p class="journey-chapter-body">${escapeHtml(String(chapter.body || ""))}</p>
                ${gains}
                ${details}
              </div>
            </article>`;
        })
        .join("")}
    </div>`;
}

function renderJourneyGainColumn(title, items) {
  if (!Array.isArray(items) || !items.length) return "";
  return `
    <section class="journey-gain-column">
      <h4>${escapeHtml(title)}</h4>
      <ul>
        ${items
          .map(
            (item) => `
              <li>
                <strong>${escapeHtml(item.title || "")}</strong>
                <span>${escapeHtml(item.detail || "")}</span>
              </li>`
          )
          .join("")}
      </ul>
    </section>`;
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
      return `<article class="metric-card has-help"${helpAttrs(helpKeyFromLabel(label))}>
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
    ["epoch", t("epoch"), summary.epoch ?? 0],
    ["living", t("living"), `${summary.living ?? 0} / ${summary.capacity ?? 0}`],
    ["births", t("births"), summary.births ?? 0],
    ["extinct", t("extinct"), summary.extinct ?? 0],
    ["meanEnergy", t("meanEnergy"), summary.mean_energy ?? 0],
    ["meanFitness", t("meanFitness"), summary.mean_fitness ?? 0],
  ]
    .map(
      ([key, label, value]) => `
        <div class="petri-stat has-help"${helpAttrs(helpKeyFromLabel(key))}>
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

  const organisms = state.organisms || [];
  if (!organisms.length) {
    lineageMap.innerHTML = "";
    lineageMap.removeAttribute("width");
    lineageMap.removeAttribute("height");
    lineageMap.removeAttribute("viewBox");
    lineageBaseSize = { width: 960, height: 520 };
    applyLineageZoom(1);
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
  const columnWidth = 210;
  const rowHeight = 100;
  const marginX = 88;
  const marginY = 68;
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
  const width = Math.max(
    960,
    marginX * 2 + Math.max(generations.length - 1, 0) * columnWidth + 52
  );
  const height = Math.max(
    520,
    marginY * 2 + Math.max(maxRows - 1, 0) * rowHeight + 36
  );
  lineageBaseSize = { width, height };
  lineageMap.setAttribute("viewBox", `0 0 ${width} ${height}`);
  lineageMap.setAttribute("width", String(width));
  lineageMap.setAttribute("height", String(height));

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
      return `<path class="lineage-edge" d="M ${parent.x + 26} ${parent.y} C ${parent.x + 96} ${parent.y}, ${child.x - 96} ${child.y}, ${child.x - 26} ${child.y}" />`;
    })
    .join("");

  const generationLabels = generations
    .map((generation, column) => {
      const x = marginX + column * columnWidth;
      return `<text class="generation-label" x="${x}" y="28" text-anchor="middle">${escapeHtml(`${t("generation")} ${generation}`)}</text>`;
    })
    .join("");

  const nodes = organisms
    .map((organism) => {
      const position = positions.get(organism.organism_id);
      const alive = organism.status === "alive";
      const energy = Math.max(0, Math.min(100, Number(organism.energy || 0)));
      const help = formatOrganismHelp(organism);
      return `
        <g class="lineage-node ${alive ? "alive" : "extinct"} has-help" transform="translate(${position.x} ${position.y})"${dynamicHelpAttrs(help)} tabindex="0">
          <circle class="node-halo" r="30"></circle>
          <circle class="node-body" r="22"></circle>
          <circle class="energy-ring" r="26" pathLength="100"
            stroke-dasharray="${energy} ${100 - energy}" transform="rotate(-90)"></circle>
          <text class="node-id" y="4" text-anchor="middle">${escapeHtml(organism.organism_id.replace("gnome-", ""))}</text>
          <text class="node-metric" y="42" text-anchor="middle">${escapeHtml(`${t("fitness")} ${Number(organism.fitness || 0).toFixed(2)}`)}</text>
        </g>`;
    })
    .join("");
  lineageMap.innerHTML = `${generationLabels}${edges}${nodes}`;
  applyLineageZoom(lineageZoom);

  populationRoster.innerHTML = organisms
    .filter((organism) => organism.status === "alive")
    .sort((a, b) => Number(b.fitness) - Number(a.fitness))
    .slice(0, 12)
    .map((organism) => {
      const help = formatOrganismHelp(organism);
      return `
        <article class="organism-card has-help"${dynamicHelpAttrs(help)}>
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
        </article>`;
    })
    .join("");
}

const LINEAGE_ZOOM_MIN = 0.4;
const LINEAGE_ZOOM_MAX = 2.75;
const LINEAGE_ZOOM_STEP = 1.18;
let lineageZoom = 1;
let lineageBaseSize = { width: 960, height: 520 };
let lineagePanning = false;
let lineagePanLast = { x: 0, y: 0 };

function updateLineageZoomLabel() {
  if (!lineageZoomLabel) return;
  lineageZoomLabel.textContent = `${Math.round(lineageZoom * 100)}%`;
}

function applyLineageZoom(nextZoom, anchor) {
  if (!lineageMap || !lineageViewport) return;
  const previousZoom = lineageZoom;
  lineageZoom = Math.max(
    LINEAGE_ZOOM_MIN,
    Math.min(LINEAGE_ZOOM_MAX, Number(nextZoom) || 1)
  );
  const width = lineageBaseSize.width * lineageZoom;
  const height = lineageBaseSize.height * lineageZoom;
  lineageMap.style.width = `${width}px`;
  lineageMap.style.height = `${height}px`;
  lineageMap.setAttribute("width", String(width));
  lineageMap.setAttribute("height", String(height));
  updateLineageZoomLabel();

  if (!anchor || previousZoom <= 0) return;
  const rect = lineageViewport.getBoundingClientRect();
  const offsetX = anchor.x - rect.left;
  const offsetY = anchor.y - rect.top;
  const contentX = (lineageViewport.scrollLeft + offsetX) / previousZoom;
  const contentY = (lineageViewport.scrollTop + offsetY) / previousZoom;
  lineageViewport.scrollLeft = contentX * lineageZoom - offsetX;
  lineageViewport.scrollTop = contentY * lineageZoom - offsetY;
}

function resetLineageView() {
  applyLineageZoom(1);
  if (lineageViewport) {
    lineageViewport.scrollLeft = 0;
    lineageViewport.scrollTop = 0;
  }
}

function initLineageInteractions() {
  if (!lineageViewport || lineageViewport.dataset.lineageReady === "true") {
    return;
  }
  lineageViewport.dataset.lineageReady = "true";

  document.getElementById("lineage-zoom-in").addEventListener("click", () => {
    const rect = lineageViewport.getBoundingClientRect();
    applyLineageZoom(lineageZoom * LINEAGE_ZOOM_STEP, {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2,
    });
  });
  document.getElementById("lineage-zoom-out").addEventListener("click", () => {
    const rect = lineageViewport.getBoundingClientRect();
    applyLineageZoom(lineageZoom / LINEAGE_ZOOM_STEP, {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2,
    });
  });
  document
    .getElementById("lineage-zoom-reset")
    .addEventListener("click", () => resetLineageView());

  lineageViewport.addEventListener(
    "wheel",
    (event) => {
      event.preventDefault();
      const factor = event.deltaY < 0 ? LINEAGE_ZOOM_STEP : 1 / LINEAGE_ZOOM_STEP;
      applyLineageZoom(lineageZoom * factor, {
        x: event.clientX,
        y: event.clientY,
      });
    },
    { passive: false }
  );

  lineageViewport.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    lineagePanning = true;
    lineagePanLast = { x: event.clientX, y: event.clientY };
    lineageViewport.classList.add("is-panning");
    lineageViewport.setPointerCapture(event.pointerId);
  });
  lineageViewport.addEventListener("pointermove", (event) => {
    if (!lineagePanning) return;
    lineageViewport.scrollLeft -= event.clientX - lineagePanLast.x;
    lineageViewport.scrollTop -= event.clientY - lineagePanLast.y;
    lineagePanLast = { x: event.clientX, y: event.clientY };
  });
  const endPan = (event) => {
    if (!lineagePanning) return;
    lineagePanning = false;
    lineageViewport.classList.remove("is-panning");
    if (lineageViewport.hasPointerCapture(event.pointerId)) {
      lineageViewport.releasePointerCapture(event.pointerId);
    }
  };
  lineageViewport.addEventListener("pointerup", endPan);
  lineageViewport.addEventListener("pointercancel", endPan);
  lineageViewport.addEventListener("lostpointercapture", () => {
    lineagePanning = false;
    lineageViewport.classList.remove("is-panning");
  });
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
  document.querySelectorAll("details.panel").forEach((panel) => {
    const haystack = panel.textContent.toLowerCase();
    const matches = !needle || haystack.includes(needle);
    panel.classList.toggle("hidden-by-search", Boolean(needle) && !matches);
    if (needle && matches) {
      panel.open = true;
    }
  });
}

async function refresh() {
  const [settings, audit, autonomy, achievements, journal, petri, evidenceControl, trustAuthority, promotionControl, deploymentControl] = await Promise.all([
    api("/api/settings"),
    api("/api/audit?limit=50"),
    api("/api/autonomy"),
    api("/api/achievements"),
    api(`/api/evolution-journal?limit=100&language=${encodeURIComponent(language)}`),
    api("/api/petri-dish"),
    api("/api/evidence-control"),
    api("/api/trust-authority"),
    api("/api/promotion-control"),
    api("/api/deployment-control"),
  ]);
  cachedAchievementCatalog = achievements.milestones || [];
  cachedAchievementTotal = Number(achievements.total || cachedAchievementCatalog.length || 0);
  fillSettings(settings);
  renderStatus(settings);
  renderAudit(audit.events || []);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  renderPetriDish(petri);
  renderEvidenceControl(evidenceControl);
  renderTrustAuthority(trustAuthority);
  renderPromotionControl(promotionControl);
  renderDeploymentControl(deploymentControl);
  applySearch(globalSearch.value);
}

async function refreshEvolution() {
  const [autonomy, achievements, journal, audit, petri, evidenceControl, trustAuthority, promotionControl, deploymentControl] = await Promise.all([
    api("/api/autonomy"),
    api("/api/achievements"),
    api(`/api/evolution-journal?limit=100&language=${encodeURIComponent(language)}`),
    api("/api/audit?limit=50"),
    api("/api/petri-dish"),
    api("/api/evidence-control"),
    api("/api/trust-authority"),
    api("/api/promotion-control"),
    api("/api/deployment-control"),
  ]);
  cachedAchievementCatalog = achievements.milestones || [];
  cachedAchievementTotal = Number(achievements.total || cachedAchievementCatalog.length || 0);
  renderAutonomy(autonomy);
  renderJournal(journal.entries || []);
  renderAudit(audit.events || []);
  renderPetriDish(petri);
  renderEvidenceControl(evidenceControl);
  renderTrustAuthority(trustAuthority);
  renderPromotionControl(promotionControl);
  renderDeploymentControl(deploymentControl);
}

document.querySelectorAll("[data-language]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

providerSelect.addEventListener("change", () => {
  const defaults = DEFAULTS[providerSelect.value];
  document.getElementById("base_url").value = defaults.base_url;
  syncModelControls(providerSelect.value, defaults.model);
  syncNvidiaProfileVisibility(providerSelect.value);
  if (providerSelect.value === "nvidia") {
    document.getElementById("max_output_tokens").value = 4096;
    document.getElementById("request_timeout_seconds").value = 90;
  } else {
    document.getElementById("max_output_tokens").value = 1200;
    document.getElementById("request_timeout_seconds").value = 45;
  }
});

modelSelect.addEventListener("change", () => {
  modelInput.value = modelSelect.value;
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
    renderTrustAuthority(await api("/api/trust-authority"));
    renderPromotionControl(await api("/api/promotion-control"));
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

attestEvidence.addEventListener("click", async () => {
  attestEvidence.disabled = true;
  try {
    await api("/api/trust/attest", { method: "POST", body: "{}" });
    renderTrustAuthority(await api("/api/trust-authority"));
    showToast(t("attestationCreated"));
  } catch (error) {
    showToast(error.message);
  } finally {
    attestEvidence.disabled = !cachedEvidenceControl?.latest_bundle?.verified;
  }
});

authorizePromotion.addEventListener("click", async () => {
  authorizePromotion.disabled = true;
  try {
    await api("/api/trust/authorize", { method: "POST", body: "{}" });
    renderTrustAuthority(await api("/api/trust-authority"));
    renderPromotionControl(await api("/api/promotion-control"));
    showToast(t("promotionAuthorized"));
  } catch (error) {
    showToast(error.message);
  } finally {
    authorizePromotion.disabled = !cachedTrustAuthority?.policy?.satisfied;
  }
});

globalSearch.addEventListener("input", () => applySearch(globalSearch.value));
document.querySelectorAll("[data-stop-toggle]").forEach((element) => {
  element.addEventListener("click", (event) => event.stopPropagation());
  element.addEventListener("keydown", (event) => event.stopPropagation());
});
journeyModal.addEventListener("close", () => {
  openJourneyUntil = null;
});
initLineageInteractions();

setLanguage(language);
initHelpTooltips();
refresh().catch((error) => {
  statusSummary.textContent = error.message;
  showToast(error.message);
});
window.setInterval(() => {
  if (cachedAutonomy?.enabled) {
    refreshEvolution().catch(() => {});
  }
}, 5000);

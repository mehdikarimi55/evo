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

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "درخواست ناموفق بود");
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
    ? "کلید روی میزبان ذخیره شده است؛ برای جایگزینی، کلید جدید را وارد کنید"
    : "کلید تازه ایجادشده ارائه‌دهنده را وارد کنید";
}

function renderStatus(settings) {
  const rows = [
    ["پیکربندی", settings.configured ? "انجام شده" : "انجام نشده"],
    ["ارائه‌دهنده", settings.provider || "—"],
    ["مدل", settings.model || "—"],
    ["کلید API", settings.api_key ? "تنظیم‌شده" : "وارد نشده"],
    ["فایل محیطی", settings.env_file_exists ? "موجود" : "ناموجود"],
    ["درخواست در هر اجرا", settings.max_calls_per_run || "—"],
  ];
  statusGrid.innerHTML = rows
    .map(
      ([label, value]) => `
      <div>
        <dt>${label}</dt>
        <dd>${escapeHtml(String(value))}</dd>
      </div>`
    )
    .join("");
  statusSummary.textContent = settings.configured
    ? `${settings.provider} · ${settings.model}`
    : settings.error || "پیکربندی کامل نیست";
}

const STATUS_LABELS = {
  proposed: "پیشنهادشده",
  eligible: "واجد شرایط",
  rejected: "ردشده",
};

const EVENT_LABELS = {
  "generation.completed": "تکمیل نسل",
  "mutation.applied": "اعمال تغییر",
  "mutation.rejected": "رد تغییر",
};

function translateStatus(value) {
  return STATUS_LABELS[value] || value || "—";
}

function translateEvent(value) {
  return EVENT_LABELS[value] || value || "—";
}

function localizeCandidate(candidate) {
  const proposal = candidate.proposal
    ? {
        مسیر_هدف: candidate.proposal.target_path,
        خلاصه: candidate.proposal.summary,
        منطق_پیشنهاد: candidate.proposal.rationale,
        فایده_موردانتظار: candidate.proposal.expected_benefit,
        ریسک: candidate.proposal.risk,
      }
    : null;
  const score = candidate.score
    ? {
        اعتبار_ساختار: candidate.score.schema_validity,
        انطباق_با_سیاست: candidate.score.policy_compliance,
        کیفیت_استدلال: candidate.score.rationale_quality,
      }
    : null;
  return {
    شناسه_نامزد: candidate.candidate_id,
    اثرانگشت_ژنوم: candidate.genome_fingerprint,
    پیشنهاد: proposal,
    امتیاز: score,
    وضعیت: translateStatus(candidate.status),
    دلیل_رد: candidate.rejection_reason,
  };
}

function localizeEvent(event) {
  return {
    زمان: event.timestamp,
    نوع_رویداد: translateEvent(event.event_type),
    جزئیات: event.payload,
  };
}

function renderAudit(events) {
  if (!events.length) {
    auditBody.innerHTML =
      `<tr><td colspan="6">هنوز رویدادی ثبت نشده است.</td></tr>`;
    return;
  }
  auditBody.innerHTML = events
    .map((event, index) => {
      const payload = event.payload || {};
      const status = payload.status || "—";
      const badgeClass = status === "rejected" ? "badge rejected" : "badge";
      return `
        <tr data-search="${escapeAttr(JSON.stringify(event).toLowerCase())}">
          <td>
            <button
              class="icon-button"
              type="button"
              title="مشاهده جزئیات رویداد"
              aria-label="مشاهده رویداد ${index + 1}"
              data-event-index="${index}"
            >◉</button>
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
      const event = events[Number(button.dataset.eventIndex)];
      evolveResult.hidden = false;
      evolveResult.textContent = JSON.stringify(localizeEvent(event), null, 2);
      evolveResult.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

function formatTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("fa-IR");
}

function escapeHtml(value) {
  return value
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
  evolveButtonLabel.textContent = active ? "در حال فکر کردن…" : "تکامل";
  evolveThinking.hidden = !active;
  evolveResult.setAttribute("aria-busy", String(active));
}

function applySearch(query) {
  const needle = query.trim().toLowerCase();
  document.querySelectorAll(".panel").forEach((panel) => {
    if (!needle) {
      panel.classList.remove("hidden-by-search");
      return;
    }
    const haystack = panel.textContent.toLowerCase();
    panel.classList.toggle("hidden-by-search", !haystack.includes(needle));
  });
  document.querySelectorAll("#audit-body tr[data-search]").forEach((row) => {
    if (!needle) {
      row.classList.remove("hidden-by-search");
      return;
    }
    row.classList.toggle(
      "hidden-by-search",
      !row.dataset.search.includes(needle)
    );
  });
}

async function refresh() {
  const settings = await api("/api/settings");
  fillSettings(settings);
  renderStatus(settings);
  const audit = await api("/api/audit?limit=50");
  renderAudit(audit.events || []);
  applySearch(globalSearch.value);
}

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
    showToast("تنظیمات در فایل .env.local ذخیره شد");
  } catch (error) {
    showToast(error.message);
  }
});

document.getElementById("run-doctor").addEventListener("click", async () => {
  try {
    const result = await api("/api/doctor");
    showToast(`پیکربندی معتبر است: ${result.provider} · ${result.model}`);
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
  evolveResult.textContent = "در انتظار پیشنهاد نامزد از سوی مدل…";
  try {
    const payload = formObject(evolveForm);
    const candidate = await api("/api/evolve", {
      method: "POST",
      body: JSON.stringify({
        task: payload.task,
        mutable_paths: payload.mutable_paths,
      }),
    });
    evolveResult.hidden = false;
    evolveResult.textContent = JSON.stringify(
      localizeCandidate(candidate),
      null,
      2
    );
    showToast(`وضعیت نامزد: ${translateStatus(candidate.status)}`);
    const audit = await api("/api/audit?limit=50");
    renderAudit(audit.events || []);
    applySearch(globalSearch.value);
  } catch (error) {
    showToast(error.message);
    evolveResult.textContent = `خطای EVO: ${error.message}`;
  } finally {
    setEvolveThinking(false);
  }
});

globalSearch.addEventListener("input", () => {
  applySearch(globalSearch.value);
});

refresh().catch((error) => {
  statusSummary.textContent = error.message;
  showToast(error.message);
});

/**
 * ✦ Google Gemini Pure Interface - Client Logic
 * Clean, conversational, privacy-first planning with automatic background currency handling.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const heroView = document.getElementById("heroView");
  const chatStream = document.getElementById("chatStream");
  const chatContainer = document.getElementById("chatContainer");
  const promptForm = document.getElementById("promptForm");
  const promptInput = document.getElementById("promptInput");
  const sendBtn = document.getElementById("sendBtn");
  const newChatBtn = document.getElementById("newChatBtn");
  const topbarNewChatBtn = document.getElementById("topbarNewChatBtn");
  const brandHomeBtn = document.getElementById("brandHomeBtn");
  const recentsList = document.getElementById("recentsList");

  // Sidebar & Theme
  const sidebar = document.getElementById("sidebar");
  const menuToggleBtn = document.getElementById("menuToggleBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeLabel = document.getElementById("themeLabel");

  // Settings
  const openSettingsBtn = document.getElementById("openSettingsBtn");
  const closeSettingsModal = document.getElementById("closeSettingsModal");
  const settingsModal = document.getElementById("settingsModal");
  const apiKeyInput = document.getElementById("apiKeyInput");
  const saveSettingsModalBtn = document.getElementById("saveSettingsModalBtn");

  // State
  let currentSessionId = generateSessionId();
  let currentPlan = null;
  let userApiKey = localStorage.getItem("gemini_user_api_key") || "";
  let recentPlans = JSON.parse(localStorage.getItem("gemini_recent_plans") || "[]");

  // Init
  initTheme();
  renderRecents();
  setupEvents();

  function generateSessionId() {
    return Math.random().toString(36).substring(2, 10);
  }

  function initTheme() {
    const savedTheme = localStorage.getItem("gemini_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeLabel.textContent = savedTheme === "dark" ? "Light mode" : "Dark mode";
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("gemini_theme", next);
    themeLabel.textContent = next === "dark" ? "Light mode" : "Dark mode";
  }

  function setupEvents() {
    // Menu toggle for mobile
    menuToggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Theme
    themeToggleBtn.addEventListener("click", toggleTheme);

    // Settings
    openSettingsBtn.addEventListener("click", () => {
      apiKeyInput.value = userApiKey;
      settingsModal.showModal();
    });

    closeSettingsModal.addEventListener("click", () => settingsModal.close());

    saveSettingsModalBtn.addEventListener("click", () => {
      userApiKey = apiKeyInput.value.trim();
      localStorage.setItem("gemini_user_api_key", userApiKey);
      settingsModal.close();
    });

    // New Chat buttons
    newChatBtn.addEventListener("click", startNewChat);
    if (topbarNewChatBtn) topbarNewChatBtn.addEventListener("click", startNewChat);
    if (brandHomeBtn) brandHomeBtn.addEventListener("click", startNewChat);

    // Auto-resize textarea
    promptInput.addEventListener("input", function() {
      this.style.height = "auto";
      this.style.height = Math.min(this.scrollHeight, 140) + "px";
    });

    // Enter to submit (Shift+Enter for newline)
    promptInput.addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        promptForm.requestSubmit();
      }
    });

    // Suggestion Cards
    document.querySelectorAll(".suggest-card").forEach(card => {
      card.addEventListener("click", () => {
        promptInput.value = card.dataset.prompt;
        promptInput.style.height = "auto";
        promptInput.style.height = Math.min(promptInput.scrollHeight, 140) + "px";
        promptForm.requestSubmit();
      });
    });

    // Form Submit
    promptForm.addEventListener("submit", handleSubmit);
  }

  function unlockInput() {
    promptInput.disabled = false;
    sendBtn.disabled = false;
    setTimeout(() => {
      promptInput.focus();
    }, 50);
  }

  function startNewChat() {
    currentSessionId = generateSessionId();
    currentPlan = null;
    chatStream.innerHTML = "";
    chatStream.classList.add("hidden");
    heroView.classList.remove("hidden");
    promptInput.value = "";
    promptInput.style.height = "auto";
    unlockInput();
    if (sidebar.classList.contains("open")) {
      sidebar.classList.remove("open");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const message = promptInput.value.trim();
    if (!message) return;

    // Transition view
    heroView.classList.add("hidden");
    chatStream.classList.remove("hidden");

    // Append User Message
    appendUserBubble(message);
    promptInput.value = "";
    promptInput.style.height = "auto";
    promptInput.disabled = true;
    sendBtn.disabled = true;

    // Create Agent Row with Thinking indicator
    const { agentRow, thinkingBox, contentCol } = createAgentRow();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          session_id: currentSessionId,
          current_plan: currentPlan,
          api_key: userApiKey || undefined
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let isDone = false;

      while (!isDone) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;
            try {
              const eventObj = JSON.parse(dataStr);
              handleChatEvent(eventObj, thinkingBox, contentCol);
              if (eventObj.type === "done" || eventObj.type === "error") {
                isDone = true;
                break;
              }
            } catch (err) {
              console.error("JSON parse error:", err);
            }
          }
        }
      }

      try {
        await reader.cancel();
      } catch (_) {}

    } catch (err) {
      thinkingBox.innerHTML = `⚠️ Could not complete planning: ${err.message}. Please try again.`;
    } finally {
      unlockInput();
    }
  }

  function handleChatEvent(eventObj, thinkingBox, contentCol) {
    if (eventObj.type === "thought") {
      thinkingBox.innerHTML = `<span class="thinking-sparkle">✦</span> ${escapeHtml(eventObj.content)}`;
    } else if (eventObj.type === "plan") {
      currentPlan = eventObj.data;
      // Remove thinking box once final plan is ready
      thinkingBox.remove();
      renderPlanCard(eventObj.data, contentCol);
      saveRecentPlan(eventObj.data);
      unlockInput();
    } else if (eventObj.type === "followup") {
      thinkingBox.remove();
      renderFollowupText(eventObj.reply, contentCol);
      unlockInput();
    } else if (eventObj.type === "error") {
      thinkingBox.innerHTML = `⚠️ ${escapeHtml(eventObj.message)}`;
      unlockInput();
    } else if (eventObj.type === "done") {
      unlockInput();
    }
  }

  function appendUserBubble(text) {
    const row = document.createElement("div");
    row.className = "chat-row user";
    row.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
    chatStream.appendChild(row);
    scrollToBottom();
  }

  function createAgentRow() {
    const row = document.createElement("div");
    row.className = "chat-row agent";

    const avatar = document.createElement("div");
    avatar.className = "agent-avatar";
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
        <path d="M12 0C12 6.627 6.627 12 0 12C6.627 12 12 17.373 12 24C12 17.373 17.373 12 24 12C17.373 12 12 6.627 12 0Z" fill="url(#geminiMiniGrad)"/>
        <defs>
          <linearGradient id="geminiMiniGrad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
            <stop stop-color="#4285F4"/>
            <stop offset="0.5" stop-color="#9B72CB"/>
            <stop offset="1" stop-color="#D96570"/>
          </linearGradient>
        </defs>
      </svg>
    `;

    const contentCol = document.createElement("div");
    contentCol.className = "agent-content-col";

    const thinkingBox = document.createElement("div");
    thinkingBox.className = "gemini-thinking-box";
    thinkingBox.innerHTML = `<span class="thinking-sparkle">✦</span> Thinking...`;

    contentCol.appendChild(thinkingBox);
    row.appendChild(avatar);
    row.appendChild(contentCol);
    chatStream.appendChild(row);
    scrollToBottom();

    return { agentRow: row, thinkingBox, contentCol };
  }

  function renderPlanCard(plan, container) {
    const curr = plan.currency || "USD";
    const symbol = getCurrencySymbol(curr);

    const planContainer = document.createElement("div");
    planContainer.className = "plan-container";

    // 1. Overview Card
    const headerCard = document.createElement("div");
    headerCard.className = "plan-header-card";
    headerCard.innerHTML = `
      <div class="plan-title-line">
        <h2>${escapeHtml(plan.title)}</h2>
        <p class="plan-summary-text">${escapeHtml(plan.summary)}</p>
      </div>

      <div class="kpi-row">
        <div class="kpi-box">
          <span class="label">Target Budget</span>
          <span class="amount highlight">${symbol}${formatNumber(plan.target_budget, curr)} ${curr}</span>
        </div>
        <div class="kpi-box">
          <span class="label">Planned Expenses</span>
          <span class="amount">${symbol}${formatNumber(plan.allocated_cost, curr)} ${curr}</span>
        </div>
        <div class="kpi-box">
          <span class="label">Contingency Reserve (12%)</span>
          <span class="amount reserve">${symbol}${formatNumber(plan.contingency_reserve, curr)} ${curr}</span>
        </div>
        <div class="kpi-box">
          <span class="label">Duration Horizon</span>
          <span class="amount">${escapeHtml(plan.duration_summary || 'N/A')}</span>
        </div>
      </div>
    `;
    planContainer.appendChild(headerCard);

    // 2. Phases & Checklist
    const phasesSec = document.createElement("div");
    phasesSec.className = "phases-section";
    const planUid = 'p' + Math.random().toString(36).substring(2, 8);

    (plan.phases || []).forEach(phase => {
      const pCard = document.createElement("div");
      pCard.className = "phase-card";

      const tasksHtml = (phase.tasks || []).map(task => `
        <div class="task-item" data-id="${task.id}">
          <input type="checkbox" class="task-checkbox" id="chk_${planUid}_${task.id}">
          <div class="task-content">
            <div class="task-header-row">
              <label for="chk_${planUid}_${task.id}" class="task-title">${escapeHtml(task.title)}</label>
              <span class="task-cost-pill">${symbol}${formatNumber(task.estimated_cost, curr)}</span>
            </div>
            <p class="task-details">${escapeHtml(task.details)}</p>
            <span class="task-meta-tag">⏱️ Est. Duration: ${escapeHtml(task.duration || 'Flexible')}</span>
          </div>
        </div>
      `).join("");

      pCard.innerHTML = `
        <div class="phase-header">
          <h3>${escapeHtml(phase.phase_name)}</h3>
          <span class="phase-budget-tag">Allocation: ${symbol}${formatNumber(phase.phase_budget, curr)}</span>
        </div>
        <div class="phase-desc-sub">${escapeHtml(phase.description)}</div>
        <div class="subtasks-list">
          ${tasksHtml}
        </div>
      `;
      phasesSec.appendChild(pCard);
    });
    planContainer.appendChild(phasesSec);

    // 3. Cost Breakdown Section
    if (plan.cost_breakdown && plan.cost_breakdown.length > 0) {
      const bdSec = document.createElement("div");
      bdSec.className = "breakdown-section";
      
      const barsHtml = plan.cost_breakdown.map(cat => `
        <div class="breakdown-item">
          <div class="breakdown-labels">
            <span>${escapeHtml(cat.category)}</span>
            <span>${symbol}${formatNumber(cat.amount, curr)} (${cat.percentage}%)</span>
          </div>
          <div class="breakdown-track">
            <div class="breakdown-fill" style="width: ${cat.percentage}%"></div>
          </div>
        </div>
      `).join("");

      bdSec.innerHTML = `
        <h3>Estimated Cost Allocation</h3>
        <div class="breakdown-bars">${barsHtml}</div>
      `;
      planContainer.appendChild(bdSec);
    }

    // 4. Practical Tips Section
    if (plan.key_tips && plan.key_tips.length > 0) {
      const tipsSec = document.createElement("div");
      tipsSec.className = "tips-section";
      const tipsHtml = plan.key_tips.map(t => `<li>${escapeHtml(t)}</li>`).join("");
      tipsSec.innerHTML = `
        <h3>Practical Tips & Recommendations</h3>
        <ul class="tips-list">${tipsHtml}</ul>
      `;
      planContainer.appendChild(tipsSec);
    }

    // 5. Actions Bar (Copy, Print, Export)
    const actionsBar = document.createElement("div");
    actionsBar.className = "plan-actions-bar";
    actionsBar.innerHTML = `
      <button class="plan-btn btn-copy-plan">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        Copy Plan
      </button>
      <button class="plan-btn btn-export-md">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
        Export Markdown
      </button>
      <button class="plan-btn btn-print-plan">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
        Print / PDF
      </button>
    `;
    planContainer.appendChild(actionsBar);

    container.appendChild(planContainer);

    // Checkbox toggles
    planContainer.querySelectorAll(".task-checkbox").forEach(chk => {
      chk.addEventListener("change", function() {
        this.closest(".task-item").classList.toggle("done", this.checked);
      });
    });

    // Action button handlers attached directly to this plan's elements
    const copyBtn = actionsBar.querySelector(".btn-copy-plan");
    copyBtn.addEventListener("click", () => copyPlanToClipboard(plan, copyBtn));

    const exportMdBtn = actionsBar.querySelector(".btn-export-md");
    exportMdBtn.addEventListener("click", () => downloadPlanMarkdown(plan));

    const printBtn = actionsBar.querySelector(".btn-print-plan");
    printBtn.addEventListener("click", () => window.print());

    scrollToBottom();
  }

  function renderFollowupText(reply, container) {
    const bubble = document.createElement("div");
    bubble.className = "plan-header-card";
    bubble.style.whiteSpace = "pre-wrap";
    bubble.style.lineHeight = "1.6";
    bubble.textContent = reply;
    container.appendChild(bubble);
    scrollToBottom();
  }

  async function copyPlanToClipboard(plan, btn) {
    try {
      const text = generatePlanMarkdown(plan);
      await navigator.clipboard.writeText(text);
      const originalHtml = btn.innerHTML;
      btn.textContent = "✓ Copied!";
      setTimeout(() => {
        btn.innerHTML = originalHtml;
      }, 2000);
    } catch (e) {
      alert("Failed to copy: " + e.message);
    }
  }

  function downloadPlanMarkdown(plan) {
    try {
      const text = generatePlanMarkdown(plan);
      const blob = new Blob([text], { type: "text/markdown" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const cleanTitle = (plan.title || "task_plan").toLowerCase().replace(/[^a-z0-9]+/g, "_");
      a.download = `${cleanTitle}.md`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert("Export failed: " + e.message);
    }
  }

  function generatePlanMarkdown(plan) {
    const curr = plan.currency || "USD";
    const symbol = getCurrencySymbol(curr);
    const lines = [
      `# ✦ ${plan.title || 'Task Execution Plan'}`,
      `**Target Budget:** ${symbol}${formatNumber(plan.target_budget, curr)} ${curr} | **Duration:** ${plan.duration_summary || 'N/A'}`,
      "",
      "## Overview",
      plan.summary || "",
      "",
      "## Budget Breakdown",
      `- **Total Target Budget:** ${symbol}${formatNumber(plan.target_budget, curr)} ${curr}`,
      `- **Planned Expenses:** ${symbol}${formatNumber(plan.allocated_cost, curr)} ${curr}`,
      `- **Contingency Reserve (12%):** ${symbol}${formatNumber(plan.contingency_reserve, curr)} ${curr}`,
      "",
      "## Actionable Phases & Checklist",
      ""
    ];

    (plan.phases || []).forEach(phase => {
      lines.push(`### ${phase.phase_name} (${symbol}${formatNumber(phase.phase_budget, curr)})`);
      if (phase.description) lines.push(`*${phase.description}*`);
      lines.push("");
      (phase.tasks || []).forEach(t => {
        lines.push(`- [ ] **[${t.id}] ${t.title}** — \`${symbol}${formatNumber(t.estimated_cost, curr)}\` (${t.duration || 'N/A'})`);
        if (t.details) lines.push(`  ${t.details}`);
      });
      lines.push("");
    });

    if (plan.key_tips && plan.key_tips.length > 0) {
      lines.push("## Practical Tips & Recommendations");
      plan.key_tips.forEach(tip => lines.push(`- ${tip}`));
    }

    return lines.join("\n");
  }

  function saveRecentPlan(plan) {
    const title = plan.title || "Untitled Plan";
    const exists = recentPlans.find(p => p.session_id === currentSessionId);
    if (!exists) {
      recentPlans.unshift({
        session_id: currentSessionId,
        title: title,
        date: new Date().toLocaleDateString()
      });
      if (recentPlans.length > 10) recentPlans.pop();
      localStorage.setItem("gemini_recent_plans", JSON.stringify(recentPlans));
      renderRecents();
    }
  }

  function renderRecents() {
    recentsList.innerHTML = "";
    recentPlans.forEach(p => {
      const btn = document.createElement("button");
      btn.className = "recent-item";
      btn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span title="${escapeHtml(p.title)}">${escapeHtml(p.title)}</span>
      `;
      recentsList.appendChild(btn);
    });
  }

  function getCurrencySymbol(code) {
    const map = {
      "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "JPY": "¥",
      "CAD": "C$", "AUD": "A$", "CHF": "CHF", "SGD": "S$", "AED": "AED"
    };
    return map[code] || code + " ";
  }

  function formatNumber(num, curr) {
    const val = Number(num) || 0;
    if (["JPY", "KRW", "VND", "IDR"].includes(curr)) {
      return Math.round(val).toLocaleString();
    }
    const locale = curr === "INR" ? "en-IN" : undefined;
    return val.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function scrollToBottom() {
    chatContainer.scrollTo({
      top: chatContainer.scrollHeight,
      behavior: "smooth"
    });
  }

});

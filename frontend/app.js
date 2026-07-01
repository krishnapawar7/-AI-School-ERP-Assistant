const endpoint = "/chat";
const healthUrl = "/health";

const statusBadge = document.getElementById("health-status");
const sessionIdInput = document.getElementById("session-id");
const studentIdInput = document.getElementById("student-id");
const queryInput = document.getElementById("query");
const geminiCheckbox = document.getElementById("use-gemini");
const sendBtn = document.getElementById("send-btn");
const output = document.getElementById("output");
const historyContainer = document.getElementById("history");

async function checkHealth() {
  try {
    const response = await fetch(healthUrl);
    const payload = await response.json();
    if (response.ok) {
      statusBadge.textContent = payload.gemini_key_configured ? "Gemini ready" : "API ready";
      statusBadge.style.background = payload.gemini_key_configured ? "#d1fae5" : "#e2e8f0";
      statusBadge.style.color = payload.gemini_key_configured ? "#065f46" : "#1e293b";
    } else {
      statusBadge.textContent = "Offline";
      statusBadge.style.background = "#fecdd3";
      statusBadge.style.color = "#991b1b";
    }
  } catch (error) {
    statusBadge.textContent = "Offline";
    statusBadge.style.background = "#fecdd3";
    statusBadge.style.color = "#991b1b";
  }
}

function formatJson(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

async function fetchHistory() {
  try {
    const response = await fetch("/chat/history?limit=5");
    const payload = await response.json();
    if (!response.ok) {
      historyContainer.textContent = "Failed to load history.";
      return;
    }

    if (!payload.history || payload.history.length === 0) {
      historyContainer.textContent = "No recent history available.";
      return;
    }

    historyContainer.innerHTML = payload.history
      .map((entry) => {
        const timestamp = new Date(entry.timestamp).toLocaleString();
        return `<div class="history-card"><strong>${timestamp}</strong><p><strong>Query:</strong> ${entry.query}</p><p><strong>Response:</strong> ${escapeHtml(
          JSON.stringify(entry.response, null, 2)
        )}</p></div>`;
      })
      .join("");
  } catch (error) {
    historyContainer.textContent = `History load failed: ${error}`;
  }
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function onSend() {
  const sessionId = sessionIdInput.value.trim() || "default";
  const studentId = studentIdInput.value.trim();
  const query = queryInput.value.trim();
  const useGemini = geminiCheckbox.checked;

  if (!query) {
    output.textContent = "Please enter a query first.";
    return;
  }

  output.textContent = "Sending request...";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        student_id: studentId || undefined,
        use_gemini: useGemini,
        query,
      }),
    });

    const payload = await response.json();
    output.textContent = formatJson(payload);
    await fetchHistory();
  } catch (error) {
    output.textContent = `Request failed:\n${error}`;
  }
}

sendBtn.addEventListener("click", onSend);
window.addEventListener("load", () => {
  checkHealth();
  fetchHistory();
});

const endpoint = "/chat";
const healthUrl = "/health";

const statusBadge = document.getElementById("health-status");
const sessionIdInput = document.getElementById("session-id");
const studentIdInput = document.getElementById("student-id");
const queryInput = document.getElementById("query");
const geminiCheckbox = document.getElementById("use-gemini");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const refreshBtn = document.getElementById("refresh-btn");
const exampleButtons = document.querySelectorAll(".example-btn");
const responseBox = document.getElementById("response-box");
const errorBox = document.getElementById("error-box");
const historyContainer = document.getElementById("history");
const studentsCount = document.getElementById("students-count");
const teachersCount = document.getElementById("teachers-count");
const staffCount = document.getElementById("staff-count");
const eventsCount = document.getElementById("events-count");
const earningsCount = document.getElementById("earnings-count");
const attendanceValue = document.getElementById("attendance-value");
const boysAttendance = document.getElementById("boys-attendance");
const girlsAttendance = document.getElementById("girls-attendance");

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
    responseBox.textContent = "Please enter a query first.";
    return;
  }

  responseBox.textContent = "Sending request...";

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
    if (!response.ok) {
      showError(payload.detail || "An error occurred while calling the API.");
      responseBox.textContent = formatJson(payload);
      return;
    }

    responseBox.textContent = formatJson(payload);
    showError("");
    await fetchHistory();
  } catch (error) {
    showError(`Request failed: ${error}`);
    responseBox.textContent = "";
  }
}

async function fetchDashboard() {
  try {
    const response = await fetch("/dashboard");
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    const totals = payload.totals || {};
    const dashboard = payload.dashboard || {};

    if (studentsCount) {
      studentsCount.textContent = totals.students ?? dashboard.students ?? studentsCount.textContent;
    }
    if (teachersCount) {
      teachersCount.textContent = totals.teachers ?? dashboard.teachers ?? teachersCount.textContent;
    }
    if (staffCount) {
      staffCount.textContent = totals.staffs ?? dashboard.staffs ?? staffCount.textContent;
    }
    if (eventsCount) {
      eventsCount.textContent = totals.events ?? dashboard.events ?? eventsCount.textContent;
    }
    if (earningsCount) {
      earningsCount.textContent = dashboard.earnings ? `$${dashboard.earnings}` : earningsCount.textContent;
    }
    if (attendanceValue) {
      attendanceValue.textContent = dashboard.attendance ? `${dashboard.attendance}%` : attendanceValue.textContent;
    }
    if (boysAttendance) {
      boysAttendance.textContent = `Boys ${dashboard.boys_attendance ?? dashboard.attendance ?? 0}%`;
    }
    if (girlsAttendance) {
      girlsAttendance.textContent = `${dashboard.girls_attendance ?? 0}%`;
    }
  } catch {
    // Ignore dashboard load errors, keep fallback values.
  }
}

function showError(message) {
  if (!message) {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
    return;
  }

  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

clearBtn.addEventListener("click", () => {
  studentIdInput.value = "";
  queryInput.value = "";
  geminiCheckbox.checked = false;
  responseBox.textContent = "Submit a query to see the ERP assistant response.";
  showError("");
});

refreshBtn.addEventListener("click", fetchHistory);
exampleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.textContent;
    geminiCheckbox.checked = false;
    responseBox.textContent = "Ready to send";
    showError("");
  });
});

sendBtn.addEventListener("click", onSend);
window.addEventListener("load", () => {
  checkHealth();
  fetchDashboard();
  fetchHistory();
});

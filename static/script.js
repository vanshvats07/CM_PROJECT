// script.js - connects the page to the Flask backend.
// It only sends the input and displays what comes back.

const SAMPLE_DATA = "10, 12, 11, 13, 12, 14, 13, 15, 12, 11, 14, 13, 100";

// Get the page elements we need
const dataInput = document.getElementById("dataInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const sampleBtn = document.getElementById("sampleBtn");
const clearBtn = document.getElementById("clearBtn");
const message = document.getElementById("message");
const notice = document.getElementById("notice");
const results = document.getElementById("results");
const tableBody = document.getElementById("tableBody");
const outlierCard = document.getElementById("outlierCard");

// ---------- Helper functions ----------

function showError(text) {
  message.textContent = text;
  message.hidden = false;
}

function hideError() {
  message.hidden = true;
}

// Fill the results table. Outlier rows get a special class (red background).
function fillTable(rows) {
  tableBody.innerHTML = "";

  for (const row of rows) {
    const tr = document.createElement("tr");
    if (row.status === "Outlier") {
      tr.className = "outlier-row";
    }

    const cells = [row.index, row.value, row.z_score];
    for (const text of cells) {
      const td = document.createElement("td");
      td.textContent = text;
      tr.appendChild(td);
    }

    // Status column shows a small colored badge
    const statusCell = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "badge " + row.status.toLowerCase();
    badge.textContent = row.status;
    statusCell.appendChild(badge);
    tr.appendChild(statusCell);

    tableBody.appendChild(tr);
  }
}

// Show the summary cards, graph and table
function showResults(data) {
  document.getElementById("meanValue").textContent = data.mean;
  document.getElementById("stdValue").textContent = data.std;
  document.getElementById("countValue").textContent = data.count;
  document.getElementById("outlierValue").textContent = data.outliers;

  // Red card if outliers were found, green card if not
  const found = Number(data.outliers) > 0;
  outlierCard.className = "card " + (found ? "has-outliers" : "no-outliers");

  // Explain the zero standard deviation case
  if (data.zero_std) {
    notice.textContent = "All values are identical, so the standard deviation is 0 " +
      "and Z-Scores cannot be calculated. Every Z-Score is shown as 0 and no outliers are reported.";
    notice.hidden = false;
  } else {
    notice.hidden = true;
  }

  document.getElementById("plotImage").src = data.plot_url;
  fillTable(data.rows);
  results.hidden = false;
}

// ---------- Button actions ----------

async function analyze() {
  hideError();
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: dataInput.value })
    });
    const data = await response.json();

    if (!response.ok) {
      showError(data.error);
      results.hidden = true;
    } else {
      showResults(data);
    }
  } catch (error) {
    showError("Could not reach the server. Is app.py running?");
  }

  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "Analyze";
}

function loadSample() {
  dataInput.value = SAMPLE_DATA;
  hideError();
}

function clearAll() {
  dataInput.value = "";
  hideError();
  results.hidden = true;
  dataInput.focus();
}

analyzeBtn.addEventListener("click", analyze);
sampleBtn.addEventListener("click", loadSample);
clearBtn.addEventListener("click", clearAll);

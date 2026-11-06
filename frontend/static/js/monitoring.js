let telemetryChartInstance = null;
let pollTimer = null;

async function fetchTelemetryData() {
  try {
    const [telemetryRes, devicesRes] = await Promise.all([
      fetch("/api/monitoring/telemetry"),
      fetch("/api/devices")
    ]);
    const telemetry = await telemetryRes.json();
    const devices = await devicesRes.json();

    updateTelemetryChart(telemetry);
    updateTelemetryTable(devices);
  } catch (err) {
    console.error("Telemetry fetch error:", err);
  }
}

function updateTelemetryChart(data) {
  const ctx = document.getElementById("telemetryChart").getContext("2d");

  // Colors based on status
  const barColors = data.statuses.map(s => {
    if (s === "ONLINE") return "rgba(16, 185, 129, 0.8)";
    if (s === "DEGRADED") return "rgba(245, 158, 11, 0.8)";
    return "rgba(239, 68, 68, 0.8)";
  });

  if (telemetryChartInstance) telemetryChartInstance.destroy();

  telemetryChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Round-Trip Latency (ms)",
        data: data.latencies,
        backgroundColor: barColors,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#9ca3af", maxRotation: 45, minRotation: 45 }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#9ca3af" },
          title: { display: true, text: "Latency (ms)", color: "#9ca3af" }
        }
      },
      plugins: {
        legend: { labels: { color: "#f9fafb" } }
      }
    }
  });
}

function updateTelemetryTable(devices) {
  const tbody = document.getElementById("telemetryTableBody");
  tbody.innerHTML = devices.map(d => {
    let lossBadge = `<span style="color: var(--accent-green);">0% (Optimal)</span>`;
    if (d.packet_loss_pct > 0 && d.packet_loss_pct < 100) {
      lossBadge = `<span style="color: var(--accent-amber);">${d.packet_loss_pct}% (Jitter / Loss)</span>`;
    } else if (d.packet_loss_pct >= 100) {
      lossBadge = `<span style="color: var(--accent-red);">100% (Host Down)</span>`;
    }

    return `
      <tr>
        <td><strong>${d.name}</strong></td>
        <td style="font-family: monospace;">${d.ip_address}</td>
        <td><span class="badge badge-${d.status.toLowerCase()}">${d.status}</span></td>
        <td style="font-family: monospace;">${d.latency_ms !== null ? d.latency_ms + ' ms' : '--'}</td>
        <td>${lossBadge}</td>
        <td>
          <div style="width: 100%; max-width: 120px; height: 8px; background: #374151; border-radius: 4px; overflow: hidden;">
            <div style="width: ${d.status === 'ONLINE' ? '100%' : (d.status === 'DEGRADED' ? '60%' : '0%')}; height: 100%; background: ${d.status === 'ONLINE' ? 'var(--accent-green)' : (d.status === 'DEGRADED' ? 'var(--accent-amber)' : 'var(--accent-red)')};"></div>
          </div>
        </td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="openSshModal(${d.id}, '${d.name}', '${d.ip_address}')">
            CLI Diagnostics
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function setupAutoRefresh() {
  const checkbox = document.getElementById("autoRefreshCheckbox");
  if (pollTimer) clearInterval(pollTimer);

  if (checkbox && checkbox.checked) {
    pollTimer = setInterval(fetchTelemetryData, 5000);
  }

  checkbox.addEventListener("change", (e) => {
    if (e.target.checked) {
      fetchTelemetryData();
      pollTimer = setInterval(fetchTelemetryData, 5000);
    } else {
      if (pollTimer) clearInterval(pollTimer);
    }
  });
}

function reloadPageData() {
  fetchTelemetryData();
}

document.addEventListener("DOMContentLoaded", () => {
  fetchTelemetryData();
  setupAutoRefresh();
});

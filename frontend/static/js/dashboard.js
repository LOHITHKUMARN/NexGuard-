let vlanChartInstance = null;
let statusChartInstance = null;

async function loadDashboard() {
  await Promise.all([
    loadKpiStats(),
    loadRecentIncidents(),
    loadCharts()
  ]);
}

async function loadKpiStats() {
  try {
    const res = await fetch("/api/monitoring/status");
    const data = await res.json();

    document.getElementById("kpiTotal").textContent = data.total_devices;
    document.getElementById("kpiOnline").textContent = data.online_devices;
    document.getElementById("kpiOffline").textContent = data.offline_devices;
    document.getElementById("kpiIncidents").textContent = data.active_incidents;
    document.getElementById("kpiAvgLatency").textContent = `${data.average_latency_ms} ms`;
    document.getElementById("kpiHealth").textContent = `${data.network_health_pct}%`;
  } catch (err) {
    console.error("Error loading KPI metrics:", err);
  }
}

async function loadCharts() {
  try {
    const [reportRes, statusRes] = await Promise.all([
      fetch("/api/reports/summary"),
      fetch("/api/monitoring/status")
    ]);
    const reportData = await reportRes.json();
    const statusData = await statusRes.json();

    // 1. VLAN Health Bar Chart
    const vlanLabels = Object.keys(reportData.vlan_breakdown || {});
    const onlineCounts = vlanLabels.map(k => reportData.vlan_breakdown[k].online);
    const offlineCounts = vlanLabels.map(k => reportData.vlan_breakdown[k].offline);

    const ctxVlan = document.getElementById("vlanBarChart").getContext("2d");
    if (vlanChartInstance) vlanChartInstance.destroy();
    vlanChartInstance = new Chart(ctxVlan, {
      type: "bar",
      data: {
        labels: vlanLabels,
        datasets: [
          {
            label: "Online Devices",
            data: onlineCounts,
            backgroundColor: "rgba(16, 185, 129, 0.8)",
            borderRadius: 6
          },
          {
            label: "Offline / Degraded",
            data: offlineCounts,
            backgroundColor: "rgba(239, 68, 68, 0.8)",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#9ca3af" } },
          y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#9ca3af", stepSize: 1 } }
        },
        plugins: {
          legend: { labels: { color: "#f9fafb" } }
        }
      }
    });

    // 2. Status Doughnut Chart
    const ctxStatus = document.getElementById("statusDoughnutChart").getContext("2d");
    if (statusChartInstance) statusChartInstance.destroy();
    statusChartInstance = new Chart(ctxStatus, {
      type: "doughnut",
      data: {
        labels: ["Online", "Offline", "Degraded"],
        datasets: [{
          data: [statusData.online_devices, statusData.offline_devices, statusData.degraded_devices],
          backgroundColor: ["#10b981", "#ef4444", "#f59e0b"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#f9fafb" } }
        }
      }
    });

  } catch (err) {
    console.error("Error creating charts:", err);
  }
}

async function loadRecentIncidents() {
  const tbody = document.getElementById("recentIncidentsTable");
  try {
    const res = await fetch("/api/incidents");
    const data = await res.json();

    if (data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No open incidents detected. All devices operational.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.slice(0, 5).map(inc => `
      <tr>
        <td><span class="badge badge-${inc.severity.toLowerCase()}">${inc.severity}</span></td>
        <td><strong>${inc.device_name}</strong></td>
        <td>${inc.title}</td>
        <td><span class="badge badge-${inc.status === 'OPEN' ? 'offline' : 'online'}">${inc.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="openSshModal(${inc.device_id}, '${inc.device_name}', '${inc.device_ip}')">
            CLI Check
          </button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="color: var(--accent-red);">Failed to load incidents: ${err.message}</td></tr>`;
  }
}

async function runSubnetScan() {
  const cidr = document.getElementById("scanCidrInput").value.trim();
  const outputEl = document.getElementById("scanResultOutput");
  if (!cidr) return;

  outputEl.textContent = `[+] Initiating ICMP ping sweep on ${cidr}...\n[+] Sending non-blocking discovery packets...`;

  try {
    const res = await fetch("/api/monitoring/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cidr })
    });
    const data = await res.json();

    if (data.error) {
      outputEl.textContent = `[!] Error: ${data.error}`;
      return;
    }

    let report = `=== Subnet Discovery Results: ${data.subnet} ===\n`;
    report += `Scanned Hosts: ${data.total_scanned} | Online Responders: ${data.online_hosts}\n\n`;
    data.results.forEach(r => {
      report += `[${r.status.padEnd(8)}] ${r.ip_address.padEnd(16)} Latency: ${r.latency_ms !== null ? r.latency_ms + 'ms' : 'TIMEOUT'} | Loss: ${r.packet_loss_pct}%\n`;
    });

    outputEl.textContent = report;
  } catch (e) {
    outputEl.textContent = `[!] Network scan error: ${e.message}`;
  }
}

function reloadPageData() {
  loadDashboard();
}

document.addEventListener("DOMContentLoaded", loadDashboard);

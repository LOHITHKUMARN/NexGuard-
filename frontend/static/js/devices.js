let cachedDevices = [];

async function loadDevices() {
  const tbody = document.getElementById("deviceTableBody");
  try {
    const res = await fetch("/api/devices");
    const data = await res.json();
    cachedDevices = data;
    renderDeviceTable(data);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="11" style="color: var(--accent-red); text-align: center;">Failed to load devices: ${err.message}</td></tr>`;
  }
}

function renderDeviceTable(devices) {
  const tbody = document.getElementById("deviceTableBody");
  if (devices.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 30px;">No matching devices found.</td></tr>`;
    return;
  }

  tbody.innerHTML = devices.map(d => `
    <tr id="device-row-${d.id}">
      <td><strong>${d.name}</strong></td>
      <td style="font-family: monospace;">${d.ip_address}</td>
      <td>${d.device_type}</td>
      <td style="font-size: 0.8rem; color: var(--text-secondary);">${d.vendor}</td>
      <td>${d.location}</td>
      <td>
        <span class="badge ${d.vlan_id ? 'badge-info' : 'badge-unknown'}">
          ${d.vlan_id ? 'VLAN ' + d.vlan_id : 'Infra'}
        </span>
      </td>
      <td>
        <span class="badge badge-${d.status.toLowerCase()}">${d.status}</span>
      </td>
      <td style="font-family: monospace;">${d.latency_ms !== null ? d.latency_ms + ' ms' : '--'}</td>
      <td style="font-family: monospace; color: ${d.packet_loss_pct > 0 ? 'var(--accent-red)' : 'var(--text-secondary)'};">
        ${d.packet_loss_pct}%
      </td>
      <td style="font-size: 0.78rem; color: var(--text-muted);">${d.last_checked}</td>
      <td>
        <div style="display: flex; gap: 6px;">
          <button class="btn btn-secondary btn-sm" title="Quick Ping" onclick="pingSingleDevice(${d.id})">
            📶 Ping
          </button>
          <button class="btn btn-secondary btn-sm" title="Cisco CLI Diagnostics" onclick="openSshModal(${d.id}, '${d.name}', '${d.ip_address}')">
            ⚡ CLI
          </button>
          <button class="btn btn-danger btn-sm" title="Delete Device" onclick="deleteDevice(${d.id})">
            🗑️
          </button>
        </div>
      </td>
    </tr>
  `).join("");
}

function filterDeviceTable() {
  const searchVal = document.getElementById("deviceSearchInput").value.toLowerCase();
  const vlanVal = document.getElementById("vlanFilterSelect").value;
  const statusVal = document.getElementById("statusFilterSelect").value;

  const filtered = cachedDevices.filter(d => {
    // Search matching
    const matchesSearch = d.name.toLowerCase().includes(searchVal) ||
      d.ip_address.toLowerCase().includes(searchVal) ||
      d.location.toLowerCase().includes(searchVal) ||
      d.device_type.toLowerCase().includes(searchVal);

    // VLAN matching
    let matchesVlan = true;
    if (vlanVal === "infra") {
      matchesVlan = !d.vlan_id;
    } else if (vlanVal) {
      matchesVlan = d.vlan_id === parseInt(vlanVal);
    }

    // Status matching
    let matchesStatus = true;
    if (statusVal) {
      matchesStatus = d.status === statusVal;
    }

    return matchesSearch && matchesVlan && matchesStatus;
  });

  renderDeviceTable(filtered);
}

async function pingSingleDevice(deviceId) {
  const row = document.getElementById(`device-row-${deviceId}`);
  if (row) row.style.opacity = "0.5";

  try {
    const res = await fetch(`/api/devices/${deviceId}/ping`, { method: "POST" });
    if (res.ok) {
      loadDevices();
    }
  } catch (err) {
    alert("Ping failed: " + err.message);
  } finally {
    if (row) row.style.opacity = "1";
  }
}

async function deleteDevice(deviceId) {
  if (!confirm("Are you sure you want to remove this device from NexGuard?")) return;
  try {
    const res = await fetch(`/api/devices/${deviceId}`, { method: "DELETE" });
    if (res.ok) {
      loadDevices();
    }
  } catch (err) {
    alert("Failed to delete device: " + err.message);
  }
}

function openAddDeviceModal() {
  document.getElementById("addDeviceModal").style.display = "flex";
}

function closeAddDeviceModal() {
  document.getElementById("addDeviceModal").style.display = "none";
}

async function submitNewDevice(e) {
  e.preventDefault();
  const name = document.getElementById("newDevName").value.trim();
  const ip = document.getElementById("newDevIp").value.trim();
  const devType = document.getElementById("newDevType").value;
  const vendor = document.getElementById("newDevVendor").value.trim();
  const location = document.getElementById("newDevLocation").value.trim();
  const vlan = document.getElementById("newDevVlan").value;

  const payload = {
    name,
    ip_address: ip,
    device_type: devType,
    vendor,
    location,
    vlan_id: vlan ? parseInt(vlan) : null
  };

  try {
    const res = await fetch("/api/devices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      closeAddDeviceModal();
      document.getElementById("addDeviceForm").reset();
      loadDevices();
    } else {
      const err = await res.json();
      alert("Error: " + (err.error || "Failed to add device"));
    }
  } catch (e) {
    alert("Network error: " + e.message);
  }
}

function reloadPageData() {
  loadDevices();
}

document.addEventListener("DOMContentLoaded", loadDevices);

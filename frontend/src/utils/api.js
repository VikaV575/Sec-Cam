import { API } from "../constants.js";

export async function refreshDevices() {
  const res = await fetch(`${API}/devices`);
  return res.json();
}

export async function sendCommand(deviceId, body) {
  await fetch(`${API}/devices/${deviceId}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function snapshot(deviceId) {
  await sendCommand(deviceId, { type: "snapshot" });
}

export async function record(deviceId, seconds) {
  await sendCommand(deviceId, { type: "record", seconds });
}

export async function startLive(deviceId) {
  const res = await fetch(`${API}/devices/${deviceId}/live/start`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Failed to start live for device ${deviceId}`);
  }

  return res.json();
}

export async function stopLive(deviceId) {
  const res = await fetch(`${API}/devices/${deviceId}/live/stop`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Failed to stop live for device ${deviceId}`);
  }

  return res.json();
}

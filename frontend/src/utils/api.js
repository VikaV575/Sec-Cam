import { API } from "../constants.js";

async function readJson(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed with ${res.status}`);
  }
  return data;
}

export async function refreshDevices() {
  const res = await fetch(`${API}/devices`);
  return readJson(res);
}

export async function sendCommand(deviceId, body) {
  const res = await fetch(`${API}/devices/${deviceId}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJson(res);
}

export async function snapshot(deviceId) {
  return sendCommand(deviceId, { type: "snapshot" });
}

export async function record(deviceId, seconds) {
  return sendCommand(deviceId, { type: "record", seconds });
}

export async function deleteMedia(deviceId, mediaId) {
  const res = await fetch(`${API}/devices/${deviceId}/media/${mediaId}`, {
    method: "DELETE",
  });
  return readJson(res);
}

export async function startLive(deviceId) {
  const res = await fetch(`${API}/devices/${deviceId}/live/start`, {
    method: "POST",
  });
  return readJson(res);
}

export async function stopLive(deviceId) {
  const res = await fetch(`${API}/devices/${deviceId}/live/stop`, {
    method: "POST",
  });
  return readJson(res);
}

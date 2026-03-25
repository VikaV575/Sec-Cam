import { useState } from "react";
import { isOnline, timeAgo } from "../utils/time.js";
import { snapshot, record, startLive, stopLive } from "../utils/api.js";
import LiveView from "./LiveView.jsx";
import "./DeviceCard.css";

export default function DeviceCard({ device, lastUploadUrl }) {
  const [seconds, setSeconds] = useState(5);
  const [isLive, setIsLive] = useState(false);
  const [liveLoading, setLiveLoading] = useState(false);
  const deviceOnline = isOnline(device.last_seen);

  async function handleLiveToggle() {
    if (liveLoading) return;

    setLiveLoading(true);
    try {
      if (isLive) {
        await stopLive(device.id);
        setIsLive(false);
      } else {
        await startLive(device.id);
        setIsLive(true);
      }
    } catch (error) {
      console.error("Live toggle failed", error);
    } finally {
      setLiveLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <div className="device-name">{device.name}</div>
          <div className="device-id">{device.id}</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className={`badge ${deviceOnline ? "online" : "offline"}`}>
            <span className="badge-dot" />
            {deviceOnline ? "Online" : "Offline"}
          </div>
          <div className="last-seen">seen {timeAgo(device.last_seen)}</div>
        </div>
      </div>

      <div className="divider" />

      <div className="actions">
        <button className="action-btn snapshot" onClick={() => snapshot(device.id)}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </svg>
          Snapshot
        </button>

        <div className="seconds-input-wrap">
          <span className="seconds-label">sec</span>
          <input
            className="seconds-input"
            type="number"
            min="1"
            max="60"
            value={seconds}
            onChange={(e) => setSeconds(e.target.value)}
          />
        </div>

        <button className="action-btn record" onClick={() => record(device.id, Number(seconds))}>
          <svg viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="8" />
          </svg>
          Record
        </button>

        <button
          className={`action-btn live${isLive ? " active" : ""}`}
          onClick={handleLiveToggle}
          disabled={liveLoading || !deviceOnline}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="5 3 19 12 5 21 5 3" fill={isLive ? "currentColor" : "none"} />
          </svg>
          {liveLoading ? "..." : isLive ? "Stop" : "Live"}
        </button>
      </div>

      {isLive && (
        <div className="live-view-wrap">
          <LiveView deviceId={device.id} />
        </div>
      )}

      {lastUploadUrl && (
        <a className="upload-link" href={lastUploadUrl} target="_blank" rel="noreferrer">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          Open last upload
        </a>
      )}
    </div>
  );
}

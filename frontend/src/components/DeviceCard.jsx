import { useState } from "react";
import { API } from "../constants.js";
import { isOnline, timeAgo } from "../utils/time.js";
import { snapshot, record, startLive, stopLive } from "../utils/api.js";
import LiveView from "./LiveView.jsx";
import "./DeviceCard.css";

const STATUS_LABELS = {
  queued: "Queued",
  running: "Running",
  completed: "Completed",
  failed: "Failed",
};

const COMMAND_LABELS = {
  snapshot: "Snapshot",
  record: "Record video",
  start_live: "Start live",
  stop_live: "Stop live",
};

function absoluteMediaUrl(url) {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return `${API}${url}`;
}

export default function DeviceCard({ device, onActivityChange }) {
  const [seconds, setSeconds] = useState(5);
  const [isLive, setIsLive] = useState(false);
  const [liveLoading, setLiveLoading] = useState(false);
  const [commandLoading, setCommandLoading] = useState(false);
  const [actionError, setActionError] = useState("");
  const deviceOnline = isOnline(device.last_seen);
  const media = device.media || [];
  const commands = device.commands || [];

  async function runCommand(action) {
    if (commandLoading) return;

    setCommandLoading(true);
    setActionError("");
    try {
      await action();
      await onActivityChange?.();
    } catch (error) {
      setActionError(error.message || "Command failed");
    } finally {
      setCommandLoading(false);
    }
  }

  async function handleLiveToggle() {
    if (liveLoading) return;

    setLiveLoading(true);
    setActionError("");
    try {
      if (isLive) {
        await stopLive(device.id);
        setIsLive(false);
      } else {
        await startLive(device.id);
        setIsLive(true);
      }
      await onActivityChange?.();
    } catch (error) {
      setActionError(error.message || "Live command failed");
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
        <button
          className="action-btn snapshot"
          onClick={() => runCommand(() => snapshot(device.id))}
          disabled={!deviceOnline || commandLoading}
        >
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

        <button
          className="action-btn record"
          onClick={() => runCommand(() => record(device.id, Number(seconds)))}
          disabled={!deviceOnline || commandLoading}
        >
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

      {actionError && <div className="action-error">{actionError}</div>}

      {isLive && (
        <div className="live-view-wrap">
          <LiveView deviceId={device.id} />
        </div>
      )}

      <div className="activity-grid">
        <section className="activity-panel">
          <div className="activity-title">Recent media</div>
          {media.length === 0 ? (
            <div className="activity-empty">No captures uploaded yet.</div>
          ) : (
            <div className="media-grid">
              {media.slice(0, 6).map((item) => {
                const url = absoluteMediaUrl(item.url);
                return (
                  <a
                    key={item.id}
                    className="media-item"
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    title={item.filename}
                  >
                    {item.media_type === "image" ? (
                      <img src={url} alt={item.filename} loading="lazy" />
                    ) : item.media_type === "video" ? (
                      <video src={url} preload="metadata" controls />
                    ) : (
                      <div className="file-preview">File</div>
                    )}
                    <div className="media-meta">
                      <span>{item.media_type}</span>
                      <span>{timeAgo(item.uploaded_at)}</span>
                    </div>
                  </a>
                );
              })}
            </div>
          )}
        </section>

        <section className="activity-panel">
          <div className="activity-title">Command status</div>
          {commands.length === 0 ? (
            <div className="activity-empty">No commands sent yet.</div>
          ) : (
            <div className="command-list">
              {commands.slice(0, 6).map((command) => (
                <div className="command-row" key={command.id}>
                  <div>
                    <div className="command-name">
                      {COMMAND_LABELS[command.type] || command.type}
                      {command.type === "record" && command.seconds ? ` · ${command.seconds}s` : ""}
                    </div>
                    <div className="command-time">{timeAgo(command.updated_at || command.created_at)}</div>
                    {command.error && <div className="command-error">{command.error}</div>}
                  </div>
                  <span className={`command-status ${command.status}`}>
                    {STATUS_LABELS[command.status] || command.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

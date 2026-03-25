import "./LiveView.css";

export default function LiveView({ deviceId }) {
  const webrtcUrl = `http://${window.location.hostname}:8889/live/${deviceId}`;

  return (
    <iframe
      title={`Live stream ${deviceId}`}
      src={webrtcUrl}
      className="live-iframe"
      allow="autoplay; fullscreen; picture-in-picture"
      allowFullScreen
    />
  );
}

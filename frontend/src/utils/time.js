export function isOnline(lastSeenIso) {
  if (!lastSeenIso) return false;
  return Date.now() - new Date(lastSeenIso).getTime() < 30_000;
}

export function timeAgo(lastSeenIso) {
  if (!lastSeenIso) return "never";
  const diff = Math.floor((Date.now() - new Date(lastSeenIso).getTime()) / 1000);
  if (diff < 5) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

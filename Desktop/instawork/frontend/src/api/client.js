const BASE = "http://localhost:8000";

export async function ingestVideo(file, tagger = "gpt4o") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("tagger", tagger);
  const res = await fetch(`${BASE}/videos`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function searchVideos(q) {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function streamUrl(videoId) {
  return `${BASE}/videos/${videoId}/stream`;
}

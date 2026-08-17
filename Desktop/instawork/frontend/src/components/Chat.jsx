import { useState, useRef, useEffect } from "react";
import { ingestVideo, searchVideos, streamUrl } from "../api/client";

let _id = 0;
const uid = () => ++_id;

const PIPELINES = [
  { id: "gpt4o",  label: "GPT-4o",  color: "#10b981", bg: "#d1fae5" },
  { id: "gemini", label: "Gemini",  color: "#8b5cf6", bg: "#ede9fe" },
];

const WELCOME = {
  id: uid(), role: "system", type: "text",
  text: "Upload a workplace video to tag it with AI, or search across ingested videos.",
};

export default function Chat() {
  const [messages, setMessages]   = useState([WELCOME]);
  const [input, setInput]         = useState("");
  const [pipeline, setPipeline]   = useState("gpt4o");
  const [busy, setBusy]           = useState(false);
  const fileRef   = useRef(null);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function push(msg) {
    const m = { id: uid(), ...msg };
    setMessages(prev => [...prev, m]);
    return m.id;
  }

  function patch(id, data) {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, ...data } : m));
  }

  async function handleSearch(e) {
    e.preventDefault();
    const q = input.trim();
    if (!q || busy) return;
    setInput("");
    setBusy(true);
    push({ role: "user", type: "text", text: q });
    const mid = push({ role: "system", type: "search", status: "loading", query: q, results: null });
    try {
      const data = await searchVideos(q);
      patch(mid, { status: "done", results: data });
    } catch {
      patch(mid, { status: "error", error: "Search failed — is the backend running?" });
    }
    setBusy(false);
    inputRef.current?.focus();
  }

  async function handleFileChange(e) {
    const file = e.target.files[0];
    if (!file || busy) return;
    e.target.value = "";
    setBusy(true);
    const p = PIPELINES.find(x => x.id === pipeline);
    push({ role: "user", type: "text", text: `Uploading ${file.name} via ${p.label}` });
    const mid = push({ role: "system", type: "ingest", status: "processing", filename: file.name, pipeline, video: null });
    try {
      const video = await ingestVideo(file, pipeline);
      patch(mid, { video, status: video.status });
    } catch {
      patch(mid, { status: "error", error: "Upload failed — check the backend logs." });
    }
    setBusy(false);
  }

  return (
    <div style={s.shell}>
      <header style={s.header}>
        <div style={s.headerLeft}>
          <span style={s.logoMark}>IW</span>
          <div>
            <div style={s.logoName}>Video Intelligence</div>
            <div style={s.logoSub}>Instawork · AI Tagging & Search</div>
          </div>
        </div>
        <div style={s.headerRight}>
          <span style={s.headerPill}>pgvector</span>
          <span style={s.headerPill}>GPT-4o</span>
          <span style={{ ...s.headerPill, background: "#ede9fe", color: "#7c3aed" }}>Gemini</span>
        </div>
      </header>

      <div style={s.feed}>
        {messages.map(msg => <Msg key={msg.id} msg={msg} />)}
        {busy && <Typing />}
        <div ref={bottomRef} />
      </div>

      <div style={s.bar}>
        <div style={s.barInner}>
          {/* pipeline toggle */}
          <div style={s.toggle}>
            {PIPELINES.map(p => (
              <button
                key={p.id}
                style={{ ...s.toggleBtn, ...(pipeline === p.id ? { background: p.bg, color: p.color, borderColor: p.color } : {}) }}
                onClick={() => setPipeline(p.id)}
                title={`Use ${p.label} for video tagging`}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* upload */}
          <input type="file" accept="video/*" ref={fileRef} style={{ display: "none" }} onChange={handleFileChange} />
          <button style={s.uploadBtn} onClick={() => fileRef.current.click()} disabled={busy} title="Upload video">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Upload
          </button>

          {/* search */}
          <form style={s.searchForm} onSubmit={handleSearch}>
            <input
              ref={inputRef}
              style={s.searchInput}
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder='Search — "frying", "forklift operation", "food safety"...'
              disabled={busy}
              autoFocus
            />
            <button style={{ ...s.searchBtn, ...(busy ? s.searchBtnDim : {}) }} type="submit" disabled={busy}>
              Search
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function Msg({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div style={{ ...s.row, ...(isUser ? s.rowUser : {}) }}>
      {!isUser && <div style={s.avatar}>IW</div>}
      <div style={{ ...s.bubble, ...(isUser ? s.bubbleUser : s.bubbleSystem) }}>
        {msg.type === "text"   && <p style={{ ...s.text, ...(isUser ? { color: "#fff" } : {}) }}>{msg.text}</p>}
        {msg.type === "ingest" && <IngestCard msg={msg} />}
        {msg.type === "search" && <SearchCard msg={msg} />}
      </div>
    </div>
  );
}

function IngestCard({ msg }) {
  const { status, filename, pipeline, video, error } = msg;
  const p = PIPELINES.find(x => x.id === pipeline) || PIPELINES[0];

  return (
    <div style={s.card}>
      <div style={s.cardHead}>
        <div style={s.cardTitle}>
          <span style={s.cardIcon}>🎬</span>
          <span>{filename}</span>
        </div>
        <div style={s.cardMeta}>
          <span style={{ ...s.pill, background: p.bg, color: p.color }}>{p.label}</span>
          <StatusPill status={status} />
        </div>
      </div>

      {status === "processing" && (
        <div style={s.processingBar}>
          <div style={s.processingFill} />
        </div>
      )}

      {status === "ready" && video?.id && (
        <video controls style={s.player} src={streamUrl(video.id)} />
      )}

      {status === "ready" && video?.description && (
        <p style={s.desc}>{video.description}</p>
      )}

      {status === "ready" && video?.tags?.length > 0 && (
        <div style={s.tags}>
          {video.tags.map(t => <Tag key={t} label={t} />)}
        </div>
      )}

      {(status === "error" || status === "failed") && (
        <p style={s.errText}>{error || video?.error}</p>
      )}
    </div>
  );
}

function SearchCard({ msg }) {
  const { status, query, results, error } = msg;

  if (status === "loading") return (
    <div style={s.loadingRow}>
      <Spinner />
      <span style={s.loadingText}>Searching for "{query}"…</span>
    </div>
  );
  if (status === "error") return <p style={s.errText}>{error}</p>;

  return (
    <div style={s.searchResults}>
      {/* agent reasoning */}
      {results.rewritten_query && results.rewritten_query !== query && (
        <div style={s.agentBox}>
          <span style={s.agentLabel}>Agent rewrote →</span>
          <span style={s.agentQuery}>"{results.rewritten_query}"</span>
        </div>
      )}
      {results.extracted_tags?.length > 0 && (
        <div style={s.agentTags}>
          {results.extracted_tags.map(t => (
            <span key={t} style={s.agentTag}>{t}</span>
          ))}
        </div>
      )}

      <p style={s.resultCount}>
        {results.total} result{results.total !== 1 ? "s" : ""}
      </p>

      {results.total === 0 && (
        <p style={s.empty}>No videos found. Try uploading some first.</p>
      )}

      {results.results.map(v => (
        <div key={v.id} style={s.resultCard}>
          <div style={s.resultHead}>
            <span style={s.resultName}>{v.url}</span>
            <span style={{ ...s.pill, background: v.tagger === "gemini" ? "#ede9fe" : "#d1fae5", color: v.tagger === "gemini" ? "#7c3aed" : "#059669" }}>
              {v.tagger === "gemini" ? "Gemini" : "GPT-4o"}
            </span>
          </div>
          <video controls style={s.player} src={streamUrl(v.id)} />
          {v.description && <p style={s.desc}>{v.description}</p>}
          <div style={s.tags}>
            {v.tags?.map(t => {
              const hit = results.extracted_tags?.some(et => t.toLowerCase().includes(et.toLowerCase()));
              return <Tag key={t} label={t} highlight={hit} />;
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

function Tag({ label, highlight }) {
  return (
    <span style={{ ...s.tag, ...(highlight ? s.tagHit : {}) }}>{label}</span>
  );
}

function StatusPill({ status }) {
  const map = {
    processing: { bg: "#fef9c3", color: "#92400e", label: "Processing…" },
    ready:      { bg: "#d1fae5", color: "#065f46", label: "Ready" },
    failed:     { bg: "#fee2e2", color: "#991b1b", label: "Failed" },
    error:      { bg: "#fee2e2", color: "#991b1b", label: "Error" },
  };
  const { bg, color, label } = map[status] || map.processing;
  return <span style={{ ...s.pill, background: bg, color }}>{label}</span>;
}

function Spinner() {
  return <div style={s.spinner} />;
}

function Typing() {
  return (
    <div style={s.row}>
      <div style={s.avatar}>IW</div>
      <div style={{ ...s.bubble, ...s.bubbleSystem, ...s.typingBubble }}>
        <span style={s.dot} /><span style={{ ...s.dot, animationDelay: "0.2s" }} /><span style={{ ...s.dot, animationDelay: "0.4s" }} />
      </div>
    </div>
  );
}

const F = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";

const s = {
  shell: { display: "flex", flexDirection: "column", height: "100vh", background: "#f1f5f9", fontFamily: F },

  // header
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 24px", background: "#0f172a", borderBottom: "1px solid #1e293b", flexShrink: 0 },
  headerLeft: { display: "flex", alignItems: "center", gap: 12 },
  logoMark: { background: "#3b82f6", color: "#fff", fontWeight: 800, fontSize: 13, borderRadius: 8, padding: "6px 9px", letterSpacing: 0.5 },
  logoName: { color: "#f1f5f9", fontWeight: 700, fontSize: 15, lineHeight: 1.2 },
  logoSub: { color: "#475569", fontSize: 11, marginTop: 2 },
  headerRight: { display: "flex", gap: 6 },
  headerPill: { fontSize: 11, fontWeight: 600, padding: "3px 9px", borderRadius: 99, background: "#1e293b", color: "#94a3b8" },

  // feed
  feed: { flex: 1, overflowY: "auto", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 20 },
  row: { display: "flex", alignItems: "flex-start", gap: 10, maxWidth: 820 },
  rowUser: { flexDirection: "row-reverse", alignSelf: "flex-end" },
  avatar: { width: 30, height: 30, borderRadius: "50%", background: "#1e293b", color: "#64748b", fontSize: 10, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 2 },
  bubble: { maxWidth: 700 },
  bubbleSystem: {},
  bubbleUser: { background: "#2563eb", borderRadius: 16, padding: "10px 16px" },
  text: { margin: 0, fontSize: 14, color: "#334155", lineHeight: 1.6 },

  // cards
  card: { background: "#fff", borderRadius: 14, border: "1px solid #e2e8f0", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 12, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" },
  cardHead: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 },
  cardTitle: { display: "flex", alignItems: "center", gap: 8, fontWeight: 600, fontSize: 14, color: "#0f172a" },
  cardIcon: { fontSize: 16 },
  cardMeta: { display: "flex", gap: 6, flexShrink: 0 },
  pill: { fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 99 },

  // processing bar
  processingBar: { height: 3, background: "#e2e8f0", borderRadius: 99, overflow: "hidden" },
  processingFill: { height: "100%", width: "60%", background: "linear-gradient(90deg, #3b82f6, #8b5cf6)", borderRadius: 99, animation: "pulse 1.5s ease-in-out infinite" },

  // video
  player: { width: "100%", borderRadius: 10, background: "#0f172a", maxHeight: 300, objectFit: "contain" },

  // description + tags
  desc: { margin: 0, fontSize: 13, color: "#475569", lineHeight: 1.7 },
  tags: { display: "flex", flexWrap: "wrap", gap: 6 },
  tag: { background: "#f1f5f9", color: "#64748b", fontSize: 12, fontWeight: 500, padding: "3px 10px", borderRadius: 99 },
  tagHit: { background: "#dbeafe", color: "#1d4ed8" },
  errText: { margin: 0, fontSize: 13, color: "#dc2626" },

  // search
  searchResults: { display: "flex", flexDirection: "column", gap: 14, width: "100%" },
  agentBox: { display: "flex", alignItems: "baseline", gap: 6 },
  agentLabel: { fontSize: 11, fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: 0.5 },
  agentQuery: { fontSize: 13, color: "#6366f1", fontStyle: "italic" },
  agentTags: { display: "flex", flexWrap: "wrap", gap: 5 },
  agentTag: { background: "#ede9fe", color: "#7c3aed", fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 99 },
  resultCount: { margin: 0, fontSize: 12, color: "#94a3b8", fontWeight: 600 },
  resultCard: { background: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "14px 18px", display: "flex", flexDirection: "column", gap: 10, boxShadow: "0 1px 3px rgba(0,0,0,0.04)" },
  resultHead: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  resultName: { fontSize: 13, fontWeight: 600, color: "#0f172a" },
  empty: { fontSize: 14, color: "#94a3b8", margin: 0 },
  loadingRow: { display: "flex", alignItems: "center", gap: 10 },
  loadingText: { fontSize: 13, color: "#64748b" },

  // input bar
  bar: { background: "#fff", borderTop: "1px solid #e2e8f0", padding: "12px 24px", flexShrink: 0 },
  barInner: { display: "flex", alignItems: "center", gap: 10, maxWidth: 860, margin: "0 auto" },

  // pipeline toggle
  toggle: { display: "flex", borderRadius: 8, overflow: "hidden", border: "1px solid #e2e8f0", flexShrink: 0 },
  toggleBtn: { padding: "7px 13px", fontSize: 12, fontWeight: 700, border: "none", background: "#f8fafc", color: "#94a3b8", cursor: "pointer", borderColor: "transparent", transition: "all 0.15s" },

  // upload
  uploadBtn: { display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, fontSize: 13, fontWeight: 600, color: "#475569", cursor: "pointer", flexShrink: 0, whiteSpace: "nowrap" },

  // search form
  searchForm: { display: "flex", gap: 8, flex: 1 },
  searchInput: { flex: 1, padding: "9px 14px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 14, outline: "none", color: "#0f172a", background: "#f8fafc" },
  searchBtn: { padding: "9px 22px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer", flexShrink: 0 },
  searchBtnDim: { background: "#93c5fd", cursor: "not-allowed" },

  // typing
  typingBubble: { display: "flex", alignItems: "center", gap: 4, background: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, padding: "12px 16px" },
  dot: { width: 6, height: 6, borderRadius: "50%", background: "#94a3b8", display: "inline-block", animation: "pulse 1.2s ease-in-out infinite" },

  // spinner
  spinner: { width: 16, height: 16, borderRadius: "50%", border: "2.5px solid #e2e8f0", borderTopColor: "#3b82f6", animation: "spin 0.7s linear infinite", flexShrink: 0 },
};

"use client";

import { FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

function Icon({ name, size = 19 }: { name: string; size?: number }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };

  if (name === "plus") return <svg {...common}><path d="M12 5v14M5 12h14"/></svg>;
  if (name === "arrow") return <svg {...common}><path d="M12 19V5m-7 7 7-7 7 7"/></svg>;
  return <svg {...common}><circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/></svg>;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isLoading) return;

    const conversation = [...messages, { role: "user" as const, content: text }];
    setMessages(conversation);
    setDraft("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: "openrouter",
          version: "v3",
          messages: conversation,
          temperature: 0.7,
        }),
      });
      const result: { text?: string | null; error?: string } = await response.json();
      if (!response.ok) throw new Error(result.error || `Request failed (${response.status}).`);
      setMessages([...conversation, {
        role: "assistant",
        content: result.text?.trim() || "I couldn't generate a text response. Please try again.",
      }]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Something went wrong. Please try again.";
      setMessages([...conversation, { role: "assistant", content: `Sorry, I couldn't get a response. ${message}` }]);
    } finally {
      setIsLoading(false);
    }
  }

  function startNewChat() {
    if (isLoading) return;
    setMessages([]);
    setDraft("");
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-top">
          <a className="brand" href="#home" aria-label="Trustmebro home">
            <span className="brand-mark">✳</span>
            <span>Trustmebro</span>
          </a>
        </div>

        <button className="new-chat" onClick={startNewChat} disabled={isLoading}>
          <Icon name="plus" size={18} />
          <span>New chat</span>
          <span className="shortcut">⌘ K</span>
        </button>

      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="mobile-brand"><span className="brand-mark">✳</span><span>Trustmebro</span></div>
          <div className="model-name">Trustmebro</div>
        </header>

        <div className="conversation-area">
          {messages.length === 0 ? (
            <div className="welcome-state">
              <div className="welcome-mark">✳</div>
              <h1>Good afternoon, Ha</h1>
              <p>What would you like to explore?</p>
            </div>
          ) : (
            <div className="conversation">
              {messages.map((message, index) => (
                <article key={`${message.role}-${index}`} className={`message message-${message.role}`}>
                  {message.role === "assistant" ? (
                    <div className="assistant-mark">✳</div>
                  ) : (
                    <div className="user-avatar">H</div>
                  )}
                  <div className="message-body">
                    {message.role === "assistant" && <div className="message-label">Trustmebro</div>}
                    <p>{message.content}</p>
                  </div>
                </article>
              ))}
              {isLoading && (
                <div className="loading-section" role="status" aria-live="polite">
                  <span className="loading-mark" aria-hidden="true"><i /><i /><i /></span>
                  <span>Trustmebro is thinking…</span>
                </div>
              )}
            </div>
          )}

          <div className="composer-wrap">
            <form className="composer" onSubmit={submitMessage}>
              <textarea
                aria-label="Message Trustmebro"
                placeholder="Message Trustmebro..."
                value={draft}
                disabled={isLoading}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
                rows={2}
              />
              <div className="composer-toolbar">
                <span className="composer-model">Model: Trustmebro</span>
                <button type="submit" disabled={isLoading || !draft.trim()} className={`send-button ${draft.trim() && !isLoading ? "ready" : ""}`} aria-label="Send message"><Icon name="arrow" size={18} /></button>
              </div>
            </form>
            <div className="composer-note">Trustmebro can make mistakes. Please double-check responses.</div>
          </div>
        </div>
        <footer className="app-footer"><Icon name="info" size={15} /><span>Trustmebro is AI and can make mistakes. Please double-check responses.</span></footer>
      </section>
    </main>
  );
}

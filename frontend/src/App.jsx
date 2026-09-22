// 聊天页应用(提交 #2:消息流 + SSE 流式渲染)。
// #3 将接入:订单选择器 / 表单弹窗 / 会话侧栏 / 👍👎 反馈。
import React, { useCallback, useEffect, useRef, useState } from "react";
import Bubble from "./components/Bubble.jsx";
import ChatInput from "./components/ChatInput.jsx";
import CitePopover from "./components/CitePopover.jsx";
import EmptyState from "./components/EmptyState.jsx";
import { chatStream, readSSEStream, getConversationId } from "./api.js";

function Sidebar() {
  return (
    <aside className="app-sidebar glass">
      <div className="brand">
        <div className="logo">🐱</div>
        <div>
          <div className="name">喵喵优选</div>
          <div className="ci-preview">智能客服 · 小喵</div>
        </div>
      </div>
      <button className="new-chat" type="button" disabled>＋ 新对话</button>
      <div className="conv-list">
        <div className="sb-empty">会话列表接入中…</div>
      </div>
    </aside>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [cite, setCite] = useState(null); // { citation, anchorEl }
  const msgsRef = useRef(null);

  // 新消息/流式增量 → 滚到底
  useEffect(() => {
    const el = msgsRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const updateLastBot = useCallback((fn) => {
    setMessages((prev) => {
      const next = [...prev];
      for (let i = next.length - 1; i >= 0; i--) {
        if (next[i].role === "bot") {
          next[i] = fn(next[i]);
          break;
        }
      }
      return next;
    });
  }, []);

  const onCite = useCallback((anchorEl, citation) => {
    setCite({ citation, anchorEl });
  }, []);

  const send = useCallback(async (text) => {
    if (busy) return;
    setBusy(true);
    const id = String(Date.now());
    setMessages((prev) => [
      ...prev,
      { id: id + "-u", role: "user", text },
      { id: id + "-b", role: "bot", text: "", badges: [], citations: [], actions: [], streaming: true },
    ]);
    try {
      const resp = await chatStream(text, getConversationId());
      await readSSEStream(resp, {
        delta: (d) => updateLastBot((m) => ({ ...m, text: m.text + d })),
        tool: (name) => updateLastBot((m) => ({ ...m, badges: [...m.badges, name] })),
        citations: (items) => updateLastBot((m) => ({ ...m, citations: items })),
        actions: (items) => updateLastBot((m) => ({ ...m, actions: items })),
        interrupt: (data) => updateLastBot((m) => ({ ...m, interrupt: data })),
      });
    } catch (e) {
      updateLastBot((m) => ({ ...m, error: true, text: "回复失败，请稍后重试" }));
    } finally {
      updateLastBot((m) => ({ ...m, streaming: false }));
      setBusy(false);
    }
  }, [busy, updateLastBot]);

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="chat-main glass">
        <header className="chat-head">
          <div className="agent-name"><span className="dot" /> 客服小喵 · 在线</div>
          <span className="ci-preview">喵喵优选 · 智能客服</span>
        </header>
        <div className="msgs" ref={msgsRef}>
          {messages.length === 0 && <EmptyState busy={busy} onPick={send} />}
          {messages.map((m) => <Bubble key={m.id} msg={m} onCite={onCite} />)}
        </div>
        <ChatInput busy={busy} onSend={send} />
      </main>
      <CitePopover
        citation={cite?.citation || null}
        anchorEl={cite?.anchorEl || null}
        onClose={() => setCite(null)}
      />
    </div>
  );
}

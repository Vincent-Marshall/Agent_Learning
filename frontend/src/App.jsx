// 聊天页应用外壳(提交 #1:工程脚手架 + 设计规范落地)。
// 消息流、SSE 接入等核心逻辑在后续提交中实现。
import React from "react";

const SUGGESTIONS = [
  "七天无理由退货怎么算",
  "订单1001的物流到哪了",
  "会员权益有哪些",
  "退货运费谁出",
];

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
      <button className="new-chat" type="button">＋ 新对话</button>
      <div className="conv-list">
        <div className="sb-empty">会话列表接入中…</div>
      </div>
    </aside>
  );
}

function EmptyState() {
  return (
    <div className="empty">
      <div className="mascot">🐱</div>
      <h1>你好，我是小喵</h1>
      <p>喵喵优选的智能客服，商品、订单、售后都能问我～</p>
      <div className="chips">
        {SUGGESTIONS.map((s) => (
          <button key={s} className="chip" type="button">{s}</button>
        ))}
      </div>
    </div>
  );
}

function ChatInput() {
  return (
    <div className="chat-foot">
      <div className="input-bar">
        <textarea
          rows="1"
          placeholder="输入消息，和小喵聊聊吧～（回车发送 / Shift+回车换行）"
          disabled
        />
        <button className="send" type="button" disabled aria-label="发送">➤</button>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="chat-main glass">
        <header className="chat-head">
          <div className="agent-name"><span className="dot" /> 客服小喵 · 在线</div>
          <span className="ci-preview">喵喵优选 · 智能客服</span>
        </header>
        <EmptyState />
        <ChatInput />
      </main>
    </div>
  );
}

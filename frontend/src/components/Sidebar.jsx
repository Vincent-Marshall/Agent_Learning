// 会话侧栏:列表(active 高亮 + 已摘要徽标)/ 切换回载历史 / 新对话。
import React from "react";

export default function Sidebar({ convs, currentId, onSwitch, onNewChat }) {
  return (
    <aside className="app-sidebar glass">
      <div className="brand">
        <div className="logo">🐱</div>
        <div>
          <div className="name">喵喵优选</div>
          <div className="ci-preview">智能客服 · 小喵</div>
        </div>
      </div>
      <button className="new-chat" type="button" onClick={onNewChat}>＋ 新对话</button>
      <div className="conv-list">
        {!convs.length ? (
          <div className="sb-empty">还没有会话，发条消息开始吧～</div>
        ) : convs.map((it) => (
          <button
            key={it.id}
            type="button"
            className={"conv-item" + (it.id === currentId ? " active" : "")}
            onClick={() => onSwitch(it.id)}
          >
            <div className="ci-top">
              #{it.id}
              {it.has_summary && <span className="ci-sum">已摘要</span>}
            </div>
            <div className="ci-preview">{it.preview || ""}</div>
          </button>
        ))}
      </div>
    </aside>
  );
}

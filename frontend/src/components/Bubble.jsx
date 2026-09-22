// 消息气泡:用户(主色渐变,右) / 客服(浅灰,左,带头像)。
// 客服气泡内:工具徽章 + markdown 正文(含可点引用角标)+ 打字指示器 + children(动作/订单卡/反馈等)。
import React, { useLayoutEffect, useRef } from "react";
import { renderMarkdown, decorateCitations } from "../markdown.jsx";

export default function Bubble({ msg, onCite, children }) {
  const textRef = useRef(null);

  // 正文渲染完成后,把 [n] 替换成可点角标(幂等,StrictMode 双跑无害)
  useLayoutEffect(() => {
    if (!textRef.current || !msg.text) return;
    if (msg.citations && msg.citations.length) {
      decorateCitations(textRef.current, msg.citations, onCite);
    }
  }, [msg.text, msg.citations, onCite]);

  if (msg.role === "user") {
    return (
      <div className="row user">
        <div className="bubble user">{msg.text}</div>
      </div>
    );
  }

  return (
    <div className="row">
      <div className="avatar">🐱</div>
      <div className={`bubble bot${msg.error ? " error" : ""}`}>
        {msg.error ? (
          <div>{msg.text}</div>
        ) : (
          <>
            {(msg.badges?.length > 0) && (
              <div className="tool-badges">
                {msg.badges.map((name, i) => (
                  <span key={i} className="tool-badge">🔧 调用了 {name}</span>
                ))}
              </div>
            )}
            {msg.text ? (
              <div
                ref={textRef}
                className="bubble-text"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }}
              />
            ) : (
              !msg.interrupt && <span className="typing"><span /><span /><span /></span>
            )}
            {children}
          </>
        )}
      </div>
    </div>
  );
}

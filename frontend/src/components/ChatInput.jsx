// 输入栏:自动增高、回车发送、Shift+回车换行、发送中禁用。
import React, { useRef, useState } from "react";

export default function ChatInput({ busy, onSend }) {
  const [value, setValue] = useState("");
  const taRef = useRef(null);

  const autoGrow = () => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 128) + "px";
  };

  const submit = () => {
    const text = value.trim();
    if (!text || busy) return;
    setValue("");
    requestAnimationFrame(() => {
      if (taRef.current) taRef.current.style.height = "auto";
    });
    onSend(text);
  };

  return (
    <div className="chat-foot">
      <div className="input-bar">
        <textarea
          ref={taRef}
          rows="1"
          value={value}
          disabled={busy}
          placeholder="输入消息，和小喵聊聊吧～（回车发送 / Shift+回车换行）"
          onChange={(e) => { setValue(e.target.value); autoGrow(); }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button
          className="send"
          type="button"
          aria-label="发送"
          disabled={busy || !value.trim()}
          onClick={submit}
        >➤</button>
      </div>
    </div>
  );
}

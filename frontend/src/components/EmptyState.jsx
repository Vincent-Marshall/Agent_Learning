// 欢迎区:吉祥物 + 建议问题 chips(点击即发送)。
import React from "react";

const SUGGESTIONS = [
  "七天无理由退货怎么算",
  "订单1001的物流到哪了",
  "会员权益有哪些",
  "退货运费谁出",
];

export default function EmptyState({ busy, onPick }) {
  return (
    <div className="empty">
      <div className="mascot">🐱</div>
      <h1>你好，我是小喵</h1>
      <p>喵喵优选的智能客服，商品、订单、售后都能问我～</p>
      <div className="chips">
        {SUGGESTIONS.map((s) => (
          <button key={s} className="chip" type="button" disabled={busy} onClick={() => onPick(s)}>
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}

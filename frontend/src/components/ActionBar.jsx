// 动作按钮栏:转人工(前端模拟)/ 建工单(表单弹窗)/ 提交退款(表单弹窗)。
// 每种动作完成后该气泡内按钮置灰(doneActions 记录)。
import React from "react";

export default function ActionBar({ msg, onTransfer, onTicket, onRefund }) {
  const items = msg.actions || [];
  const done = new Set(msg.doneActions || []);
  if (!items.length) return null;

  return (
    <div className="action-bar">
      {items.map((a, i) => {
        if (a.type === "transfer_human") {
          return (
            <button key={i} type="button" className="action-btn ghost"
              disabled={done.has("transfer_human")}
              onClick={() => onTransfer(msg.id)}>转人工</button>
          );
        }
        if (a.type === "create_ticket") {
          return (
            <button key={i} type="button" className="action-btn"
              disabled={done.has("create_ticket")}
              onClick={() => onTicket(msg.id)}>建工单</button>
          );
        }
        if (a.type === "refund_form") {
          return (
            <button key={i} type="button" className="action-btn"
              disabled={done.has("refund_form")}
              onClick={() => onRefund(msg.id, a.draft || {})}>提交退款工单</button>
          );
        }
        return null;
      })}
    </div>
  );
}

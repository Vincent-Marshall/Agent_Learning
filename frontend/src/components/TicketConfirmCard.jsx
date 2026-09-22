// 工单预览确认卡:interrupt(kind=confirm_ticket)渲染。
// 确认提交 / 取消 → resume 续跑(值 {confirmed: bool}),卡面置灰防重复点。
import React, { useState } from "react";

export default function TicketConfirmCard({ preview, onConfirm }) {
  const [decided, setDecided] = useState(false);
  const choose = (confirmed) => {
    if (decided) return;
    setDecided(true);
    onConfirm(confirmed);
  };
  return (
    <div className={"ticket-confirm" + (decided ? " decided" : "")}>
      <div className="tc-title">📋 工单预览</div>
      <div className="tc-row"><span className="tc-label">工单类型</span><span>{preview?.ticket_type || "咨询"}</span></div>
      <div className="tc-row"><span className="tc-label">问题描述</span><span>{preview?.description || ""}</span></div>
      <div className="tc-btns">
        <button type="button" className="action-btn" disabled={decided} onClick={() => choose(true)}>确认提交</button>
        <button type="button" className="action-btn tc-cancel" disabled={decided} onClick={() => choose(false)}>取消</button>
      </div>
    </div>
  );
}
